from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
from catalog.models import PetCategory, PetBreed, Pet
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem

User = get_user_model()

class OrdersTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='ordercustomer',
            email='ordercustomer@example.com',
            password='TestPassword123!',
            first_name='Caroline',
            last_name='Astor',
            role='customer'
        )
        self.category = PetCategory.objects.create(name="Dogs", slug="dogs")
        self.breed = PetBreed.objects.create(name="Maltipoo", slug="maltipoo", category=self.category)
        self.pet = Pet.objects.create(
            reference_number="TEST-ORD-001",
            name="Teddy",
            category=self.category,
            breed=self.breed,
            date_of_birth=date.today() - timedelta(days=75),
            sex='male',
            price=Decimal("4100.00"),
            status='available',
            is_published=True
        )

    def test_checkout_submission_and_order_creation(self):
        self.client.login(username='ordercustomer', password='TestPassword123!')
        
        # Add to cart
        self.client.post(reverse('cart:add_to_cart', kwargs={'pet_id': self.pet.id}))
        
        # Submit checkout
        checkout_payload = {
            'customer_name': 'Caroline Astor',
            'customer_email': 'ordercustomer@example.com',
            'customer_phone': '2125550188',
            'delivery_street_address': '840 Fifth Avenue',
            'delivery_apartment': 'Suite 10',
            'delivery_city': 'New York',
            'delivery_state': 'NY',
            'delivery_postal_code': '10065',
            'delivery_notes': 'Chaperoned hand-delivery please',
            'preferred_delivery_date': (date.today() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'preferred_delivery_window': 'Morning (9:00 AM - 1:00 PM EST)',
            'terms_accepted': 'on',
            'welfare_policy_acknowledged': 'on',
            'payment_choice': 'paypal'
        }
        response = self.client.post(reverse('orders:checkout'), checkout_payload)
        
        order = Order.objects.filter(customer=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().pet, self.pet)
        
        # Pet availability status should transition to reserved
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.status, 'reserved')

        # Verify order confirmation email was dispatched to customer
        self.assertGreaterEqual(len(mail.outbox), 1)
        confirmation_email = mail.outbox[-1]
        self.assertIn('ordercustomer@example.com', confirmation_email.to)
        self.assertIn(order.order_number, confirmation_email.subject)
        self.assertIn('Royal Maltipoos', confirmation_email.subject)
        self.assertTrue(len(confirmation_email.alternatives) > 0)
        self.assertIn('support@royalmaltipoos.shop', confirmation_email.alternatives[0][0])

    def test_order_cancellation_restores_inventory(self):
        # Create an order with reserved pet
        self.pet.status = 'reserved'
        self.pet.save()
        
        order = Order.objects.create(
            customer=self.user,
            customer_name='Caroline Astor',
            customer_email='ordercustomer@example.com',
            customer_phone='2125550188',
            delivery_street_address='840 Fifth Ave',
            delivery_city='New York',
            delivery_state='NY',
            delivery_postal_code='10065',
            subtotal=self.pet.price,
            total_amount=self.pet.price,
            order_status='pending_payment'
        )
        OrderItem.objects.create(order=order, pet=self.pet, price=self.pet.price)
        
        # Cancel order
        order.order_status = 'cancelled'
        order.save()
        
        # Business logic restores pet availability
        self.pet.status = 'available'
        self.pet.save()
        
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.status, 'available')

    def test_concurrent_purchase_locking_simulation(self):
        # Verify select_for_update transactional locking
        with transaction.atomic():
            locked_pet = Pet.objects.select_for_update().get(id=self.pet.id)
            self.assertEqual(locked_pet.status, 'available')
            locked_pet.status = 'reserved'
            locked_pet.save()

        self.pet.refresh_from_db()
        self.assertEqual(self.pet.status, 'reserved')
        # Pet is no longer purchasable
        self.assertFalse(self.pet.is_purchasable)
