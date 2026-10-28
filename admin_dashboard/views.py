from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal

from catalog.models import Pet, PetBreed, PetCategory, PetImage, HealthDocument
from orders.models import Order, OrderStatusHistory
from deliveries.models import Delivery, DeliveryEvent
from reviews.models import Review, ReviewModerationHistory
from pages.models import ContactInquiry, NewsletterSubscriber
from accounts.models import User

def staff_required(user):
    return user.is_authenticated and (user.is_store_staff or user.is_superuser)

@user_passes_test(staff_required, login_url='accounts:login')
def dashboard_overview(request):
    # Statistics calculations
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status='pending_payment').count()
    confirmed_orders = Order.objects.filter(order_status='confirmed').count()
    active_deliveries = Delivery.objects.filter(status__in=['scheduled', 'preparing', 'picked_up', 'in_transit', 'out_for_delivery']).count()
    delivered_orders = Order.objects.filter(order_status='delivered').count()
    
    # Revenue from paid orders only
    revenue_agg = Order.objects.filter(payment_status='paid').aggregate(total_revenue=Sum('total_amount'))
    total_revenue = revenue_agg['total_revenue'] or Decimal('0.00')

    # Inventory statistics
    available_pets = Pet.objects.filter(status='available').count()
    reserved_pets = Pet.objects.filter(status='reserved').count()
    sold_pets = Pet.objects.filter(status='sold').count()

    # Moderation & Inquiries
    pending_reviews_count = Review.objects.filter(status='pending').count()
    unresolved_inquiries = ContactInquiry.objects.filter(is_resolved=False).count()

    # Recent activity
    recent_orders = Order.objects.select_related('customer', 'delivery').prefetch_related('items').order_by('-created_at')[:6]
    recent_deliveries = Delivery.objects.select_related('order', 'assigned_agent').order_by('-last_location_update')[:5]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'active_deliveries': active_deliveries,
        'delivered_orders': delivered_orders,
        'total_revenue': total_revenue,
        'available_pets': available_pets,
        'reserved_pets': reserved_pets,
        'sold_pets': sold_pets,
        'pending_reviews_count': pending_reviews_count,
        'unresolved_inquiries': unresolved_inquiries,
        'recent_orders': recent_orders,
        'recent_deliveries': recent_deliveries,
    }
    return render(request, 'admin_dashboard/overview.html', context)


@user_passes_test(staff_required, login_url='accounts:login')
def inventory_list(request):
    pets = Pet.objects.select_related('category', 'breed').prefetch_related('images').order_by('-created_at')
    categories = PetCategory.objects.all().prefetch_related('breeds')
    
    status_filter = request.GET.get('status')
    if status_filter:
        pets = pets.filter(status=status_filter)
        
    return render(request, 'admin_dashboard/inventory_list.html', {
        'pets': pets,
        'categories': categories,
        'current_status': status_filter
    })


@user_passes_test(staff_required, login_url='accounts:login')
def add_pet_view(request):
    categories = PetCategory.objects.filter(is_active=True)
    breeds = PetBreed.objects.filter(is_active=True)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        ref = request.POST.get('reference_number')
        category_id = request.POST.get('category')
        breed_id = request.POST.get('breed')
        price = request.POST.get('price')
        dob = request.POST.get('date_of_birth')
        sex = request.POST.get('sex')
        coat = request.POST.get('coat_color')
        desc = request.POST.get('description')
        status = request.POST.get('status', 'available')
        image_url = request.POST.get('image_url')

        if name and ref and category_id and breed_id and price and dob:
            pet = Pet.objects.create(
                name=name,
                reference_number=ref,
                category_id=category_id,
                breed_id=breed_id,
                price=Decimal(price),
                date_of_birth=dob,
                sex=sex,
                coat_color=coat,
                description=desc,
                status=status,
                is_published=True,
                is_featured=bool(request.POST.get('is_featured'))
            )
            if image_url:
                PetImage.objects.create(pet=pet, image_url=image_url, is_primary=True)
            messages.success(request, f"Pet listing {name} ({ref}) created successfully.")
            return redirect('admin_dashboard:inventory')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'admin_dashboard/pet_form.html', {'categories': categories, 'breeds': breeds})


@user_passes_test(staff_required, login_url='accounts:login')
def add_category_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        desc = request.POST.get('description', '').strip()
        if name:
            cat = PetCategory.objects.create(name=name, description=desc, is_active=True)
            messages.success(request, f"New dynamic pet category '{cat.name}' created.")
            return redirect('admin_dashboard:inventory')
    return render(request, 'admin_dashboard/category_form.html')


@user_passes_test(staff_required, login_url='accounts:login')
def add_breed_view(request):
    categories = PetCategory.objects.filter(is_active=True)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        cat_id = request.POST.get('category')
        desc = request.POST.get('description', '').strip()
        temperament = request.POST.get('temperament', '').strip()
        if name and cat_id:
            breed = PetBreed.objects.create(
                name=name,
                category_id=cat_id,
                description=desc,
                temperament=temperament,
                is_active=True
            )
            messages.success(request, f"New breed '{breed.name}' created under {breed.category.name}.")
            return redirect('admin_dashboard:inventory')
    return render(request, 'admin_dashboard/breed_form.html', {'categories': categories})


@user_passes_test(staff_required, login_url='accounts:login')
def orders_management(request):
    orders = Order.objects.select_related('customer', 'delivery').prefetch_related('items').order_by('-created_at')
    
    q = request.GET.get('q')
    if q:
        orders = orders.filter(
            Q(order_number__icontains=q) |
            Q(customer_name__icontains=q) |
            Q(customer_email__icontains=q)
        )
        
    status = request.GET.get('status')
    if status:
        orders = orders.filter(order_status=status)
        
    return render(request, 'admin_dashboard/orders_list.html', {
        'orders': orders,
        'current_status': status,
        'search_query': q,
    })


@user_passes_test(staff_required, login_url='accounts:login')
def order_detail_admin(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related('customer', 'delivery', 'delivery__assigned_agent').prefetch_related('items', 'items__pet', 'status_history'),
        order_number=order_number
    )
    couriers = User.objects.filter(role='delivery_agent')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('order_status')
            if new_status and new_status != order.order_status:
                old_status = order.order_status
                order.order_status = new_status
                order.save()
                
                # Sync delivery status if relevant
                if hasattr(order, 'delivery'):
                    if new_status in ('dispatched', 'in_transit'):
                        order.delivery.status = 'in_transit'
                        order.delivery.is_live_tracking_active = True
                        order.delivery.save()
                    elif new_status == 'delivered':
                        order.delivery.status = 'delivered'
                        order.delivery.actual_delivery_time = timezone.now()
                        order.delivery.save()
                        
                OrderStatusHistory.objects.create(
                    order=order,
                    from_status=old_status,
                    to_status=new_status,
                    changed_by=request.user,
                    notes=request.POST.get('notes', 'Updated via executive portal')
                )
                messages.success(request, f"Order status updated to {order.get_order_status_display()}.")

        elif action == 'assign_courier':
            courier_id = request.POST.get('courier_id')
            if courier_id and hasattr(order, 'delivery'):
                courier = get_object_or_404(User, id=courier_id)
                order.delivery.assigned_agent = courier
                order.delivery.save()
                messages.success(request, f"Courier {courier.get_full_name() or courier.username} assigned to delivery.")

        return redirect('admin_dashboard:order_detail', order_number=order.order_number)

    return render(request, 'admin_dashboard/order_detail.html', {
        'order': order,
        'couriers': couriers,
    })


@user_passes_test(staff_required, login_url='accounts:login')
def review_moderation_queue(request):
    pending_reviews = Review.objects.filter(status='pending').select_related('customer', 'pet', 'breed').order_by('-created_at')
    recent_moderated = Review.objects.exclude(status='pending').select_related('customer', 'moderated_by').order_by('-moderated_at')[:10]

    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        decision = request.POST.get('decision')  # 'approve' or 'reject'
        admin_notes = request.POST.get('admin_notes', '')

        review = get_object_or_404(Review, id=review_id)
        if decision == 'approve':
            review.status = 'approved'
            review.moderated_by = request.user
            review.moderated_at = timezone.now()
            review.admin_notes = admin_notes
            review.save()
            ReviewModerationHistory.objects.create(
                review=review,
                action='Approved for public wall',
                moderator=request.user,
                notes=admin_notes
            )
            messages.success(request, f"Review #{review.id} approved and published.")
        elif decision == 'reject':
            review.status = 'rejected'
            review.moderated_by = request.user
            review.moderated_at = timezone.now()
            review.admin_notes = admin_notes
            review.save()
            ReviewModerationHistory.objects.create(
                review=review,
                action='Rejected / Inappropriate',
                moderator=request.user,
                notes=admin_notes
            )
            messages.warning(request, f"Review #{review.id} rejected.")

        return redirect('admin_dashboard:review_moderation')

    return render(request, 'admin_dashboard/review_queue.html', {
        'pending_reviews': pending_reviews,
        'recent_moderated': recent_moderated,
    })


@user_passes_test(staff_required, login_url='accounts:login')
def delivery_dispatch_console(request):
    deliveries = Delivery.objects.select_related('order', 'assigned_agent').prefetch_related('events').order_by('-created_at')
    active_deliveries = deliveries.filter(status__in=['scheduled', 'preparing', 'picked_up', 'in_transit', 'out_for_delivery'])
    couriers = User.objects.filter(role='delivery_agent')

    return render(request, 'admin_dashboard/delivery_dispatch.html', {
        'deliveries': deliveries,
        'active_deliveries': active_deliveries,
        'couriers': couriers,
    })
