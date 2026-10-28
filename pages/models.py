from django.db import models

class ContactInquiry(models.Model):
    SUBJECT_CHOICES = (
        ('adoption_inquiry', 'Pet Placement & Availability Inquiry'),
        ('delivery_question', 'Delivery & Travel Logistics'),
        ('private_viewing', 'Request Private Viewing at Manhattan Atelier'),
        ('health_warranty', 'Health Guarantee & Lineage Question'),
        ('general', 'General Customer Concierge'),
    )

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, default='')
    subject = models.CharField(max_length=40, choices=SUBJECT_CHOICES, default='adoption_inquiry')
    pet_interest = models.CharField(max_length=150, blank=True, default='', help_text='e.g., Maltipoo Puppy or Reference ID')
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    staff_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Contact Inquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.created_at.strftime('%Y-%m-%d')})"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class FAQ(models.Model):
    CATEGORY_CHOICES = (
        ('adoption', 'Adoption & Placement Process'),
        ('delivery', 'Nationwide Chaperoned Delivery'),
        ('health', 'Health Standards & 10-Year Warranty'),
        ('care', 'Puppy Preparation & Settling In'),
    )

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='adoption')
    question = models.CharField(max_length=255)
    answer = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category', 'display_order', 'id']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.question}"


class GalleryItem(models.Model):
    title = models.CharField(max_length=150)
    caption = models.CharField(max_length=255, blank=True, default='')
    image = models.ImageField(upload_to='gallery/', blank=True, null=True)
    image_url = models.URLField(blank=True, default='')
    breed_tag = models.CharField(max_length=100, default='Maltipoo')
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    @property
    def url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return '/static/images/placeholder_puppy.svg'

    def __str__(self):
        return self.title


class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default='')

    class Meta:
        verbose_name_plural = 'Blog Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    author = models.CharField(max_length=100, default='Dr. Eleanor Vance, DVM')
    author_title = models.CharField(max_length=150, default='Chief Veterinary Officer')
    excerpt = models.TextField(help_text='Short preview summary for card listings')
    content = models.TextField(help_text='Full rich article body')
    image_url = models.URLField(blank=True, default='')
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    read_time = models.CharField(max_length=30, default='5 min read')
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    tags = models.CharField(max_length=200, blank=True, default='Puppy Care, Health')
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    @property
    def cover_url(self):
        if self.featured_image:
            return self.featured_image.url
        if self.image_url:
            return self.image_url
        return '/static/images/placeholder_puppy.svg'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('pages:blog_detail', kwargs={'slug': self.slug})
