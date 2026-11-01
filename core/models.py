from django.db import models

class SiteSetting(models.Model):
    business_name = models.CharField(max_length=100, default='Royal Maltipoos')
    tagline = models.CharField(max_length=255, default="Premier Luxury Maltipoo & Maltese Placement & Chaperoned Delivery Atelier")
    phone = models.CharField(max_length=30, default='(212) 555-PAWS')
    email = models.EmailField(default='support@royalmaltipoos.shop')
    address = models.CharField(max_length=255, default='450 Lexington Avenue, Suite 1800, New York, NY 10017')
    operating_hours = models.CharField(max_length=150, default='Mon - Sat: 9:00 AM - 7:00 PM EST | Sun: By Private Appointment')
    delivery_disclaimer = models.TextField(
        default='Home delivery across the contiguous United States is coordinated via our licensed USDA-certified climate-controlled couriers or flight nannies. Animal safety, welfare, and climate conditions strictly dictate dispatch scheduling.'
    )
    animal_welfare_pledge = models.TextField(
        default='Every pet in our atelier receives comprehensive veterinary screenings, microchip registration, age-appropriate vaccinations, and our 10-Year Genetic Health Warranty before placement.'
    )
    standard_delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=250.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0888, help_text='NYC Sales Tax ~ 8.875%')
    enable_payment_simulator = models.BooleanField(default=True, help_text='Safe simulator for local development without live Stripe keys')
    
    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.business_name

    @classmethod
    def get_settings(cls):
        settings, _ = cls.objects.get_or_create(id=1)
        return settings
