import hmac
import hashlib
import time
import json
from django.conf import settings

def create_stripe_checkout_session(order, success_url, cancel_url):
    """
    Creates a Stripe Checkout Session for the given order.
    Uses official stripe python package if installed or requests HTTP client.
    """
    api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    if not api_key:
        raise ValueError("Stripe API Secret Key is not configured in settings or environment.")

    # Convert dollar amounts to cents for Stripe
    unit_amount = int(order.total_amount * 100)

    try:
        import stripe
        stripe.api_key = api_key
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"Royal Maltipoos Placement - Order #{order.order_number}",
                        'description': f"Companion Placement for {order.customer_name}",
                    },
                    'unit_amount': unit_amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            client_reference_id=order.order_number,
            customer_email=order.customer_email,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'order_number': order.order_number,
            }
        )
        return session.id, session.url
    except ImportError:
        # Fallback via direct HTTPS requests to Stripe API
        import requests
        data = {
            'mode': 'payment',
            'client_reference_id': order.order_number,
            'customer_email': order.customer_email,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'payment_method_types[0]': 'card',
            'line_items[0][price_data][currency]': 'usd',
            'line_items[0][price_data][product_data][name]': f"Royal Maltipoos Placement - Order #{order.order_number}",
            'line_items[0][price_data][unit_amount]': str(unit_amount),
            'line_items[0][quantity]': '1',
            'metadata[order_number]': order.order_number,
        }
        res = requests.post(
            'https://api.stripe.com/v1/checkout/sessions',
            headers={'Authorization': f'Bearer {api_key}'},
            data=data,
            timeout=15
        )
        if res.status_code == 200:
            res_data = res.json()
            return res_data['id'], res_data['url']
        else:
            raise RuntimeError(f"Stripe API Error: {res.text}")


def verify_stripe_webhook_signature(payload, sig_header, secret):
    """
    Verifies Stripe webhook signature using HMAC SHA-256 according to Stripe specifications.
    """
    if not sig_header or not secret:
        return False, "Missing signature header or webhook secret"

    # Header format: t=1492774577,v1=5257a869e7ecebeda32affa62cd496d...
    pairs = dict(item.split('=', 1) for item in sig_header.split(',') if '=' in item)
    timestamp = pairs.get('t')
    signatures = [v for k, v in [item.split('=', 1) for item in sig_header.split(',') if '=' in item] if k == 'v1']

    if not timestamp or not signatures:
        return False, "Malformed signature header"

    # Protect against replay attacks (5 minute tolerance)
    if abs(time.time() - int(timestamp)) > 300:
        return False, "Timestamp outside tolerance window"

    signed_payload = f"{timestamp}.{payload}".encode('utf-8')
    expected_sig = hmac.new(secret.encode('utf-8'), signed_payload, hashlib.sha256).hexdigest()

    for sig in signatures:
        if hmac.compare_digest(expected_sig, sig):
            return True, "Valid signature"

    return False, "Signature mismatch"
