from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
from decimal import Decimal
from .models import PetCategory, PetBreed, Pet

class CatalogTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Dynamic category and breed creation
        self.category = PetCategory.objects.create(
            name="Dogs",
            slug="dogs",
            description="Luxury canine companions.",
            is_active=True
        )
        self.breed = PetBreed.objects.create(
            name="Maltipoo",
            slug="maltipoo",
            category=self.category,
            description="Hypoallergenic Maltese and Poodle cross.",
            is_active=True
        )
        # Pet available
        self.pet1 = Pet.objects.create(
            reference_number="TEST-PET-001",
            name="Bella",
            category=self.category,
            breed=self.breed,
            date_of_birth=date.today() - timedelta(days=90),
            sex='female',
            coat_color='Champagne Apricot',
            expected_adult_size='Toy (5-8 lbs)',
            price=Decimal("4200.00"),
            status='available',
            is_published=True,
            is_featured=True,
            description="Sweet tempered, playful maltipoo puppy."
        )
        # Pet draft / unavailable
        self.pet2 = Pet.objects.create(
            reference_number="TEST-PET-002",
            name="ShadowPup",
            category=self.category,
            breed=self.breed,
            date_of_birth=date.today() - timedelta(days=60),
            sex='male',
            coat_color='White',
            expected_adult_size='Toy (6-9 lbs)',
            price=Decimal("3800.00"),
            status='draft',
            is_published=False,
            is_featured=False,
            description="Draft listing not ready for public."
        )

    def test_dynamic_category_and_breed_creation(self):
        # Admin adds new category (e.g. Cats) and breed (e.g. British Shorthair) without code modification
        cat_category = PetCategory.objects.create(name="Cats", slug="cats", is_active=True)
        cat_breed = PetBreed.objects.create(name="British Shorthair", slug="british-shorthair", category=cat_category, is_active=True)
        self.assertEqual(cat_breed.category.name, "Cats")
        self.assertTrue(PetCategory.objects.filter(slug="cats").exists())

    def test_pet_is_purchasable_property(self):
        self.assertTrue(self.pet1.is_purchasable)
        self.assertFalse(self.pet2.is_purchasable)

    def test_pet_calculated_age(self):
        self.assertIn("weeks", self.pet1.age_display)

    def test_catalog_pet_list_view_filters_unpublished(self):
        response = self.client.get(reverse('catalog:pet_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bella")
        self.assertNotContains(response, "ShadowPup")

    def test_catalog_category_and_breed_views(self):
        response = self.client.get(reverse('catalog:category_detail', kwargs={'category_slug': 'dogs'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bella")

        response = self.client.get(reverse('catalog:breed_detail', kwargs={'category_slug': 'dogs', 'breed_slug': 'maltipoo'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bella")

    def test_pet_detail_view(self):
        response = self.client.get(reverse('catalog:pet_detail', kwargs={'slug': self.pet1.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bella")
        self.assertContains(response, "$4200")

    def test_search_results(self):
        response = self.client.get(reverse('catalog:search'), {'q': 'Bella'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bella")

        response = self.client.get(reverse('catalog:search'), {'q': 'NonExistentPuppy'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Bella")
