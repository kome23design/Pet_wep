from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.urls import reverse
from django.conf import settings
from decimal import Decimal

from cart.models import Cart
from catalog.models import Pet
from orders.models import Order, OrderItem, OrderStatusHistory, Coupon
from orders.forms import CheckoutForm
from accounts.models import User, CustomerAddress
from deliveries.models import Delivery, DeliveryEvent
from payments.models import Payment

def validate_coupon_api(request):
    """
    JSON API for instant coupon validation at checkout.
    """
    code = request.GET.get('code', '').strip()
    if not code:
        return JsonResponse({'valid': False, 'message': 'Please enter a coupon code.'})

    coupon = Coupon.objects.filter(code__iexact=code).first()
    if not coupon:
        return JsonResponse({'valid': False, 'message': 'Invalid coupon code. Please verify spelling.'})

    # Get cart subtotal
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    elif request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    subtotal = cart.subtotal if cart else Decimal('0.00')
    is_valid, reason = coupon.is_valid(subtotal)
    if not is_valid:
        return JsonResponse({'valid': False, 'message': reason})

    discount = coupon.calculate_discount(subtotal)
    delivery_fee = cart.delivery_fee if cart else Decimal('250.00')
    tax_amount = cart.tax_amount if cart else Decimal('0.00')
    new_total = max(Decimal('0.00'), subtotal - discount + delivery_fee + tax_amount)

    return JsonResponse({
        'valid': True,
        'code': coupon.code,
        'discount_amount': float(discount),
        'discount_display': f"${discount:,.2f}",
        'new_total_display': f"${new_total:,.2f}",
        'message': f"Promotional code {coupon.code} applied successfully ({coupon.get_discount_type_display()})!"
    })

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
                    
                    # Account handling (Guest vs Authenticated vs Optional Account Creation)
                    if request.user.is_authenticated:
                        order.customer = request.user
                    elif form.cleaned_data.get('create_account') and form.cleaned_data.get('account_password'):
                        email = form.cleaned_data.get('customer_email')
                        raw_pwd = form.cleaned_data.get('account_password')
                        name_parts = form.cleaned_data.get('customer_name', '').split(' ', 1)
                        first_name = name_parts[0]
                        last_name = name_parts[1] if len(name_parts) > 1 else ''
                        
                        # Generate unique username from email
                        username_base = email.split('@')[0]
                        username = username_base
                        counter = 1
                        while User.objects.filter(username=username).exists():
                            username = f"{username_base}{counter}"
                            counter += 1

                        if not User.objects.filter(email=email).exists():
                            new_user = User.objects.create_user(
                                username=username,
                                email=email,
                                password=raw_pwd,
                                first_name=first_name,
                                last_name=last_name,
                                role='customer'
                            )
                            auth_login(request, new_user)
                            order.customer = new_user
                            messages.success(request, f"Welcome to Prestige Paws NYC! Your private client account '{username}' has been created.")
                    else:
                        order.customer = None  # Explicit Guest Order!

                    # Coupon & Discount Handling
                    order.subtotal = cart.subtotal
                    order.delivery_fee = cart.delivery_fee
                    order.tax_amount = cart.tax_amount
                    
                    coupon_code = form.cleaned_data.get('coupon_code', '').strip()
                    discount = Decimal('0.00')
                    if coupon_code:
                        coupon = Coupon.objects.filter(code__iexact=coupon_code, is_active=True).first()
                        if coupon:
                            is_valid, _ = coupon.is_valid(cart.subtotal)
                            if is_valid:
                                discount = coupon.calculate_discount(cart.subtotal)
                                order.coupon = coupon
                                order.discount_amount = discount
                                coupon.times_used += 1
                                coupon.save(update_fields=['times_used'])

                    order.total_amount = max(Decimal('0.00'), cart.subtotal - discount + cart.delivery_fee + cart.tax_amount)
                    
                    # Payment Method & Status
                    payment_choice = form.cleaned_data.get('payment_choice', 'paypal')
                    order.payment_method = payment_choice
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
                        notes=f'Order placed via secure checkout ({order.get_payment_method_display()}). Admin will contact client with full payment details.'
                    )

                    # Create pending Payment record for admin tracking
                    Payment.objects.update_or_create(
                        order=order,
                        defaults={
                            'amount': order.total_amount,
                            'payment_method': order.payment_method or 'paypal',
                            'status': 'pending',
                            'raw_response_notes': f'Awaiting admin payment instructions for {order.get_payment_method_display()}.'
                        }
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

            messages.success(
                request,
                f"Order #{order.order_number} confirmed! Our admin will contact you shortly with the full payment details with respect to your chosen payment method ({order.get_payment_method_display()})."
            )

            # Route to Order Confirmation (or Stripe if configured)
            if payment_choice == 'card' and settings.STRIPE_SECRET_KEY:
                return redirect('payments:stripe_checkout', order_number=order.order_number)
            else:
                return redirect('orders:order_confirmation', order_number=order.order_number)
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


def order_detail_view(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related('customer', 'delivery', 'delivery__assigned_agent').prefetch_related('items', 'items__pet', 'status_history'),
        order_number=order_number
    )
    if order.customer and (not request.user.is_authenticated or (order.customer != request.user and not request.user.is_store_staff)):
        messages.error(request, "Access restricted to authorized account owner.")
        return redirect('accounts:dashboard')
        
    return render(request, 'orders/order_detail.html', {'order': order})


def download_receipt_view(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related('customer', 'delivery').prefetch_related('items'),
        order_number=order_number
    )
    if order.customer and (not request.user.is_authenticated or (order.customer != request.user and not request.user.is_store_staff)):
        messages.error(request, "Access restricted.")
        return redirect('accounts:dashboard')
        
    return render(request, 'orders/order_receipt_print.html', {'order': order})
