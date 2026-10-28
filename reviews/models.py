from django.db import models
from django.conf import settings
from catalog.models import Pet, PetBreed

class Review(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Moderation Review'),
        ('approved', 'Approved for Public Display'),
        ('rejected', 'Rejected / Inappropriate Content'),
    )

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    pet = models.ForeignKey(Pet, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    breed = models.ForeignKey(PetBreed, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)], default=5)
    headline = models.CharField(max_length=150)
    comment = models.TextField()
    adopter_location = models.CharField(max_length=100, default='New York, NY', help_text='City, State of adopter')
    
    is_verified_purchase = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    admin_notes = models.TextField(blank=True, default='')
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_reviews'
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def stars_range(self):
        return range(self.rating)

    @property
    def empty_stars_range(self):
        return range(5 - self.rating)

    def __str__(self):
        return f"{self.headline} ({self.rating}★) by {self.customer.get_full_name() or self.customer.username} [{self.get_status_display()}]"


class ReviewModerationHistory(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='moderation_logs')
    action = models.CharField(max_length=30)
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} on Review #{self.review.id} by {self.moderator} at {self.timestamp}"
