from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
from catalog.models import PetCategory, PetBreed, Pet
from orders.models import Order, OrderItem
from reviews.models import Review, ReviewModerationHistory

User = get_user_model()

class ReviewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(
            username='verifiedbuyer',
            email='buyer@example.com',
            password='Password123!',
            role='customer'
        )
        self.non_buyer = User.objects.create_user(
            username='nonbuyer',
            email='nonbuyer@example.com',
            password='Password123!',
            role='customer'
        )
        self.staff_user = User.objects.create_user(
            username='moderator',
            email='mod@example.com',
            password='Password123!',
            role='staff',
            is_staff=True
        )
        self.category = PetCategory.objects.create(name="Dogs", slug="dogs")
        self.breed = PetBreed.objects.create(name="Maltese", slug="maltese", category=self.category)
        self.pet = Pet.objects.create(
            reference_number="TEST-REV-001",
            name="Snowball",
            category=self.category,
            breed=self.breed,
            date_of_birth=date.today() - timedelta(days=100),
            sex='male',
            price=Decimal("4600.00"),
            status='sold',
            is_published=True
        )
        # Create completed and paid order for verifiedbuyer
        order = Order.objects.create(
            customer=self.buyer,
            customer_name='Verified Buyer',
            customer_email='buyer@example.com',
            customer_phone='2125550111',
            delivery_street_address='10 CPW',
            delivery_city='New York',
            delivery_state='NY',
            delivery_postal_code='10023',
            subtotal=self.pet.price,
            total_amount=self.pet.price,
            payment_status='paid',
            order_status='delivered'
        )
        OrderItem.objects.create(order=order, pet=self.pet, price=self.pet.price)

    def test_verified_purchase_flag_automatic_assignment(self):
        self.client.login(username='verifiedbuyer', password='Password123!')
        url = reverse('reviews:write_review')
        payload = {
            'headline': 'An Absolute Dream Puppy!',
            'rating': 5,
            'comment': 'Snowball arrived in immaculate health and has melted our hearts. Chaperoned delivery was sublime!',
            'adopter_location': 'Manhattan, NYC',
            'pet': self.pet.id,
            'breed': self.breed.id
        }
        response = self.client.post(url, payload)
        self.assertRedirects(response, reverse('reviews:review_list'))
        
        review = Review.objects.get(pet=self.pet, customer=self.buyer)
        self.assertTrue(review.is_verified_purchase)
        self.assertEqual(review.status, 'pending') # Moderation required

    def test_unapproved_reviews_hidden_from_public_list(self):
        # Create a pending review
        review = Review.objects.create(
            customer=self.buyer,
            pet=self.pet,
            headline='Pending Review Test',
            comment='Testing moderation visibility.',
            rating=5,
            status='pending',
            is_verified_purchase=True
        )
        response = self.client.get(reverse('reviews:review_list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Pending Review Test')

        # Approve review
        review.status = 'approved'
        review.save()
        
        response = self.client.get(reverse('reviews:review_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending Review Test')
