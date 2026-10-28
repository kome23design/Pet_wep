from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import CustomerAddress

User = get_user_model()

class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testclient',
            'email': 'client@example.com',
            'password': 'SecurePassword2026!',
            'first_name': 'Eleanor',
            'last_name': 'Vance',
        }
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            role='customer'
        )

    def test_user_creation_and_role(self):
        self.assertEqual(self.user.username, 'testclient')
        self.assertEqual(self.user.role, 'customer')
        self.assertFalse(self.user.is_staff)
        self.assertTrue(self.user.check_password('SecurePassword2026!'))

    def test_login_and_logout(self):
        login_success = self.client.login(username='testclient', password='SecurePassword2026!')
        self.assertTrue(login_success)

        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('pages:home'))

    def test_customer_address_book(self):
        address = CustomerAddress.objects.create(
            user=self.user,
            address_label='Manhattan Residence',
            recipient_name='Eleanor Vance',
            street_address='100 Central Park South',
            apartment_suite='Apt 14B',
            city='New York',
            state='NY',
            postal_code='10019',
            is_default=True
        )
        self.assertIn('100 Central Park South', str(address))
        self.assertTrue(address.is_default)

    def test_unauthenticated_dashboard_redirect(self):
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
