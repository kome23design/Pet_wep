from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from datetime import date

class PetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    seo_title = models.CharField(max_length=150, blank=True, default='')
    seo_description = models.TextField(blank=True, default='')
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Pet Categories'
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.seo_title:
            self.seo_title = f"{self.name} for Sale | Royal Maltipoos"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'category_slug': self.slug})

    def __str__(self):
        return self.name


class PetBreed(models.Model):
    category = models.ForeignKey(PetCategory, on_delete=models.CASCADE, related_name='breeds')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True)
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='breeds/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    origin_history = models.TextField(blank=True, default='')
    temperament = models.CharField(max_length=200, blank=True, default='Affectionate, Intelligent, Gentle, Hypoallergenic')
    hypoallergenic = models.BooleanField(default=True)
    typical_weight = models.CharField(max_length=50, blank=True, default='6 - 12 lbs')
    life_expectancy = models.CharField(max_length=50, blank=True, default='12 - 15 years')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Pet Breeds'
        unique_together = ('category', 'slug')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:breed_detail', kwargs={'category_slug': self.category.slug, 'breed_slug': self.slug})

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Pet(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('reserved', 'Reserved (Checkout In Progress)'),
        ('sold', 'Sold / Adopted'),
        ('unavailable', 'Temporarily Unavailable'),
    )
    
    SEX_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('unknown', 'Unknown / Not Specified'),
    )

    reference_number = models.CharField(max_length=50, unique=True, help_text='Unique reference code, e.g. PP-DOG-2026-001')
    name = models.CharField(max_length=100, help_text='Pet listing name or title')
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    category = models.ForeignKey(PetCategory, on_delete=models.PROTECT, related_name='pets')
    breed = models.ForeignKey(PetBreed, on_delete=models.PROTECT, related_name='pets')
    description = models.TextField()
    date_of_birth = models.DateField(help_text='Birth date of the pet')
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, default='female')
    coat_color = models.CharField(max_length=100, default='Apricot Cream')
    expected_adult_size = models.CharField(max_length=100, default='8 - 11 lbs')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price in USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Medical & Veterinary Credentials
    microchip_id = models.CharField(max_length=60, unique=True, blank=True, null=True, help_text='ISO Standard 15-Digit Microchip ID')
    vaccination_summary = models.TextField(
        default='DHPP Series (Core Vaccinations), Bordetella, Rabies (age-appropriate), Deworming Schedule Complete.'
    )
    veterinary_health_certificate_number = models.CharField(max_length=80, blank=True, default='USDA-APHIS-7001-NYC')
    genetic_health_warranty_years = models.PositiveIntegerField(default=10, help_text='Royal Maltipoos 10-Year Genetic Health Warranty')
    
    # Lineage and Origin
    breeder_atelier_origin = models.CharField(max_length=150, default='Certified Ethical NY/CT Partner Atelier')
    current_location = models.CharField(max_length=150, default='Royal Maltipoos Manhattan Atelier - New York, NY')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.reference_number}")
            self.slug = base_slug
        super().save(*args, **kwargs)

    @property
    def age_weeks(self):
        if not self.date_of_birth:
            return 0
        days = (date.today() - self.date_of_birth).days
        return max(0, days // 7)

    @property
    def age_display(self):
        weeks = self.age_weeks
        if weeks < 8:
            return f"{weeks} weeks (Nursery - Available for Pre-Reserve)"
        elif weeks < 52:
            months = weeks // 4
            return f"{weeks} weeks ({months} months)"
        else:
            years = weeks // 52
            return f"{years} year(s) old"

    @property
    def is_purchasable(self):
        return self.is_published and self.status == 'available'

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()

    def get_absolute_url(self):
        return reverse('catalog:pet_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return f"{self.name} - {self.breed.name} (${self.price:,.2f}) [{self.get_status_display()}]"


class PetImage(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='pets/', blank=True, null=True)
    image_url = models.URLField(blank=True, default='', help_text='Curated demo photo URL if file upload not used')
    caption = models.CharField(max_length=150, blank=True, default='')
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'display_order', 'id']

    @property
    def url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return '/static/images/placeholder_puppy.svg'

    def __str__(self):
        return f"Photo for {self.pet.name} ({'Primary' if self.is_primary else 'Gallery'})"


class HealthDocument(models.Model):
    DOC_TYPES = (
        ('vaccination', 'Vaccination & Deworming Record'),
        ('vet_cert', 'Veterinary Certificate of Health Inspection'),
        ('microchip', 'Microchip Lifetime Registration Certificate'),
        ('warranty', '10-Year Genetic Health Warranty Agreement'),
        ('pedigree', 'Official Certified Pedigree / Lineage Record'),
        ('dna_test', 'Canine Health & Genetic DNA Panel (Embark/Wisdom)'),
    )

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='health_documents')
    title = models.CharField(max_length=150)
    document_type = models.CharField(max_length=30, choices=DOC_TYPES, default='vet_cert')
    document_file = models.FileField(upload_to='health_docs/', blank=True, null=True)
    issuing_veterinarian = models.CharField(max_length=120, default='Dr. Eleanor Vance, DVM (NYC Veterinary Medical Center)')
    clinic_name = models.CharField(max_length=150, default='Manhattan Animal Hospital & Wellness Group')
    issued_date = models.DateField(default=date.today)
    verification_code = models.CharField(max_length=50, blank=True, default='VET-AUTH-NYC-2026')
    notes = models.TextField(blank=True, default='Comprehensive examination: cardiac, pulmonary, patellas, bite, eyes clear and healthy.')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.pet.name}"
