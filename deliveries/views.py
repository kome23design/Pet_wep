from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from deliveries.models import Delivery, DeliveryLocation, DeliveryEvent
from orders.models import Order, OrderStatusHistory

def live_tracking_view(request, tracking_number):
    delivery = get_object_or_404(
        Delivery.objects.select_related('order', 'order__customer', 'assigned_agent', 'assigned_agent__delivery_profile').prefetch_related('events', 'location_history', 'order__items', 'order__items__pet'),
        tracking_number=tracking_number
    )
    
    # Authorization: Customer must own the order or be staff/courier
    order = delivery.order
    if order.customer:
        if not request.user.is_authenticated:
            # Check session or redirect to login
            messages.info(request, "Please log in to view protected live companion delivery telemetry.")
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
            
        if order.customer != request.user and not request.user.is_store_staff and request.user != delivery.assigned_agent:
            messages.error(request, "You are not authorized to view this private delivery tracking stream.")
            return redirect('accounts:dashboard')

    events = delivery.events.all().order_by('-event_time')
    breadcrumbs = delivery.location_history.all().order_by('recorded_at')
    
    # Coordinate trail for Leaflet polyline
    route_coords = [[loc.latitude, loc.longitude] for loc in breadcrumbs]
    if delivery.has_active_coordinates and [delivery.current_latitude, delivery.current_longitude] not in route_coords:
        route_coords.append([delivery.current_latitude, delivery.current_longitude])

    context = {
        'delivery': delivery,
        'order': order,
        'events': events,
        'breadcrumbs': breadcrumbs,
        'route_coords_json': route_coords,
        'is_courier_viewer': request.user.is_authenticated and (request.user == delivery.assigned_agent or request.user.is_store_staff),
    }
    return render(request, 'deliveries/live_tracking.html', context)


def delivery_telemetry_api(request, tracking_number):
    """
    Real-time JSON Telemetry endpoint for Leaflet.js live polling.
    """
    delivery = get_object_or_404(
        Delivery.objects.select_related('order', 'order__customer'),
        tracking_number=tracking_number
    )
    
    # Auth check
    if delivery.order.customer:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if delivery.order.customer != request.user and not request.user.is_store_staff and request.user != delivery.assigned_agent:
            return JsonResponse({'error': 'Forbidden'}, status=403)

    breadcrumbs = list(
        delivery.location_history.order_by('recorded_at').values('latitude', 'longitude', 'recorded_at', 'notes')
    )
    
    events = [
        {
            'status': e.status,
            'title': e.title,
            'description': e.description,
            'location': e.location_name,
            'time': e.event_time.strftime('%I:%M %p, %b %d'),
        }
        for e in delivery.events.order_by('-event_time')
    ]

    data = {
        'tracking_number': delivery.tracking_number,
        'status': delivery.status,
        'status_display': delivery.get_status_display(),
        'carrier_type_display': delivery.get_carrier_type_display(),
        'origin': {
            'name': delivery.origin_name,
            'lat': delivery.origin_latitude,
            'lng': delivery.origin_longitude,
        },
        'destination': {
            'name': delivery.destination_name,
            'address': delivery.destination_address,
            'lat': delivery.destination_latitude,
            'lng': delivery.destination_longitude,
        },
        'current_location': {
            'lat': delivery.current_latitude,
            'lng': delivery.current_longitude,
            'label': delivery.current_location_label,
            'last_update': delivery.last_location_update.strftime('%I:%M:%S %p') if delivery.last_location_update else None,
            'is_live': delivery.is_live_tracking_active,
        },
        'breadcrumbs': [
            {'lat': b['latitude'], 'lng': b['longitude'], 'time': b['recorded_at'].strftime('%H:%M:%S'), 'notes': b['notes']}
            for b in breadcrumbs
        ],
        'events': events,
    }
    return JsonResponse(data)


@login_required
def courier_portal_view(request):
    """
    Dedicated dashboard for authorized couriers to view assigned deliveries and push GPS updates.
    """
    if not (request.user.is_delivery_agent or request.user.is_store_staff):
        messages.error(request, "Courier portal restricted to certified delivery staff.")
        return redirect('accounts:dashboard')
        
    deliveries = Delivery.objects.filter(assigned_agent=request.user).order_by('-created_at')
    if request.user.is_store_staff and not deliveries.exists():
        deliveries = Delivery.objects.all().order_by('-created_at')[:10]

    return render(request, 'deliveries/courier_portal.html', {'deliveries': deliveries})


@login_required
@require_POST
def update_delivery_location_api(request, tracking_number):
    """
    Protected endpoint for authorized delivery agents to broadcast GPS or manual telemetry.
    """
    delivery = get_object_or_404(Delivery, tracking_number=tracking_number)
    
    # Verification: Only assigned courier or store staff can update
    if request.user != delivery.assigned_agent and not request.user.is_store_staff:
        return HttpResponseForbidden("Unauthorized courier credentials.")

    try:
        lat = float(request.POST.get('latitude'))
        lng = float(request.POST.get('longitude'))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid latitude or longitude format.'}, status=400)

    # Coordinate validation
    if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lng <= 180.0):
        return JsonResponse({'success': False, 'error': 'GPS coordinates outside valid planetary range.'}, status=400)

    label = request.POST.get('location_label', '').strip() or f"En Route ({lat:.4f}, {lng:.4f})"
    status = request.POST.get('status')
    notes = request.POST.get('notes', '').strip()

    # Save to telemetry history
    DeliveryLocation.objects.create(
        delivery=delivery,
        latitude=lat,
        longitude=lng,
        source='gps' if request.POST.get('source') == 'device_gps' else 'agent_portal',
        notes=notes or label
    )

    # Update delivery current location
    delivery.current_latitude = lat
    delivery.current_longitude = lng
    delivery.current_location_label = label
    delivery.last_location_update = timezone.now()
    delivery.is_live_tracking_active = True

    if status and status in dict(Delivery.STATUS_CHOICES) and status != delivery.status:
        old_status = delivery.status
        delivery.status = status
        
        # Sync with order status
        if status == 'delivered':
            delivery.order.order_status = 'delivered'
            delivery.order.save(update_fields=['order_status'])
            delivery.actual_delivery_time = timezone.now()
        elif status == 'in_transit':
            delivery.order.order_status = 'in_transit'
            delivery.order.save(update_fields=['order_status'])
        elif status == 'out_for_delivery':
            delivery.order.order_status = 'out_for_delivery'
            delivery.order.save(update_fields=['order_status'])

        # Add event milestone
        DeliveryEvent.objects.create(
            delivery=delivery,
            status=status,
            title=f"Status Updated: {delivery.get_status_display()}",
            description=notes or f"Updated by courier {request.user.get_full_name() or request.user.username}",
            location_name=label,
            recorded_by=request.user
        )

        OrderStatusHistory.objects.create(
            order=delivery.order,
            from_status=old_status,
            to_status=status,
            changed_by=request.user,
            notes=f"Courier updated delivery status to {delivery.get_status_display()} at {label}"
        )

    delivery.save()

    return JsonResponse({
        'success': True,
        'message': 'Telemetry position recorded successfully.',
        'lat': delivery.current_latitude,
        'lng': delivery.current_longitude,
        'status': delivery.status,
        'last_update': delivery.last_location_update.strftime('%I:%M:%S %p'),
    })
