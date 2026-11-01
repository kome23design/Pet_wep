import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
from catalog.models import PetCategory, PetBreed, Pet
from orders.models import Order, OrderItem
from deliveries.models import Delivery, DeliveryLocation, DeliveryEvent

User = get_user_model()

class DeliveriesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='delivcustomer',
            email='delivcustomer@example.com',
            password='Password123!',
            role='customer'
        )
        self.courier = User.objects.create_user(
            username='courierjohn',
            email='courierjohn@example.com',
            password='Password123!',
            role='delivery_agent',
            is_staff=True
        )
        self.other_user = User.objects.create_user(
            username='intruder',
            email='intruder@example.com',
            password='Password123!',
            role='customer'
        )
        self.category = PetCategory.objects.create(name="Dogs", slug="dogs")
        self.breed = PetBreed.objects.create(name="Maltipoo", slug="maltipoo", category=self.category)
        self.pet = Pet.objects.create(
            reference_number="TEST-DEL-001",
            name="Coco",
            category=self.category,
            breed=self.breed,
            date_of_birth=date.today() - timedelta(days=90),
            sex='female',
            price=Decimal("4300.00"),
            status='sold',
            is_published=True
        )
        self.order = Order.objects.create(
            customer=self.customer,
            customer_name='Eleanor Customer',
            customer_email='delivcustomer@example.com',
            customer_phone='2125550144',
            delivery_street_address='740 Park Ave',
            delivery_city='New York',
            delivery_state='NY',
            delivery_postal_code='10021',
            subtotal=Decimal("4300.00"),
            total_amount=Decimal("4300.00"),
            order_status='in_transit'
        )
        OrderItem.objects.create(order=self.order, pet=self.pet, price=self.pet.price)
        self.delivery = Delivery.objects.create(
            order=self.order,
            assigned_agent=self.courier,
            status='in_transit',
            origin_name='Royal Maltipoos Flagship Atelier',
            origin_address='450 Lexington Ave, Suite 1800, New York, NY 10017',
            origin_latitude=40.7527,
            origin_longitude=-73.9772,
            destination_name='Eleanor Customer',
            destination_address='740 Park Ave, New York, NY 10021',
            destination_latitude=40.7712,
            destination_longitude=-73.9654,
            current_latitude=40.7580,
            current_longitude=-73.9720,
            current_location_label='Manhattan Dispatch Facility, New York, NY'
        )

    def test_telemetry_polling_api(self):
        self.client.login(username='delivcustomer', password='Password123!')
        url = reverse('deliveries:telemetry_api', kwargs={'tracking_number': self.delivery.tracking_number})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'in_transit')
        self.assertIn('current_location', data)
        self.assertAlmostEqual(float(data['current_location']['lat']), 40.758, places=3)

    def test_courier_gps_coordinate_validation(self):
        self.client.login(username='courierjohn', password='Password123!')
        url = reverse('deliveries:courier_update_location', kwargs={'tracking_number': self.delivery.tracking_number})
        
        # Invalid latitude > 90
        invalid_payload = {
            'latitude': '95.0',
            'longitude': '-73.97',
            'status': 'in_transit',
            'location_label': 'Invalid latitude test',
            'notes': 'Out of bounds'
        }
        response = self.client.post(url, invalid_payload)
        self.assertEqual(response.status_code, 400)
        
        # Valid GPS update
        valid_payload = {
            'latitude': '40.7650',
            'longitude': '-73.9680',
            'status': 'in_transit',
            'location_label': 'Park Avenue Approaches',
            'notes': 'Approaching destination'
        }
        response = self.client.post(url, valid_payload)
        self.assertEqual(response.status_code, 200)
        
        self.delivery.refresh_from_db()
        self.assertAlmostEqual(self.delivery.current_latitude, 40.7650, places=4)
        # Verify location trail was recorded
        self.assertTrue(DeliveryLocation.objects.filter(delivery=self.delivery, latitude=40.765).exists())

    def test_unauthorized_courier_update_rejection(self):
        # Customer cannot post courier GPS updates
        self.client.login(username='delivcustomer', password='Password123!')
        url = reverse('deliveries:courier_update_location', kwargs={'tracking_number': self.delivery.tracking_number})
        payload = {
            'latitude': '40.7650',
            'longitude': '-73.9680'
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 403)
