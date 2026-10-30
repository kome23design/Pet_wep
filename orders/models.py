from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid
import datetime

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage Discount (%)'),
        ('fixed', 'Fixed Amount ($)'),
    )

    code = models.CharField(max_length=50, unique=True, help_text='Promo code string, e.g. PRESTIGE10')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text='Percentage or fixed USD amount')
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text='Leave empty for unlimited')
    times_used = models.PositiveIntegerField(default=0)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    description = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.discount_type == 'percentage':
            return f"{self.code} ({int(self.discount_value)}% off)"
        return f"{self.code} (${self.discount_value:,.2f} off)"

    def is_valid(self, subtotal=Decimal('0.00')):
        if not self.is_active:
            return False, "This coupon code is no longer active."
        from django.utils import timezone
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False, "This promotional code is not yet valid."
        if self.valid_to and now > self.valid_to:
            return False, "This promotional code has expired."
        if self.max_uses and self.times_used >= self.max_uses:
            return False, "This promotional code has reached its maximum redemptions."
        if subtotal < self.min_order_amount:
            return False, f"Minimum order subtotal of ${self.min_order_amount:,.2f} is required."
        return True, "Valid"

    def calculate_discount(self, subtotal):
        if self.discount_type == 'percentage':
            return (subtotal * (self.discount_value / Decimal('100.00'))).quantize(Decimal('0.01'))
        elif self.discount_type == 'fixed':
            return min(self.discount_value, subtotal).quantize(Decimal('0.01'))
        return Decimal('0.00')


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

    PAYMENT_METHOD_CHOICES = (
        ('paypal', 'PayPal'),
        ('chime', 'Chime'),
        ('cashapp', 'Cash App'),
        ('apple_pay', 'Apple Pay'),
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
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Payment Method & Statuses
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='paypal')
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
