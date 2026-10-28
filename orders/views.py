from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.conf import settings
from decimal import Decimal

from cart.models import Cart
from catalog.models import Pet
from orders.models import Order, OrderItem, OrderStatusHistory
from orders.forms import CheckoutForm
from accounts.models import CustomerAddress
from deliveries.models import Delivery, DeliveryEvent
from payments.models import Payment

def checkout_view(request):
    # Retrieve user's cart
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    elif request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()
        
    if not cart or cart.item_count == 0:
        messages.warning(request, "Your reservation cart is currently empty. Please select a puppy to proceed.")
        return redirect('catalog:pet_list')

    items = cart.items.select_related('pet', 'pet__breed', 'pet__category')

    # Initial form data pre-filling
    initial_data = {}
    if request.user.is_authenticated:
        initial_data['customer_name'] = request.user.get_full_name() or request.user.username
        initial_data['customer_email'] = request.user.email
        initial_data['customer_phone'] = getattr(request.user, 'phone_number', '')
        
        default_addr = CustomerAddress.objects.filter(user=request.user, is_default=True).first()
        if not default_addr:
            default_addr = CustomerAddress.objects.filter(user=request.user).first()
            
        if default_addr:
            initial_data['delivery_street_address'] = default_addr.street_address
            initial_data['delivery_apartment'] = default_addr.apartment_suite
            initial_data['delivery_city'] = default_addr.city
            initial_data['delivery_state'] = default_addr.state
            initial_data['delivery_postal_code'] = default_addr.postal_code
            initial_data['delivery_notes'] = default_addr.delivery_instructions

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Concurrency & Database Transaction Protection
            try:
                with transaction.atomic():
                    # Lock each pet row for update to prevent concurrent double-booking
                    pet_ids = [item.pet_id for item in items]
                    locked_pets = list(Pet.objects.select_for_update().filter(id__in=pet_ids))
                    
                    # Verify each pet is still strictly 'available'
                    unavailable = [p for p in locked_pets if p.status != 'available']
                    if unavailable:
                        names = ", ".join([p.name for p in unavailable])
                        messages.error(
                            request,
                            f"We deeply regret that {names} was just placed or reserved by another client during your checkout. Your cart has been updated."
                        )
                        return redirect('cart:view_cart')

                    # Create Order
                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.customer = request.user
                        
                    order.subtotal = cart.subtotal
                    order.delivery_fee = cart.delivery_fee
                    order.tax_amount = cart.tax_amount
                    order.total_amount = cart.total
                    order.order_status = 'pending_payment'
                    order.payment_status = 'pending'
                    order.save()

                    # Create OrderItems and mark pets as 'reserved'
                    for item in items:
                        OrderItem.objects.create(
                            order=order,
                            pet=item.pet,
                            price=item.pet.price,
                            pet_name=item.pet.name,
                            pet_breed_name=item.pet.breed.name,
                            pet_reference_number=item.pet.reference_number
                        )
                        # Mark pet reserved
                        item.pet.status = 'reserved'
                        item.pet.save(update_fields=['status'])

                    # Create initial OrderStatusHistory
                    OrderStatusHistory.objects.create(
                        order=order,
                        from_status='initiated',
                        to_status='pending_payment',
                        changed_by=request.user if request.user.is_authenticated else None,
                        notes='Order placed via secure checkout. Awaiting payment authorization.'
                    )

                    # Create associated Delivery record
                    delivery = Delivery.objects.create(
                        order=order,
                        origin_name=settings.NYC_ORIGIN_NAME,
                        origin_address=settings.BUSINESS_ADDRESS,
                        origin_latitude=settings.NYC_ORIGIN_LAT,
                        origin_longitude=settings.NYC_ORIGIN_LNG,
                        destination_name=order.customer_name,
                        destination_address=order.destination_display,
                        current_latitude=settings.NYC_ORIGIN_LAT,
                        current_longitude=settings.NYC_ORIGIN_LNG,
                        current_location_label='Manhattan Flagship Atelier, New York, NY',
                        status='scheduled',
                    )
                    DeliveryEvent.objects.create(
                        delivery=delivery,
                        status='scheduled',
                        title='Order Placed & Chaperoned Delivery Scheduled',
                        description=f"Destination: {order.destination_display}. Window: {order.preferred_delivery_window}.",
                        location_name='NYC Flagship Atelier'
                    )

                    # Clear the cart items
                    cart.items.all().delete()

            except Exception as e:
                messages.error(request, f"An error occurred while securing your reservation: {str(e)}")
                return redirect('cart:view_cart')

            # Route to Payment
            payment_choice = form.cleaned_data.get('payment_choice')
            if payment_choice == 'stripe' and settings.STRIPE_SECRET_KEY:
                return redirect('payments:stripe_checkout', order_number=order.order_number)
            else:
                return redirect('payments:simulate_payment', order_number=order.order_number)
        else:
            messages.error(request, "Please check the required fields in the checkout form.")
    else:
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
        'items': items,
        'stripe_configured': bool(settings.STRIPE_SECRET_KEY),
    }
    return render(request, 'orders/checkout.html', context)


def order_confirmation_view(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related('customer', 'delivery').prefetch_related('items', 'items__pet'),
        order_number=order_number
    )
    # Security: If order belongs to an authenticated user, only that user or staff can view
    if order.customer and request.user.is_authenticated and order.customer != request.user and not request.user.is_store_staff:
        messages.error(request, "You are not authorized to view this order confirmation.")
        return redirect('accounts:dashboard')
        
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def order_history_view(request):
    orders = Order.objects.filter(customer=request.user).select_related('delivery').prefetch_related('items').order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related('customer', 'delivery', 'delivery__assigned_agent').prefetch_related('items', 'items__pet', 'status_history'),
        order_number=order_number
    )
    if order.customer != request.user and not request.user.is_store_staff:
        messages.error(request, "Access restricted to authorized account owner.")
        return redirect('accounts:dashboard')
        
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def download_receipt_view(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related('customer', 'delivery').prefetch_related('items'),
        order_number=order_number
    )
    if order.customer != request.user and not request.user.is_store_staff:
        messages.error(request, "Access restricted.")
        return redirect('accounts:dashboard')
        
    return render(request, 'orders/order_receipt_print.html', {'order': order})
