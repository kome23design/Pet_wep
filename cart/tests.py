from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
from decimal import Decimal
from catalog.models import PetCategory, PetBreed, Pet
from cart.models import Cart, CartItem

class CartTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = PetCategory.objects.create(name="Dogs", slug="dogs")
        self.breed = PetBreed.objects.create(name="Maltese", slug="maltese", category=self.category)
        
        self.pet1 = Pet.objects.create(
            reference_number="TEST-CART-001",
            name="Daisy",
            category=self.category,
            breed=self.breed,
            date_of_birth=date.today() - timedelta(days=70),
            sex='female',
            price=Decimal("4500.00"),
            status='available',
            is_published=True
        )
        self.pet2 = Pet.objects.create(
            reference_number="TEST-CART-002",
            name="Charlie",
            category=self.category,
            breed=self.breed,
            date_of_birth=date.today() - timedelta(days=80),
            sex='male',
            price=Decimal("4000.00"),
            status='reserved',
            is_published=True
        )

    def test_add_pet_to_cart(self):
        response = self.client.post(reverse('cart:add_to_cart', kwargs={'pet_id': self.pet1.id}))
        self.assertRedirects(response, reverse('cart:view_cart'))
        
        cart = Cart.objects.first()
        self.assertIsNotNone(cart)
        self.assertEqual(cart.item_count, 1)
        self.assertEqual(cart.subtotal, Decimal("4500.00"))

    def test_unique_pet_constraint_prevents_duplicate_cart_item(self):
        # Adding same pet twice does not create duplicate items
        self.client.post(reverse('cart:add_to_cart', kwargs={'pet_id': self.pet1.id}))
        self.client.post(reverse('cart:add_to_cart', kwargs={'pet_id': self.pet1.id}))
        
        cart = Cart.objects.first()
        self.assertEqual(cart.item_count, 1)
        self.assertEqual(cart.items.filter(pet=self.pet1).count(), 1)

    def test_cannot_add_unavailable_pet_to_cart(self):
        response = self.client.post(reverse('cart:add_to_cart', kwargs={'pet_id': self.pet2.id}))
        cart = Cart.objects.first()
        if cart:
            self.assertEqual(cart.items.filter(pet=self.pet2).count(), 0)

    def test_remove_from_cart(self):
        self.client.post(reverse('cart:add_to_cart', kwargs={'pet_id': self.pet1.id}))
        cart = Cart.objects.first()
        item = cart.items.first()
        
        response = self.client.post(reverse('cart:remove_from_cart', kwargs={'item_id': item.id}))
        self.assertRedirects(response, reverse('cart:view_cart'))
        self.assertEqual(cart.item_count, 0)
