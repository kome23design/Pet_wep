from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.db import transaction

from orders.models import Order, OrderStatusHistory
from payments.models import Payment
from catalog.models import Pet
from payments.stripe_client import create_stripe_checkout_session, verify_stripe_webhook_signature
import json

def stripe_checkout_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    
    if not settings.STRIPE_SECRET_KEY:
        messages.info(request, "Stripe API keys are not configured. Switched automatically to the Development Payment Simulator.")
        return redirect('payments:simulate_payment', order_number=order.order_number)

    success_url = request.build_absolute_uri(reverse('payments:payment_return', kwargs={'order_number': order.order_number}))
    cancel_url = request.build_absolute_uri(reverse('payments:payment_cancel', kwargs={'order_number': order.order_number}))

    try:
        session_id, session_url = create_stripe_checkout_session(order, success_url, cancel_url)
        order.stripe_session_id = session_id
        order.save(update_fields=['stripe_session_id'])
        return redirect(session_url)
    except Exception as e:
        messages.error(request, f"Unable to initialize Stripe payment session: {str(e)}. You may use the development payment simulator below.")
        return redirect('payments:simulate_payment', order_number=order.order_number)


def simulate_payment_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    
    # If already paid
    if order.payment_status == 'paid':
        return redirect('orders:order_confirmation', order_number=order.order_number)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'success':
            with transaction.atomic():
                order.payment_status = 'paid'
                order.order_status = 'confirmed'
                order.payment_reference = f"SIM-PAY-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                order.save()

                Payment.objects.update_or_create(
                    order=order,
                    defaults={
                        'amount': order.total_amount,
                        'payment_method': order.payment_method or 'simulator',
                        'status': 'successful',
                        'stripe_payment_intent_id': order.payment_reference,
                        'raw_response_notes': f'Authorized via {order.get_payment_method_display()} - Prestige Paws Placement Atelier'
                    }
                )

                # Update pets to sold
                for item in order.items.all():
                    item.pet.status = 'sold'
                    item.pet.save(update_fields=['status'])

                OrderStatusHistory.objects.create(
                    order=order,
                    from_status='pending_payment',
                    to_status='confirmed',
                    notes='Payment authorized via Development Simulator sandbox. Order confirmed for chaperoned delivery.'
                )

            messages.success(request, f"Payment simulation successful! Order #{order.order_number} is confirmed.")
            return redirect('orders:order_confirmation', order_number=order.order_number)

        elif action == 'fail':
            order.payment_status = 'failed'
            order.save(update_fields=['payment_status'])
            
            Payment.objects.update_or_create(
                order=order,
                defaults={
                    'amount': order.total_amount,
                    'payment_method': 'simulator',
                    'status': 'failed',
                    'raw_response_notes': 'Simulated Card Decline: Insufficient Funds / Bank Verification Failed'
                }
            )
            messages.error(request, "Simulated payment failure: Your financial institution declined the test transaction.")
            return redirect('payments:simulate_payment', order_number=order.order_number)

        elif action == 'cancel':
            # Cancel order and restore inventory
            with transaction.atomic():
                order.order_status = 'cancelled'
                order.payment_status = 'failed'
                order.save()
                for item in order.items.all():
                    item.pet.status = 'available'
                    item.pet.save(update_fields=['status'])
                OrderStatusHistory.objects.create(
                    order=order,
                    from_status='pending_payment',
                    to_status='cancelled',
                    notes='Checkout cancelled by customer. Reserved pet inventory restored to available.'
                )
            messages.info(request, f"Order #{order.order_number} cancelled. Your reservation has been released.")
            return redirect('catalog:pet_list')

    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'payments/payment_simulator.html', context)


@csrf_exempt
def stripe_webhook_view(request):
    """
    Secure, idempotent Stripe Webhook Endpoint with HMAC signature verification.
    """
    payload = request.body.decode('utf-8')
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    if secret:
        valid, msg = verify_stripe_webhook_signature(payload, sig_header, secret)
        if not valid:
            return HttpResponse(status=400, content=f"Signature verification failed: {msg}")

    try:
        event = json.loads(payload)
    except Exception:
        return HttpResponse(status=400, content="Invalid JSON payload")

    event_type = event.get('type')
    event_data = event.get('data', {}).get('object', {})

    if event_type == 'checkout.session.completed':
        order_number = event_data.get('client_reference_id') or event_data.get('metadata', {}).get('order_number')
        session_id = event_data.get('id')
        payment_intent_id = event_data.get('payment_intent')
        amount_total = Decimal(str(event_data.get('amount_total', 0))) / 100

        if order_number:
            try:
                with transaction.atomic():
                    order = Order.objects.select_for_update().get(order_number=order_number)
                    if order.payment_status != 'paid':
                        order.payment_status = 'paid'
                        order.order_status = 'confirmed'
                        order.payment_reference = payment_intent_id or session_id
                        order.save()

                        Payment.objects.update_or_create(
                            order=order,
                            defaults={
                                'amount': amount_total,
                                'payment_method': 'stripe_checkout',
                                'status': 'successful',
                                'stripe_session_id': session_id,
                                'stripe_payment_intent_id': payment_intent_id or '',
                                'raw_response_notes': f"Stripe webhook processed event {event.get('id')}"
                            }
                        )

                        for item in order.items.all():
                            item.pet.status = 'sold'
                            item.pet.save(update_fields=['status'])

                        OrderStatusHistory.objects.create(
                            order=order,
                            from_status='pending_payment',
                            to_status='confirmed',
                            notes=f'Stripe payment verified via webhook. PaymentIntent: {payment_intent_id}'
                        )
            except Order.DoesNotExist:
                pass

    return JsonResponse({'status': 'success'})


def payment_return_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'payments/payment_return.html', {'order': order})


def payment_cancel_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    # Restore pet inventory
    with transaction.atomic():
        order.order_status = 'cancelled'
        order.save(update_fields=['order_status'])
        for item in order.items.all():
            item.pet.status = 'available'
            item.pet.save(update_fields=['status'])
        OrderStatusHistory.objects.create(
            order=order,
            from_status='pending_payment',
            to_status='cancelled',
            notes='Stripe checkout session cancelled by client. Pet availability restored.'
        )
    messages.info(request, "Checkout process was cancelled. Your selected puppy is available in our catalog.")
    return redirect('catalog:pet_list')
