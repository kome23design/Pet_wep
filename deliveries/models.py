from django.db import models
from django.conf import settings
from orders.models import Order
import uuid
import datetime

class Delivery(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Delivery Scheduled'),
        ('preparing', 'Pre-Travel Veterinary Check & Comfort Crate Setup'),
        ('picked_up', 'Picked Up from Manhattan Atelier'),
        ('in_transit', 'In Transit with Certified Chaperone'),
        ('out_for_delivery', 'Out for Final Hand-Delivery'),
        ('delivered', 'Safely Delivered & Health Transferred'),
        ('delayed', 'Weather / Animal Welfare Rest Stop Delay'),
        ('cancelled', 'Delivery Cancelled'),
    )

    CARRIER_TYPES = (
        ('courier_sprinter', 'Dedicated Climate-Controlled Sprinter (Ground)'),
        ('flight_nanny', 'In-Cabin Certified Flight Nanny (Air Travel)'),
        ('nyc_chaperone', 'NYC Metropolitan Private Chaperone'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    tracking_number = models.CharField(max_length=50, unique=True, editable=False)
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_deliveries'
    )
    carrier_type = models.CharField(max_length=30, choices=CARRIER_TYPES, default='courier_sprinter')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='scheduled')
    
    # Origin (Manhattan Atelier by default)
    origin_name = models.CharField(max_length=150, default='Royal Maltipoos Flagship Atelier')
    origin_address = models.CharField(max_length=255, default='450 Lexington Avenue, New York, NY 10017')
    origin_latitude = models.FloatField(default=40.7527)
    origin_longitude = models.FloatField(default=-73.9772)
    
    # Destination snapshot from Order
    destination_name = models.CharField(max_length=150)
    destination_address = models.CharField(max_length=255)
    destination_latitude = models.FloatField(default=40.7128)
    destination_longitude = models.FloatField(default=-74.0060)
    
    # Live GPS telemetry
    current_latitude = models.FloatField(default=40.7527)
    current_longitude = models.FloatField(default=-73.9772)
    last_location_update = models.DateTimeField(null=True, blank=True)
    current_location_label = models.CharField(max_length=200, default='Manhattan Dispatch Facility, New York, NY')
    is_live_tracking_active = models.BooleanField(default=False)
    
    # ETA & Schedule
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    scheduled_departure = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    
    # Delivery Confirmation
    recipient_signature_name = models.CharField(max_length=120, blank=True, default='')
    agent_confirmation_notes = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Deliveries'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            date_code = datetime.date.today().strftime('%y%m%d')
            rand_code = uuid.uuid4().hex[:6].upper()
            self.tracking_number = f"TRK-PP-{date_code}-{rand_code}"
        super().save(*args, **kwargs)

    @property
    def has_active_coordinates(self):
        return self.current_latitude is not None and self.current_longitude is not None

    def __str__(self):
        return f"{self.tracking_number} -> {self.destination_name} [{self.get_status_display()}]"


class DeliveryLocation(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='location_history')
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy_meters = models.FloatField(null=True, blank=True)
    speed_mph = models.FloatField(null=True, blank=True)
    heading_degrees = models.FloatField(null=True, blank=True)
    source = models.CharField(
        max_length=30,
        choices=(('gps', 'Courier GPS Device'), ('agent_portal', 'Agent Manual Update'), ('dispatcher', 'NYC Dispatch Console')),
        default='gps'
    )
    notes = models.CharField(max_length=255, blank=True, default='')
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"Loc ({self.latitude:.4f}, {self.longitude:.4f}) for {self.delivery.tracking_number} at {self.recorded_at.strftime('%H:%M:%S')}"


class DeliveryEvent(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='events')
    status = models.CharField(max_length=30)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    location_name = models.CharField(max_length=150, default='New York, NY')
    event_time = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-event_time']

    def __str__(self):
        return f"[{self.event_time.strftime('%Y-%m-%d %H:%M')}] {self.title} ({self.delivery.tracking_number})"
