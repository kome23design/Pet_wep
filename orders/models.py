from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid
import datetime

class Order(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('processing', 'Payment Processing'),
        ('paid', 'Paid & Verified'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Refunded'),
    )

    ORDER_STATUS_CHOICES = (
        ('pending_payment', 'Pending Payment'),
        ('payment_processing', 'Payment Processing'),
        ('confirmed', 'Order Confirmed & Health Vetted'),
        ('preparing', 'Preparing for Chaperoned Travel'),
        ('dispatched', 'Dispatched from Manhattan Atelier'),
        ('in_transit', 'In Transit with Certified Courier'),
        ('out_for_delivery', 'Out for Final Hand-Delivery'),
        ('delivered', 'Safely Hand-Delivered'),
        ('cancelled', 'Cancelled & Inventory Restored'),
        ('refunded', 'Cancelled & Fully Refunded'),
    )

    order_number = models.CharField(max_length=40, unique=True, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Recipient details
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    
    # Delivery destination snapshot
    delivery_street_address = models.CharField(max_length=255)
    delivery_apartment = models.CharField(max_length=50, blank=True, default='')
    delivery_city = models.CharField(max_length=100)
    delivery_state = models.CharField(max_length=50)
    delivery_postal_code = models.CharField(max_length=20)
    delivery_country = models.CharField(max_length=50, default='United States')
    delivery_notes = models.TextField(blank=True, default='')
    preferred_delivery_date = models.DateField(null=True, blank=True)
    preferred_delivery_window = models.CharField(max_length=100, blank=True, default='Morning (9:00 AM - 1:00 PM EST)')
    
    # Financial snapshot
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('250.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Statuses
    payment_status = models.CharField(max_length=25, choices=PAYMENT_STATUS_CHOICES, default='pending')
    order_status = models.CharField(max_length=25, choices=ORDER_STATUS_CHOICES, default='pending_payment')
    
    # References & Notes
    payment_reference = models.CharField(max_length=150, blank=True, default='')
    stripe_session_id = models.CharField(max_length=150, blank=True, default='')
    customer_notes = models.TextField(blank=True, default='')
    admin_internal_notes = models.TextField(blank=True, default='')
    
    # Agreements
    terms_accepted = models.BooleanField(default=True)
    welfare_policy_acknowledged = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            date_str = datetime.date.today().strftime('%Y%m%d')
            rand_suffix = uuid.uuid4().hex[:6].upper()
            self.order_number = f"ORD-{date_str}-{rand_suffix}"
        super().save(*args, **kwargs)

    @property
    def destination_display(self):
        parts = [self.delivery_street_address]
        if self.delivery_apartment:
            parts.append(self.delivery_apartment)
        parts.append(f"{self.delivery_city}, {self.delivery_state} {self.delivery_postal_code}")
        return ", ".join(parts)

    def __str__(self):
        return f"{self.order_number} - {self.customer_name} (${self.total_amount:,.2f}) [{self.get_order_status_display()}]"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    pet = models.ForeignKey('catalog.Pet', on_delete=models.PROTECT, related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pet_name = models.CharField(max_length=100)
    pet_breed_name = models.CharField(max_length=100)
    pet_reference_number = models.CharField(max_length=50)

    class Meta:
        unique_together = ('order', 'pet')

    def __str__(self):
        return f"{self.pet_name} ({self.pet_reference_number}) - Order #{self.order.order_number}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=30)
    to_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.order.order_number}: {self.from_status} -> {self.to_status} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
