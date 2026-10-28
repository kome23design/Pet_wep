from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from core.models import SiteSetting
from accounts.models import CustomerProfile, CustomerAddress, DeliveryAgentProfile
from catalog.models import PetCategory, PetBreed, Pet, PetImage, HealthDocument
from orders.models import Order, OrderItem, OrderStatusHistory
from payments.models import Payment
from deliveries.models import Delivery, DeliveryLocation, DeliveryEvent
from reviews.models import Review, ReviewModerationHistory
from pages.models import FAQ, GalleryItem, ContactInquiry

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the Prestige Paws NYC database with comprehensive demonstration data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing Prestige Paws NYC demonstration dataset..."))

        # 1. Site Setting
        settings = SiteSetting.get_settings()
        settings.business_name = "Prestige Paws NYC"
        settings.tagline = "Manhattan's Premier Pet Placement & Chaperoned Delivery Atelier"
        settings.phone = "(212) 555-PAWS"
        settings.email = "concierge@prestigepaws.nyc"
        settings.address = "450 Lexington Avenue, Suite 1800, New York, NY 10017"
        settings.standard_delivery_fee = Decimal('250.00')
        settings.tax_rate = Decimal('0.0888')
        settings.enable_payment_simulator = True
        settings.save()
        self.stdout.write(self.style.SUCCESS("[OK] Site Settings established."))

        # 2. Users
        # Superuser Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@prestigepaws.nyc',
                'first_name': 'Alexander',
                'last_name': 'Vanderbilt',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            }
        )
        if created:
            admin_user.set_password('AdminPass2026!')
            admin_user.save()

        # Staff Manager
        staff_user, created = User.objects.get_or_create(
            username='staff_lisa',
            defaults={
                'email': 'lisa@prestigepaws.nyc',
                'first_name': 'Lisa',
                'last_name': 'Sterling',
                'role': 'staff',
                'is_staff': True,
                'is_verified': True,
            }
        )
        if created:
            staff_user.set_password('StaffPass2026!')
            staff_user.save()

        # Delivery Courier
        courier_user, created = User.objects.get_or_create(
            username='courier_dave',
            defaults={
                'email': 'courier.dave@prestigepaws.nyc',
                'first_name': 'David',
                'last_name': 'Ross',
                'role': 'delivery_agent',
                'phone_number': '(212) 555-0199',
                'is_staff': True,
                'is_verified': True,
            }
        )
        if created:
            courier_user.set_password('CourierPass2026!')
            courier_user.save()
            DeliveryAgentProfile.objects.create(
                user=courier_user,
                badge_number='PP-NY-882',
                usda_license_id='USDA-APHIS-TR-10029',
                vehicle_make_model='Custom Mercedes-Benz Sprinter (Climate Controlled)',
                vehicle_license_plate='NYC-PET-1',
                contact_phone='(212) 555-0199',
                is_on_duty=True,
                current_latitude=40.7300,
                current_longitude=-74.0500,
                last_gps_update=timezone.now()
            )

        # Customer User
        customer_user, created = User.objects.get_or_create(
            username='customer_sophie',
            defaults={
                'email': 'sophie.miller@example.com',
                'first_name': 'Sophie',
                'last_name': 'Miller',
                'role': 'customer',
                'phone_number': '(917) 555-8832',
                'is_verified': True,
            }
        )
        if created:
            customer_user.set_password('CustomerPass2026!')
            customer_user.save()
            CustomerProfile.objects.create(
                user=customer_user,
                preferred_contact_method='email',
                residence_type='apartment',
                has_fenced_yard=False,
                has_experience_with_breed=True,
                newsletter_subscribed=True,
                special_care_notes='Doorman high-rise on Central Park West. Please notify concierge upon arrival.'
            )
            CustomerAddress.objects.create(
                user=customer_user,
                address_label='Central Park Residence',
                recipient_name='Sophie Miller',
                street_address='15 Central Park West',
                apartment_suite='Apt 14B',
                city='New York',
                state='NY',
                postal_code='10023',
                latitude=40.7698,
                longitude=-73.9818,
                is_default=True,
                delivery_instructions='Direct lobby check-in with front desk concierge.'
            )
        self.stdout.write(self.style.SUCCESS("[OK] Staff, Courier, and Customer accounts ready."))

        # 3. Catalog: Category & Breeds
        dog_cat, _ = PetCategory.objects.get_or_create(
            name='Dogs',
            defaults={
                'slug': 'dogs',
                'description': 'Hand-reared, ethically bred puppies from our certified network of veterinary-inspected partner ateliers.',
                'seo_title': 'Premium Puppies for Sale in NYC & US Home Delivery | Prestige Paws',
                'seo_description': 'Discover exquisite Maltipoo and Maltese puppies for sale in New York City with chaperoned delivery across the USA.',
                'display_order': 1,
            }
        )

        maltipoo_breed, _ = PetBreed.objects.get_or_create(
            category=dog_cat,
            name='Maltipoo',
            defaults={
                'slug': 'maltipoo',
                'description': 'The Maltipoo is an affectionate, gentle, and highly intelligent companion dog resulting from the cross between a Maltese and a Toy or Miniature Poodle. Renowned for their soft hypoallergenic coat and calm demeanor.',
                'temperament': 'Affectionate, Intelligent, Playful, Gentle, Hypoallergenic',
                'hypoallergenic': True,
                'typical_weight': '5 - 12 lbs',
                'life_expectancy': '12 - 16 years',
                'origin_history': 'Developed in the United States as a beloved low-shedding companion dog suited for urban luxury apartments and family estates alike.',
            }
        )

        maltese_breed, _ = PetBreed.objects.get_or_create(
            category=dog_cat,
            name='Maltese',
            defaults={
                'slug': 'maltese',
                'description': 'The Maltese is a timeless ancient aristocratic toy breed renowned for its silky snow-white coat, gentle devotion, and charming disposition. Extremely affectionate, intelligent, and naturally clean.',
                'temperament': 'Gentle, Playful, Devoted, Fearless, Sweet-Tempered',
                'hypoallergenic': True,
                'typical_weight': '4 - 7 lbs',
                'life_expectancy': '12 - 15 years',
                'origin_history': 'Celebrated for over two millennia as the royal companion of Mediterranean and European courts, the Maltese exemplifies classic elegance.',
            }
        )
        self.stdout.write(self.style.SUCCESS("[OK] Pet Category (Dogs) and Breeds (Maltipoo, Maltese) created."))

        # 4. Pet Listings
        today = date.today()
        puppies_data = [
            # Maltipoos
            {
                'ref': 'PP-MP-2026-001',
                'name': 'Milo',
                'breed': maltipoo_breed,
                'category': dog_cat,
                'dob': today - timedelta(weeks=10),
                'sex': 'male',
                'color': 'Apricot Cream',
                'size': '7 - 9 lbs as adult',
                'price': Decimal('3850.00'),
                'is_featured': True,
                'status': 'available',
                'desc': 'Milo is a charismatic, teddy-bear faced male Maltipoo with an enchanting apricot curly coat. Exceptionally cuddly, well-socialized with children and adults, and already familiar with crate sleeping and indoor pee-pad training. Includes complete health certificate and lifetime microchip.',
                'images': [
                    'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=800&q=80',
                    'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=800&q=80',
                ]
            },
            {
                'ref': 'PP-MP-2026-002',
                'name': 'Bella',
                'breed': maltipoo_breed,
                'category': dog_cat,
                'dob': today - timedelta(weeks=11),
                'sex': 'female',
                'color': 'Warm Champagne Honey',
                'size': '6 - 8 lbs as adult',
                'price': Decimal('4200.00'),
                'is_featured': True,
                'status': 'available',
                'desc': 'Bella has an exquisite petite frame with large expressive hazel eyes and a non-shedding plush fleece coat. Very tranquil personality, eager to please, and loves lap cuddling. Vetted clear by Dr. Eleanor Vance at Manhattan Animal Hospital.',
                'images': [
                    'https://images.unsplash.com/photo-1587300003388-59208cc962cb?auto=format&fit=crop&w=800&q=80',
                    'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=800&q=80',
                ]
            },
            {
                'ref': 'PP-MP-2026-003',
                'name': 'Teddy',
                'breed': maltipoo_breed,
                'category': dog_cat,
                'dob': today - timedelta(weeks=9),
                'sex': 'male',
                'color': 'Caramel Red',
                'size': '8 - 10 lbs as adult',
                'price': Decimal('3950.00'),
                'is_featured': False,
                'status': 'available',
                'desc': 'Teddy embodies the true living teddy-bear Maltipoo. Deep rich caramel coat with striking contrast. Playful curiosity, joyful temperament, and excellent response to early puppy training.',
                'images': [
                    'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=800&q=80',
                ]
            },
            {
                'ref': 'PP-MP-2026-004',
                'name': 'Daisy',
                'breed': maltipoo_breed,
                'category': dog_cat,
                'dob': today - timedelta(weeks=12),
                'sex': 'female',
                'color': 'Vanilla Biscuit & Cream',
                'size': '7 - 9 lbs as adult',
                'price': Decimal('3750.00'),
                'is_featured': False,
                'status': 'available',
                'desc': 'Daisy is a gentle, sweet-natured female puppy who adores human attention. Hypoallergenic double-coat, USDA certified for national transport, and current on all age-appropriate DHPP vaccines.',
                'images': [
                    'https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?auto=format&fit=crop&w=800&q=80',
                ]
            },
            # Maltese
            {
                'ref': 'PP-ML-2026-001',
                'name': 'Oliver',
                'breed': maltese_breed,
                'category': dog_cat,
                'dob': today - timedelta(weeks=10),
                'sex': 'male',
                'color': 'Pure Snow White',
                'size': '5 - 6 lbs as adult',
                'price': Decimal('4500.00'),
                'is_featured': True,
                'status': 'available',
                'desc': 'Oliver is a stunning example of purebred Maltese elegance. Silky straight pure white coat, button black nose, and dark soulful eyes. Gentle, loyal, and naturally quiet, making him ideal for refined city living.',
                'images': [
                    'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?auto=format&fit=crop&w=800&q=80',
                    'https://images.unsplash.com/photo-1544568100-847a948585b9?auto=format&fit=crop&w=800&q=80',
                ]
            },
            {
                'ref': 'PP-ML-2026-002',
                'name': 'Luna',
                'breed': maltese_breed,
                'category': dog_cat,
                'dob': today - timedelta(weeks=11),
                'sex': 'female',
                'color': 'Gleaming Pearl White',
                'size': '4.5 - 6 lbs as adult',
                'price': Decimal('4700.00'),
                'is_featured': True,
                'status': 'available',
                'desc': 'Luna possesses royal poise and an exceptionally loving heart. Silky pure pearl coat, flawless black pigment, and eager social personality. Fully vet health certified with DNA health panel clear.',
                'images': [
                    'https://images.unsplash.com/photo-1544568100-847a948585b9?auto=format&fit=crop&w=800&q=80',
                ]
            },
            {
                'ref': 'PP-ML-2026-003',
                'name': 'Coco',
                'breed': maltese_breed,
                'category': dog_cat,
                'dob': today - timedelta(weeks=13),
                'sex': 'female',
                'color': 'Snow White',
                'size': '5 - 7 lbs as adult',
                'price': Decimal('4400.00'),
                'is_featured': False,
                'status': 'available',
                'desc': 'Coco is a delightfully sweet and joyful Maltese puppy. Loving lap companion who thrives on gentle affection. Microchipped with national 24/7 recovery database registration included.',
                'images': [
                    'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?auto=format&fit=crop&w=800&q=80',
                ]
            },
            {
                'ref': 'PP-ML-2026-004',
                'name': 'Jasper',
                'breed': maltese_breed,
                'category': dog_cat,
                'dob': today - timedelta(weeks=14),
                'sex': 'male',
                'color': 'Pure White Silk',
                'size': '5.5 - 6.5 lbs as adult',
                'price': Decimal('4300.00'),
                'is_featured': False,
                'status': 'sold',  # For demonstrating sold state and order history
                'desc': 'Jasper is a playful and intelligent Maltese male placed into his loving forever home in Manhattan. Example of a successfully transitioned Prestige Paws placement.',
                'images': [
                    'https://images.unsplash.com/photo-1544568100-847a948585b9?auto=format&fit=crop&w=800&q=80',
                ]
            },
        ]

        created_pets = {}
        for p in puppies_data:
            pet_obj, _ = Pet.objects.get_or_create(
                reference_number=p['ref'],
                defaults={
                    'name': p['name'],
                    'category': p['category'],
                    'breed': p['breed'],
                    'description': p['desc'],
                    'date_of_birth': p['dob'],
                    'sex': p['sex'],
                    'coat_color': p['color'],
                    'expected_adult_size': p['size'],
                    'price': p['price'],
                    'status': p['status'],
                    'is_published': True,
                    'is_featured': p['is_featured'],
                    'microchip_id': f"98514100{hash(p['ref']) % 9000000 + 1000000}",
                    'veterinary_health_certificate_number': f"USDA-APHIS-NYC-{p['ref'][-3:]}",
                    'breeder_atelier_origin': 'Prestige Paws Certified NY Partner Atelier',
                    'current_location': 'Prestige Paws Manhattan Atelier - New York, NY',
                }
            )
            created_pets[p['ref']] = pet_obj

            # Images
            for idx, img_url in enumerate(p['images']):
                PetImage.objects.get_or_create(
                    pet=pet_obj,
                    image_url=img_url,
                    defaults={
                        'caption': f"{pet_obj.name} - Prestige Paws Certified Portrait",
                        'is_primary': (idx == 0),
                        'display_order': idx,
                    }
                )

            # Health Documents
            HealthDocument.objects.get_or_create(
                pet=pet_obj,
                document_type='vet_cert',
                defaults={
                    'title': f'Official Veterinary Certificate of Inspection - {pet_obj.name}',
                    'issuing_veterinarian': 'Dr. Eleanor Vance, DVM (Lic. #NY-048291)',
                    'clinic_name': 'Manhattan Animal Hospital & Wellness Group',
                    'issued_date': today - timedelta(days=5),
                    'notes': 'Cardiopulmonary clear, knees/patellas normal Grade 0, eyes clear, healthy bite.',
                }
            )
            HealthDocument.objects.get_or_create(
                pet=pet_obj,
                document_type='vaccination',
                defaults={
                    'title': f'Vaccine & Deworming Record Log - {pet_obj.name}',
                    'issuing_veterinarian': 'Dr. Eleanor Vance, DVM',
                    'clinic_name': 'Manhattan Animal Hospital',
                    'issued_date': today - timedelta(days=5),
                    'notes': 'DHPP 1st & 2nd doses administered. Bordetella intranasal complete. Strongid deworming protocol finished.',
                }
            )
            HealthDocument.objects.get_or_create(
                pet=pet_obj,
                document_type='warranty',
                defaults={
                    'title': f'Prestige Paws 10-Year Genetic Health Warranty - {pet_obj.name}',
                    'issuing_veterinarian': 'Prestige Paws Placement Directorate',
                    'clinic_name': 'Prestige Paws Legal & Veterinary Affairs',
                    'issued_date': today,
                    'notes': 'Comprehensive coverage guaranteeing freedom from congenital life-threatening genetic defects.',
                }
            )

        self.stdout.write(self.style.SUCCESS(f"[OK] {len(puppies_data)} Pet Listings with health credentials and images ready."))

        # 5. Demonstration Order & Live Delivery Tracking
        # Create an active delivery for customer_sophie with Jasper
        demo_pet = created_pets['PP-ML-2026-004']  # Jasper
        order, order_created = Order.objects.get_or_create(
            order_number='ORD-20261024-DEMO1',
            defaults={
                'customer': customer_user,
                'customer_name': 'Sophie Miller',
                'customer_email': 'sophie.miller@example.com',
                'customer_phone': '(917) 555-8832',
                'delivery_street_address': '15 Central Park West',
                'delivery_apartment': 'Apt 14B',
                'delivery_city': 'New York',
                'delivery_state': 'NY',
                'delivery_postal_code': '10023',
                'subtotal': demo_pet.price,
                'delivery_fee': Decimal('250.00'),
                'tax_amount': (demo_pet.price * Decimal('0.0888')).quantize(Decimal('0.01')),
                'total_amount': demo_pet.price + Decimal('250.00') + (demo_pet.price * Decimal('0.0888')).quantize(Decimal('0.01')),
                'payment_status': 'paid',
                'order_status': 'in_transit',
                'payment_reference': 'sim_ch_demo_prestige_paws_883',
                'preferred_delivery_window': 'Afternoon (1:00 PM - 5:00 PM EST)',
                'delivery_notes': 'Please phone concierge 15 minutes before arrival.',
                'terms_accepted': True,
                'welfare_policy_acknowledged': True,
            }
        )

        if order_created:
            OrderItem.objects.create(
                order=order,
                pet=demo_pet,
                price=demo_pet.price,
                pet_name=demo_pet.name,
                pet_breed_name=demo_pet.breed.name,
                pet_reference_number=demo_pet.reference_number
            )
            Payment.objects.create(
                order=order,
                amount=order.total_amount,
                payment_method='simulator',
                status='successful',
                stripe_payment_intent_id='pi_demo_test_983712984712',
                raw_response_notes='Demonstration Sandbox Payment Verified.'
            )
            OrderStatusHistory.objects.create(
                order=order,
                from_status='confirmed',
                to_status='in_transit',
                changed_by=staff_user,
                notes='Pet cleared final travel hydration check. Courier David Ross departed Manhattan dispatch facility.'
            )

            # Live Delivery record
            delivery, _ = Delivery.objects.get_or_create(
                order=order,
                defaults={
                    'tracking_number': 'TRK-PP-261024-DEMO1',
                    'assigned_agent': courier_user,
                    'carrier_type': 'courier_sprinter',
                    'status': 'in_transit',
                    'origin_name': 'Prestige Paws NYC Flagship Atelier',
                    'origin_address': '450 Lexington Avenue, New York, NY 10017',
                    'origin_latitude': 40.7527,
                    'origin_longitude': -73.9772,
                    'destination_name': 'Sophie Miller Residence',
                    'destination_address': '15 Central Park West, Apt 14B, New York, NY 10023',
                    'destination_latitude': 40.7698,
                    'destination_longitude': -73.9818,
                    # Current position: approaching Central Park South
                    'current_latitude': 40.7640,
                    'current_longitude': -73.9770,
                    'last_location_update': timezone.now() - timedelta(minutes=4),
                    'current_location_label': 'Approaching Central Park South, New York, NY',
                    'is_live_tracking_active': True,
                    'estimated_arrival': timezone.now() + timedelta(minutes=25),
                }
            )

            # Location trail (breadcrumbs)
            DeliveryLocation.objects.create(
                delivery=delivery,
                latitude=40.7527,
                longitude=-73.9772,
                source='dispatcher',
                notes='Departed Flagship Atelier on Lexington Ave',
                recorded_at=timezone.now() - timedelta(minutes=30)
            )
            DeliveryLocation.objects.create(
                delivery=delivery,
                latitude=40.7580,
                longitude=-73.9790,
                source='gps',
                notes='Cruising along 5th Avenue / 54th St corridor',
                recorded_at=timezone.now() - timedelta(minutes=15)
            )
            DeliveryLocation.objects.create(
                delivery=delivery,
                latitude=40.7640,
                longitude=-73.9770,
                source='gps',
                notes='Transitioning onto Central Park South, smooth road conditions',
                recorded_at=timezone.now() - timedelta(minutes=4)
            )

            # Milestones
            DeliveryEvent.objects.create(
                delivery=delivery,
                status='scheduled',
                title='Chaperoned Delivery Scheduled',
                description='Customer chosen preferred afternoon arrival window confirmed with concierge team.',
                location_name='NYC Flagship Atelier'
            )
            DeliveryEvent.objects.create(
                delivery=delivery,
                status='preparing',
                title='Pre-Travel Veterinary Check & Comfort Crate Placement',
                description='Dr. Vance verified hydration, temperature, and temperament. Climate-controlled Sprinter prepared at 70°F.',
                location_name='Prestige Paws Medical Bay'
            )
            DeliveryEvent.objects.create(
                delivery=delivery,
                status='in_transit',
                title='In Transit with Certified Chaperone David Ross',
                description='Sprinter in transit. Live GPS tracking active.',
                location_name='Manhattan Courier Route'
            )

        self.stdout.write(self.style.SUCCESS("[OK] Active Live Delivery Tracking demonstration order created (#ORD-20261024-DEMO1)."))

        # 6. Customer Reviews (Approved & Verified)
        reviews_data = [
            {
                'pet': created_pets['PP-MP-2026-001'],
                'breed': maltipoo_breed,
                'customer': customer_user,
                'rating': 5,
                'headline': 'The most professional, ethical pet placement experience in New York.',
                'comment': 'From our first consultation with Alexander to the moment our Maltipoo arrived via chaperoned transport, everything was seamless. Our veterinarian was thoroughly impressed by the thoroughness of the health records. Truly a 5-star atelier.',
                'location': 'Upper East Side, New York',
                'is_verified': True,
                'status': 'approved',
            },
            {
                'pet': created_pets['PP-ML-2026-001'],
                'breed': maltese_breed,
                'customer': customer_user,
                'rating': 5,
                'headline': 'Exquisite Maltese with impeccable manners and radiant coat!',
                'comment': 'Our little Oliver is pure joy. He was already familiar with gentle handling and slept peacefully through his first night. The live GPS courier tracking gave our family total peace of mind during travel.',
                'location': 'Tribeca, New York',
                'is_verified': True,
                'status': 'approved',
            },
            {
                'pet': created_pets['PP-MP-2026-002'],
                'breed': maltipoo_breed,
                'customer': customer_user,
                'rating': 5,
                'headline': 'Unrivaled care, transparency, and animal welfare standards.',
                'comment': 'Having visited other breeders, Prestige Paws stands in a category of its own. They prioritize animal welfare above all else. The 10-year genetic health guarantee speaks volumes about their confidence in their bloodlines.',
                'location': 'Greenwich, Connecticut',
                'is_verified': True,
                'status': 'approved',
            },
        ]

        for r in reviews_data:
            review_obj, _ = Review.objects.get_or_create(
                customer=r['customer'],
                headline=r['headline'],
                defaults={
                    'pet': r['pet'],
                    'breed': r['breed'],
                    'rating': r['rating'],
                    'comment': r['comment'],
                    'adopter_location': r['location'],
                    'is_verified_purchase': r['is_verified'],
                    'status': r['status'],
                    'moderated_by': staff_user,
                    'moderated_at': timezone.now(),
                    'admin_notes': 'Verified customer review meeting all quality guidelines.'
                }
            )

        self.stdout.write(self.style.SUCCESS("[OK] Verified 5-star customer reviews published."))

        # 7. FAQs
        faqs_data = [
            {
                'cat': 'adoption',
                'q': 'How does the Prestige Paws placement process work?',
                'a': 'Our placement process is designed to ensure a perfect match. You may browse our available puppies online, schedule a private consultation at our Manhattan Atelier, or complete your reservation directly through our secure platform. Every adoption includes comprehensive health documents, full ownership transfer, and chaperoned travel coordination.',
                'order': 1
            },
            {
                'cat': 'delivery',
                'q': 'How does live order and delivery tracking work?',
                'a': 'Once your puppy has cleared their pre-travel veterinary inspection, they are placed with a dedicated, licensed animal transport specialist. For ground delivery, we utilize custom climate-controlled vehicles with real-time GPS telemetry. You can view your courier moving in real time on our interactive tracking map right from your customer dashboard.',
                'order': 2
            },
            {
                'cat': 'health',
                'q': 'What veterinary health guarantees are included?',
                'a': 'Every puppy comes with an official USDA Certificate of Veterinary Inspection issued within days of departure, up-to-date age-appropriate DHPP vaccinations, complete deworming history, ISO microchip registration, and our industry-leading 10-Year Genetic Health Warranty protecting against congenital life-threatening hereditary disorders.',
                'order': 3
            },
            {
                'cat': 'care',
                'q': 'Are Maltipoos and Maltese hypoallergenic?',
                'a': 'Both Maltipoos and Maltese produce minimal dander and have low-to-no shedding hair rather than fur, making them exceptionally well-tolerated by allergy sufferers. We also offer allergy consultation appointments at our atelier.',
                'order': 4
            },
        ]

        for f in faqs_data:
            FAQ.objects.get_or_create(
                question=f['q'],
                defaults={
                    'category': f['cat'],
                    'answer': f['a'],
                    'display_order': f['order'],
                    'is_published': True
                }
            )

        # 8. Gallery Items
        gallery_items = [
            {
                'title': 'Maltipoo at Manhattan Atelier',
                'tag': 'Maltipoo',
                'url': 'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=800&q=80',
                'caption': 'Socialization hour in our sunlit nursery room.'
            },
            {
                'title': 'Purebred Maltese Puppy Portrait',
                'tag': 'Maltese',
                'url': 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?auto=format&fit=crop&w=800&q=80',
                'caption': 'Classic snow-white Maltese puppy with radiant pigment.'
            },
            {
                'title': 'Chaperoned Travel Experience',
                'tag': 'Delivery',
                'url': 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?auto=format&fit=crop&w=800&q=80',
                'caption': 'Comfort-first climate controlled travel setup.'
            },
        ]
        for g in gallery_items:
            GalleryItem.objects.get_or_create(
                title=g['title'],
                defaults={
                    'breed_tag': g['tag'],
                    'image_url': g['url'],
                    'caption': g['caption'],
                    'is_featured': True
                }
            )

        self.stdout.write(self.style.SUCCESS("[OK] Demonstration FAQs and Gallery loaded."))
        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Complete Prestige Paws NYC demonstration dataset populated successfully!"))
        self.stdout.write(self.style.NOTICE("Demo credentials:"))
        self.stdout.write(self.style.NOTICE("  Admin:      admin / AdminPass2026!"))
        self.stdout.write(self.style.NOTICE("  Staff:      staff_lisa / StaffPass2026!"))
        self.stdout.write(self.style.NOTICE("  Courier:    courier_dave / CourierPass2026!"))
        self.stdout.write(self.style.NOTICE("  Customer:   customer_sophie / CustomerPass2026!"))
