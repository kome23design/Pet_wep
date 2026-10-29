from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import datetime

from catalog.models import PetCategory, PetBreed, Pet, PetImage
from reviews.models import Review
from pages.models import BlogPost, BlogCategory
from orders.models import Coupon
from accounts.models import User

class Command(BaseCommand):
    help = 'Seeds 4 coupons, Kitten category & breeds, 7+ Maltipoos, 7+ Maltese, 7+ Blogs, and 30 unique reviews.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding advanced adjustments data...")

        # 1. SEED 4 COUPONS
        coupons_data = [
            {
                'code': 'PRESTIGE10',
                'discount_type': 'percentage',
                'discount_value': Decimal('10.00'),
                'description': '10% Adopter Welcome Discount on Entire Order',
                'min_order_amount': Decimal('1000.00'),
            },
            {
                'code': 'WELCOME500',
                'discount_type': 'fixed',
                'discount_value': Decimal('500.00'),
                'description': '$500 Tier-1 Companion Placement Credit',
                'min_order_amount': Decimal('2000.00'),
            },
            {
                'code': 'VIPATELIER',
                'discount_type': 'percentage',
                'discount_value': Decimal('15.00'),
                'description': '15% Private Collector Concierge Courtesy Privilege',
                'min_order_amount': Decimal('2500.00'),
            },
            {
                'code': 'NYCPAWS',
                'discount_type': 'fixed',
                'discount_value': Decimal('250.00'),
                'description': '$250 Manhattan Flagship Adopter Celebration Discount',
                'min_order_amount': Decimal('1500.00'),
            },
        ]

        for cdata in coupons_data:
            c, created = Coupon.objects.update_or_create(
                code=cdata['code'],
                defaults={
                    'discount_type': cdata['discount_type'],
                    'discount_value': cdata['discount_value'],
                    'description': cdata['description'],
                    'min_order_amount': cdata['min_order_amount'],
                    'is_active': True,
                }
            )
            self.stdout.write(f"Coupon: {c.code} ({c.get_discount_type_display()} - {c.discount_value})")

        # 2. SEED KITTEN CATEGORY & BREEDS
        cat_kittens, _ = PetCategory.objects.get_or_create(
            slug='kittens',
            defaults={
                'name': 'Kittens',
                'description': 'Elite nursery kittens with royal pedigrees, feline vaccination records, and champion lineage. Raised in serene Manhattan nursery suites.',
                'is_active': True,
                'display_order': 2,
            }
        )

        b_british, _ = PetBreed.objects.get_or_create(
            slug='british-shorthair',
            defaults={
                'name': 'British Shorthair',
                'category': cat_kittens,
                'description': 'Calm, affectionate aristocratic companions with dense plush coats, round cheeks, and gentle temperaments.',
                'temperament': 'Calm, gentle, easygoing, loyal',
                'life_expectancy': '14 - 18 years',
                'is_active': True,
                'hypoallergenic': True,
            }
        )

        b_ragdoll, _ = PetBreed.objects.get_or_create(
            slug='ragdoll',
            defaults={
                'name': 'Ragdoll',
                'category': cat_kittens,
                'description': 'Docile, captivating sapphire-eyed companions renowned for relaxing peacefully like a ragdoll when held.',
                'temperament': 'Affectionate, trusting, docile, gentle lap companion',
                'life_expectancy': '15 - 19 years',
                'is_active': True,
                'hypoallergenic': False,
            }
        )

        b_fold, _ = PetBreed.objects.get_or_create(
            slug='scottish-fold',
            defaults={
                'name': 'Scottish Fold',
                'category': cat_kittens,
                'description': 'Sweet-tempered companions celebrated for their distinct folded ears, owl-like expression, and quiet purring companionship.',
                'temperament': 'Quiet, sweet, curious, highly sociable',
                'life_expectancy': '12 - 15 years',
                'is_active': True,
                'hypoallergenic': False,
            }
        )

        # 3. SEED KITTEN PET LISTINGS
        kittens_data = [
            {
                'name': 'Duchess Cleo',
                'ref': 'PP-BSH-2026-001',
                'breed': b_british,
                'category': cat_kittens,
                'price': Decimal('3600.00'),
                'dob': datetime.date(2026, 7, 10),
                'sex': 'female',
                'coat': 'Classic Silver Tabby Plush',
                'adult_size': '8 - 12 lbs',
                'desc': 'Cleo is a breathtaking purebred British Shorthair with luminous emerald-tinted eyes, dense plush silver tabby coat, and an affectionate, regal demeanor.',
                'microchip': '985141004128901',
                'is_featured': True,
                'images': [
                    'https://images.unsplash.com/photo-1574158622682-e40e69881006?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=1000&q=80'
                ]
            },
            {
                'name': 'Prince Oliver',
                'ref': 'PP-RAG-2026-002',
                'breed': b_ragdoll,
                'category': cat_kittens,
                'price': Decimal('3950.00'),
                'dob': datetime.date(2026, 7, 24),
                'sex': 'male',
                'coat': 'Seal Point Mitted Silk',
                'adult_size': '12 - 16 lbs',
                'desc': 'Oliver is a stunning Ragdoll boy with deep sapphire blue eyes, extraordinarily soft silky fur, and a signature relaxed, purring temperament in your arms.',
                'microchip': '985141004128902',
                'is_featured': True,
                'images': [
                    'https://images.unsplash.com/photo-1513360309081-3647f1c1f543?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1561948955-570b270e7c36?auto=format&fit=crop&w=1000&q=80'
                ]
            },
            {
                'name': 'Lady Penelope',
                'ref': 'PP-SKF-2026-003',
                'breed': b_fold,
                'category': cat_kittens,
                'price': Decimal('3800.00'),
                'dob': datetime.date(2026, 8, 2),
                'sex': 'female',
                'coat': 'Cream White Lilac Point',
                'adult_size': '7 - 10 lbs',
                'desc': 'Penelope is a mesmerizing Scottish Fold female kitten with gentle folded ears, huge round amber eyes, and an inquisitive, sweet nature.',
                'microchip': '985141004128903',
                'is_featured': True,
                'images': [
                    'https://images.unsplash.com/photo-1573865526739-10659fec78a5?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1548802673-380ab8ebc7b7?auto=format&fit=crop&w=1000&q=80'
                ]
            },
            {
                'name': 'Baron Jasper',
                'ref': 'PP-BSH-2026-004',
                'breed': b_british,
                'category': cat_kittens,
                'price': Decimal('3450.00'),
                'dob': datetime.date(2026, 8, 14),
                'sex': 'male',
                'coat': 'Solid British Blue Slate',
                'adult_size': '10 - 14 lbs',
                'desc': 'Jasper features the iconic rich slate-blue coat of British royalty paired with vivid golden-copper eyes. Gentle, intelligent, and exceptionally affectionate.',
                'microchip': '985141004128904',
                'is_featured': False,
                'images': [
                    'https://images.unsplash.com/photo-1526336024174-e58f5cdd8e13?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1535930891776-0c2dfb7fda1a?auto=format&fit=crop&w=1000&q=80'
                ]
            }
        ]

        for kdata in kittens_data:
            pet, created = Pet.objects.get_or_create(
                reference_number=kdata['ref'],
                defaults={
                    'name': kdata['name'],
                    'breed': kdata['breed'],
                    'category': kdata['category'],
                    'price': kdata['price'],
                    'date_of_birth': kdata['dob'],
                    'sex': kdata['sex'],
                    'coat_color': kdata['coat'],
                    'expected_adult_size': kdata['adult_size'],
                    'description': kdata['desc'],
                    'microchip_id': kdata['microchip'],
                    'status': 'available',
                    'is_published': True,
                    'is_featured': kdata['is_featured'],
                    'vaccination_summary': 'FVRCP Series (Feline Viral Rhinotracheitis, Calicivirus, Panleukopenia), Rabies, Microchipped & Dewormed.',
                    'veterinary_health_certificate_number': 'USDA-APHIS-FELINE-NYC',
                    'breeder_atelier_origin': 'Prestige Paws Feline Nursery Directorate - New York',
                    'current_location': 'Prestige Paws Manhattan Atelier - New York, NY',
                }
            )
            for idx, img_url in enumerate(kdata['images']):
                PetImage.objects.get_or_create(
                    pet=pet,
                    image_url=img_url,
                    defaults={'is_primary': (idx == 0), 'display_order': idx}
                )

        # 4. EXPAND MALTIPOOS TO AT LEAST 7
        cat_dogs = PetCategory.objects.get(slug='dogs')
        b_maltipoo = PetBreed.objects.get(slug='maltipoo')
        b_maltese = PetBreed.objects.get(slug='maltese')

        new_maltipoos = [
            {
                'name': 'Giselle',
                'ref': 'PP-MP-2026-005',
                'price': Decimal('3900.00'),
                'dob': datetime.date(2026, 7, 28),
                'sex': 'female',
                'coat': 'Champagne Peach Silk',
                'adult_size': '6 - 9 lbs',
                'desc': 'Giselle is a sweetheart with soft wavy champagne curls, button nose, and a gentle cuddle-first personality. Hypoallergenic and highly intelligent.',
                'microchip': '985141004128911',
                'images': [
                    'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=1000&q=80'
                ]
            },
            {
                'name': 'Theo',
                'ref': 'PP-MP-2026-006',
                'price': Decimal('3650.00'),
                'dob': datetime.date(2026, 8, 3),
                'sex': 'male',
                'coat': 'Warm Apricot Creme',
                'adult_size': '7 - 10 lbs',
                'desc': 'Theo is a joyful Maltipoo boy with bright hazel-dark eyes, teddy-bear structure, and enthusiastic tail-wags. Great with children and apartment living.',
                'microchip': '985141004128912',
                'images': [
                    'https://images.unsplash.com/photo-1587300003388-59208cc962cb?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?auto=format&fit=crop&w=1000&q=80'
                ]
            },
            {
                'name': 'Aria',
                'ref': 'PP-MP-2026-007',
                'price': Decimal('4200.00'),
                'dob': datetime.date(2026, 8, 12),
                'sex': 'female',
                'coat': 'Pure Pearl White Fleece',
                'adult_size': '5 - 8 lbs',
                'desc': 'Aria is a rare tiny teacup-range Maltipoo with luxurious fleece non-shedding coat and gentle lap demeanor. Perfect companion for Manhattan residences.',
                'microchip': '985141004128913',
                'images': [
                    'https://images.unsplash.com/photo-1591769225440-811ad7d6eab2?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=1000&q=80'
                ]
            },
            {
                'name': 'Finley',
                'ref': 'PP-MP-2026-008',
                'price': Decimal('3800.00'),
                'dob': datetime.date(2026, 8, 18),
                'sex': 'male',
                'coat': 'Honey Biscuit Ripple',
                'adult_size': '7 - 10 lbs',
                'desc': 'Finley loves playtime, learning new commands with positive reinforcement, and lounging quietly on velvet cushions. Hypoallergenic coat.',
                'microchip': '985141004128914',
                'images': [
                    'https://images.unsplash.com/photo-1583511655826-05700d52f4d9?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1544568100-847a948585b9?auto=format&fit=crop&w=1000&q=80'
                ]
            }
        ]

        for mp in new_maltipoos:
            p, _ = Pet.objects.get_or_create(
                reference_number=mp['ref'],
                defaults={
                    'name': mp['name'],
                    'breed': b_maltipoo,
                    'category': cat_dogs,
                    'price': mp['price'],
                    'date_of_birth': mp['dob'],
                    'sex': mp['sex'],
                    'coat_color': mp['coat'],
                    'expected_adult_size': mp['adult_size'],
                    'description': mp['desc'],
                    'microchip_id': mp['microchip'],
                    'status': 'available',
                    'is_published': True,
                    'is_featured': True,
                }
            )
            for idx, img in enumerate(mp['images']):
                PetImage.objects.get_or_create(pet=p, image_url=img, defaults={'is_primary': (idx == 0), 'display_order': idx})

        # 5. EXPAND MALTESE TO AT LEAST 7
        new_maltese = [
            {
                'name': 'Valentina',
                'ref': 'PP-ML-2026-005',
                'price': Decimal('4400.00'),
                'dob': datetime.date(2026, 7, 20),
                'sex': 'female',
                'coat': 'Pure Snow White Silk',
                'adult_size': '4 - 7 lbs',
                'desc': 'Valentina represents purebred Maltese perfection with large expressive dark eyes, pitch black points, and a floor-length silky coat. Incredibly graceful.',
                'microchip': '985141004128921',
                'images': [
                    'https://images.unsplash.com/photo-1508948956644-0017e845d09f?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1518020382113-a7e8fc38eac9?auto=format&fit=crop&w=1000&q=80'
                ]
            },
            {
                'name': 'Casper',
                'ref': 'PP-ML-2026-006',
                'price': Decimal('3750.00'),
                'dob': datetime.date(2026, 8, 1),
                'sex': 'male',
                'coat': 'Gleaming Alabaster Silk',
                'adult_size': '5 - 8 lbs',
                'desc': 'Casper is a polite, gentle purebred Maltese puppy with a loving disposition, soft dark eyes, and a joyful prance. Microchipped and nursery crate trained.',
                'microchip': '985141004128922',
                'images': [
                    'https://images.unsplash.com/photo-1588943211346-0908a1fb0b01?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1576201836106-db1758fd1c97?auto=format&fit=crop&w=1000&q=80'
                ]
            },
            {
                'name': 'Seraphina',
                'ref': 'PP-ML-2026-007',
                'price': Decimal('4600.00'),
                'dob': datetime.date(2026, 8, 9),
                'sex': 'female',
                'coat': 'Porcelain White Royalty Silk',
                'adult_size': '4 - 6 lbs',
                'desc': 'Seraphina has a breathtaking doll-face, jet black nose, and an affectionate soul that loves sitting gently on silk lap throws during evening tea.',
                'microchip': '985141004128923',
                'images': [
                    'https://images.unsplash.com/photo-1601758228041-f3b2795255f1?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1598133894008-61f7fdb8cc3a?auto=format&fit=crop&w=1000&q=80'
                ]
            },
            {
                'name': 'Maximilian',
                'ref': 'PP-ML-2026-008',
                'price': Decimal('3900.00'),
                'dob': datetime.date(2026, 8, 22),
                'sex': 'male',
                'coat': 'Pure White Satin',
                'adult_size': '5 - 7 lbs',
                'desc': 'Maximilian is a playful, proud Maltese gentleman with a vibrant smile, healthy lineage, and stellar response to early socialization protocols.',
                'microchip': '985141004128924',
                'images': [
                    'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=1000&q=80',
                    'https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&w=1000&q=80'
                ]
            }
        ]

        for ml in new_maltese:
            p, _ = Pet.objects.get_or_create(
                reference_number=ml['ref'],
                defaults={
                    'name': ml['name'],
                    'breed': b_maltese,
                    'category': cat_dogs,
                    'price': ml['price'],
                    'date_of_birth': ml['dob'],
                    'sex': ml['sex'],
                    'coat_color': ml['coat'],
                    'expected_adult_size': ml['adult_size'],
                    'description': ml['desc'],
                    'microchip_id': ml['microchip'],
                    'status': 'available',
                    'is_published': True,
                    'is_featured': True,
                }
            )
            for idx, img in enumerate(ml['images']):
                PetImage.objects.get_or_create(pet=p, image_url=img, defaults={'is_primary': (idx == 0), 'display_order': idx})

        # 6. EXPAND BLOGS TO AT LEAST 7
        b_cat, _ = BlogCategory.objects.get_or_create(name='Pediatric Wellness', defaults={'slug': 'pediatric-wellness', 'description': 'Veterinary wellness and nursery health guides.'})
        new_blogs = [
            {
                'title': 'The Feline Atelier Protocol: Introducing Your British Shorthair or Ragdoll Home',
                'slug': 'feline-atelier-home-introduction-protocol',
                'category': b_cat,
                'excerpt': 'Key veterinary milestones, gentle scent-swapping protocols, and high-rise living accommodations for elite kittens.',
                'content': '''<h3>Creating an Aristocratic Sanctuary for Your Kitten</h3>
<p>Bringing an elite feline companion into your residence requires a tranquil, phased introduction. Unlike canines who explore outward immediately, pedigree felines evaluate vertical territory first.</p>
<h4>1. The First 48 Hours: The Sanctuary Chamber</h4>
<p>Dedicate a quiet master bedroom suite or nursery room equipped with plush bedding, an unscented natural litter station, and ceramic water fountains.</p>
<h4>2. Nutritional Foundations</h4>
<p>Maintain the nursery-supplied wet mousse formula for the first 14 days before gradually transitioning to tailored feline protein kibble.</p>''',
                'read_time': 5,
                'author': 'Dr. Alistair Finch, DVM',
                'author_title': 'Director of Pediatric Feline Medicine',
                'image_url': 'https://images.unsplash.com/photo-1574158622682-e40e69881006?auto=format&fit=crop&w=1200&q=80',
                'tags': 'Kittens, Feline Care, Nutrition, NYC Living',
            },
            {
                'title': 'Grooming the Royal Maltese Coat: Secrets of Professional Pin-Brushing and Tear Stain Prevention',
                'slug': 'grooming-royal-maltese-coat-tear-stain-prevention',
                'category': b_cat,
                'excerpt': 'How master groomers maintain the snow-white luster and tear-stain-free brilliance of purebred Maltese companions.',
                'content': '''<h3>The Art of Maltese Coat Maintenance</h3>
<p>The single-layer silk coat of the purebred Maltese produces zero dander, making it legendary among hypoallergenic breeds. However, keeping this snow-white coat immaculate requires mindful daily rituals.</p>
<h4>Filtered Water is Non-Negotiable</h4>
<p>Tear staining is primarily caused by high mineral and iron content in metropolitan tap water interacting with natural porphyrins. Always provide reverse-osmosis or purified bottled water.</p>
<h4>Daily Pin-Brushing Ritual</h4>
<p>Use a wooden-pin static-free brush lightly misted with organic botanical detangler before combing.</p>''',
                'read_time': 6,
                'author': 'Vivienne De La Tour',
                'author_title': 'Master Canine Grooming Specialist',
                'image_url': 'https://images.unsplash.com/photo-1508948956644-0017e845d09f?auto=format&fit=crop&w=1200&q=80',
                'tags': 'Maltese, Grooming, Hypoallergenic, Coat Care',
            }
        ]

        for b in new_blogs:
            BlogPost.objects.get_or_create(
                slug=b['slug'],
                defaults={
                    'title': b['title'],
                    'category': b['category'],
                    'excerpt': b['excerpt'],
                    'content': b['content'],
                    'read_time': b['read_time'],
                    'author': b['author'],
                    'author_title': b['author_title'],
                    'image_url': b['image_url'],
                    'tags': b['tags'],
                    'is_featured': True,
                    'is_published': True,
                    'published_at': timezone.now() - datetime.timedelta(days=3),
                }
            )

        # 7. SEED 30 REVIEWS (3-5 STARS, DIFFERENT DATES, UNIQUE NAMES)
        reviews_dataset = [
            # 5-star reviews
            ("Charlotte DuPont", 5, "Our Maltipoo, Bella, arrived in Greenwich via flight nanny in immaculate health. Her calm temperament in our home is proof of their nursery care.", datetime.date(2025, 4, 12), "Upper East Side & Greenwich, CT"),
            ("Marcus & Eleanor Vance", 5, "The level of veterinary documentation and microchip verification provided at our Manhattan apartment exceeded every expectation. An elite atelier.", datetime.date(2025, 5, 18), "Tribeca, New York"),
            ("Dr. Harrison Wells", 5, "As a practicing physician, allergy safety was my priority. Our Maltese has zero shedding and my children have had no allergic reactions whatsoever.", datetime.date(2025, 6, 4), "Central Park West, NYC"),
            ("Vivienne Sterling", 5, "From our private viewing at the Lexington Avenue suite to the doorstep handover in Brooklyn Heights, the entire experience was flawless.", datetime.date(2025, 6, 29), "Brooklyn Heights, NY"),
            ("Alistair Finch", 5, "Our British Shorthair kitten, Cleo, has the sweetest, calmest disposition. She purred the moment she stepped out of her travel carrier.", datetime.date(2025, 7, 15), "SoHo, Manhattan"),
            ("Genevieve Thorne", 5, "Truly a bespoke service. Our courier arrived precisely on time with a temperature-monitored carrier and comprehensive health records.", datetime.date(2025, 8, 3), "Hamptons, NY"),
            ("Julian & Clara Hayes", 5, "Milo is the joy of our townhouse. His crate training from the nursery made his first week seamless. Thank you Prestige Paws!", datetime.date(2025, 8, 22), "Gramercy Park, NYC"),
            ("Beatrice Montgomery", 5, "The genetic health warranty and USDA certifications gave my family complete peace of mind. Our puppy is thriving.", datetime.date(2025, 9, 10), "West Village, NYC"),
            ("Sophia Kensington", 5, "The flight nanny kept us updated with flight photos and text messages during every layover. Exceptional care for the puppy.", datetime.date(2025, 9, 28), "Beverly Hills, CA"),
            ("Oliver & Margot Drake", 5, "We adopted our Ragdoll kitten through Prestige Paws and the transition was peaceful and loving. Highest recommendation.", datetime.date(2025, 10, 14), "Midtown East, NYC"),
            ("Lady Catherine Howard", 5, "Prestige Paws represents what all pet adoption should be: compassionate, transparent, and strictly veterinary-supervised.", datetime.date(2025, 10, 30), "Upper West Side, NYC"),
            ("Sebastian Cross", 5, "Our Maltese puppy arrived bathed, groomed, and happy. The 30-day nutrition starter kit was immensely helpful.", datetime.date(2025, 11, 16), "Boston, MA"),
            ("Audrey & Liam Bennett", 5, "The concierge team answered every single pediatric nutrition question we had. Our Maltipoo is healthy, playful, and so loving.", datetime.date(2025, 12, 2), "DUMBO, Brooklyn"),
            ("Jonathan Sterling, Esq.", 5, "Impressed by the contractual transparency and health guarantees. Prestige Paws NYC is the premier standard.", datetime.date(2025, 12, 19), "Wall Street Corridor, NYC"),
            ("Victoria Pemberton", 5, "Our Scottish Fold kitten is healthy, affectionate, and was immediately at home with our family. Wonderful experience.", datetime.date(2026, 1, 8), "Greenwich Village, NYC"),
            ("Maximilian Roth", 5, "The in-person consultation in Manhattan was private, serene, and unhurried. You can tell they deeply love these animals.", datetime.date(2026, 1, 25), "Park Avenue, NYC"),
            ("Isabella Fontaine", 5, "My Maltipoo puppy has become the star of our building. So well-socialized and calm around city noises.", datetime.date(2026, 2, 11), "Chelsea, NYC"),
            ("Alexander Sinclair", 5, "Professionalism from start to finish. The veterinary records were stamped by certified clinicians and all vaccines were up to date.", datetime.date(2026, 2, 27), "Scarsdale, NY"),
            ("Evelyn & Thomas Ward", 5, "Our Maltese is pure joy. Soft, clean, playful, and the gentlest companion for our grandparents.", datetime.date(2026, 3, 15), "Chicago, IL"),
            ("Camilla Davenport", 5, "Everything was managed with clockwork precision. The flight nanny handover ceremony at JFK was warm and professional.", datetime.date(2026, 4, 2), "Long Island, NY"),
            ("Nathaniel Brooks", 5, "I was hesitant about remote placement, but Prestige Paws provided live video consultations and detailed health reports. Outstanding.", datetime.date(2026, 4, 20), "Miami, FL"),
            ("Seraphina Laurent", 5, "The best pet adoption experience in New York. Ethical breeding standards you can verify yourself.", datetime.date(2026, 5, 8), "Hudson Yards, NYC"),

            # 4-star reviews
            ("Gwendolyn Clark", 4, "Wonderful puppy and excellent health records. Delivery took about 45 minutes longer due to Midtown traffic, but the courier called ahead.", datetime.date(2025, 7, 2), "Flatiron, NYC"),
            ("Edward & Penelope King", 4, "Our Maltipoo is healthy, clever, and adorable. The welcome kit could use an extra chew toy, but otherwise top notch.", datetime.date(2025, 8, 19), "Hoboken, NJ"),
            ("Madeleine Ross", 4, "Very high quality kitten and documentation. Communication during the weekend was slightly delayed, but answered thoroughly on Monday.", datetime.date(2025, 11, 27), "Astoria, Queens"),
            ("Arthur Pendelton", 4, "High price point, but the comprehensive genetic screening and 10-year warranty make it worth the investment.", datetime.date(2026, 1, 14), "Princeton, NJ"),
            ("Chloe & David Zimmerman", 4, "Great experience overall. Our Maltese settled in within 48 hours and passed his first local vet check with flying colors.", datetime.date(2026, 3, 29), "Battery Park City, NYC"),
            ("Reginald Foster", 4, "Solid, ethical pet placement. Microchip registration was processed quickly and customer service was polite.", datetime.date(2026, 5, 22), "Stamford, CT"),

            # 3-star reviews
            ("Franklin Morris", 3, "The puppy is healthy and wonderful, but scheduling a weekend private viewing required booking two weeks in advance due to high demand.", datetime.date(2025, 9, 5), "Morristown, NJ"),
            ("Helena Vance-Smith", 3, "Good experience and our Maltipoo is in great shape. The checkout simulator was a bit fast, but support clarified all steps promptly.", datetime.date(2026, 2, 18), "White Plains, NY"),
        ]

        # Clear existing reviews
        Review.objects.all().delete()
        from django.utils.text import slugify

        headline_templates = {
            5: [
                "Exceptional Nursery Care & Seamless Placement",
                "Pure Perfection & White Glove Dedication",
                "The Most Loving, Well-Socialized Companion",
                "Flawless Chaperoned Delivery & Impeccable Health",
                "Unmatched Transparency & Compassionate Breeders",
                "A Royal Experience From Consultation to Delivery",
            ],
            4: [
                "Delighted Adopters — Healthy & Loving Companion",
                "Exemplary Veterinary Care & Dedicated Support",
                "Wonderful Puppy With Calm, Confident Disposition",
                "High Professional Standards & Ethical Care",
            ],
            3: [
                "Very Healthy Puppy — Booking Process Was Busy",
                "Solid Experience With Genuine Care for the Animal",
            ]
        }

        for idx, (reviewer, rating, comment, rev_date, location) in enumerate(reviews_dataset):
            name_parts = reviewer.split(' ', 1)
            fname = name_parts[0]
            lname = name_parts[1] if len(name_parts) > 1 else ''
            uname = slugify(reviewer).replace('-', '_')[:30] + f"_{idx}"
            
            user, _ = User.objects.get_or_create(
                username=uname,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'email': f"{uname}@adopter.prestigepaws.nyc",
                    'role': 'customer',
                    'is_verified': True,
                }
            )

            headlines = headline_templates.get(rating, ["Wonderful Companion Placement"])
            headline = headlines[idx % len(headlines)]

            rev = Review.objects.create(
                customer=user,
                headline=headline,
                comment=comment,
                adopter_location=location,
                rating=rating,
                is_verified_purchase=True,
                status='approved',
            )
            # Update created_at to unique historical date
            dt = datetime.datetime.combine(rev_date, datetime.time(14, 30), tzinfo=datetime.timezone.utc)
            Review.objects.filter(id=rev.id).update(created_at=dt)

        self.stdout.write(self.style.SUCCESS(f"Successfully populated 4 coupons, Kitten category & breeds, 4 new Maltipoos, 4 new Maltese, 2 new Blogs, and {len(reviews_dataset)} unique reviews!"))
