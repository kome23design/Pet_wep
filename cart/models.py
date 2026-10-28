from django.db import models
from django.conf import settings
from decimal import Decimal
from catalog.models import Pet
from core.models import SiteSetting

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    @property
    def item_count(self):
        return self.items.count()

    @property
    def subtotal(self):
        return sum(item.pet.price for item in self.items.all())

    @property
    def delivery_fee(self):
        if self.item_count == 0:
            return Decimal('0.00')
        site_settings = SiteSetting.get_settings()
        return site_settings.standard_delivery_fee

    @property
    def tax_rate(self):
        site_settings = SiteSetting.get_settings()
        return site_settings.tax_rate

    @property
    def tax_amount(self):
        if self.item_count == 0:
            return Decimal('0.00')
        tax = (self.subtotal * self.tax_rate).quantize(Decimal('0.01'))
        return tax

    @property
    def total(self):
        if self.item_count == 0:
            return Decimal('0.00')
        return self.subtotal + self.delivery_fee + self.tax_amount

    def __str__(self):
        owner = self.user.username if self.user else f"Session {self.session_key}"
        return f"Cart ({owner}) - {self.item_count} pets"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    # Because each individual animal is unique, a pet can only be present once per cart
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='cart_items')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'pet')

    def __str__(self):
        return f"{self.pet.name} in Cart #{self.cart.id}"
