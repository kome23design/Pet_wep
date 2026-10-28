from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('staff', 'Staff / Inventory Manager'),
        ('delivery_agent', 'Pet Courier / Delivery Agent'),
        ('admin', 'Administrator'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=25, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_delivery_agent(self):
        return self.role == 'delivery_agent' or hasattr(self, 'delivery_profile')

    @property
    def is_store_staff(self):
        return self.role in ('staff', 'admin') or self.is_staff or self.is_superuser

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=(('email', 'Email'), ('phone', 'Phone Call'), ('sms', 'SMS Text')),
        default='email'
    )
    residence_type = models.CharField(
        max_length=30,
        choices=(('apartment', 'Luxury Apartment / Condo'), ('single_family', 'Single Family Home'), ('estate', 'Private Estate / Townhouse')),
        default='single_family'
    )
    has_fenced_yard = models.BooleanField(default=True)
    has_experience_with_breed = models.BooleanField(default=True)
    newsletter_subscribed = models.BooleanField(default=True)
    special_care_notes = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Profile of {self.user.username}"


class CustomerAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_addresses')
    address_label = models.CharField(max_length=50, default='Primary Residence', help_text='e.g., Manhattan Penthouse, Hamptons Home')
    recipient_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    apartment_suite = models.CharField(max_length=50, blank=True, default='')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50, default='NY')
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='United States')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    delivery_instructions = models.TextField(blank=True, default='', help_text='Doorman building, call on arrival, elevator instructions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Customer Addresses'
        ordering = ['-is_default', '-created_at']

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set other addresses of this user to is_default=False
            CustomerAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.recipient_name} - {self.street_address}, {self.city}, {self.state} {self.postal_code}"


class DeliveryAgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_profile')
    badge_number = models.CharField(max_length=30, unique=True)
    usda_license_id = models.CharField(max_length=50, blank=True, default='USDA-CERT-NY-7729')
    vehicle_make_model = models.CharField(max_length=100, default='Climate-Controlled Mercedes-Benz Sprinter')
    vehicle_license_plate = models.CharField(max_length=30, default='NYC-PAW-01')
    contact_phone = models.CharField(max_length=25)
    is_on_duty = models.BooleanField(default=True)
    current_latitude = models.FloatField(null=True, blank=True, default=40.7527)
    current_longitude = models.FloatField(null=True, blank=True, default=-73.9772)
    last_gps_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Courier {self.user.get_full_name() or self.user.username} [Badge #{self.badge_number}]"
