from django.db import models
from orders.models import Order
from decimal import Decimal

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Verification'),
        ('successful', 'Successful & Settled'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Refunded'),
    )

    METHOD_CHOICES = (
        ('stripe_checkout', 'Stripe Hosted Secure Checkout'),
        ('stripe_card', 'Stripe Credit/Debit Card'),
        ('simulator', 'Development Payment Simulator (Test Sandbox)'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='usd')
    payment_method = models.CharField(max_length=30, choices=METHOD_CHOICES, default='stripe_checkout')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    stripe_session_id = models.CharField(max_length=150, blank=True, default='')
    stripe_payment_intent_id = models.CharField(max_length=150, blank=True, default='')
    stripe_charge_id = models.CharField(max_length=150, blank=True, default='')
    
    idempotency_key = models.CharField(max_length=100, blank=True, default='')
    raw_response_notes = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.id} for Order {self.order.order_number} - ${self.amount} [{self.get_status_display()}]"
