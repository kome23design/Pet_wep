from django.core.management.base import BaseCommand
from pages.models import BlogCategory, BlogPost

class Command(BaseCommand):
    help = 'Populates the Canine Atelier Journal with rich articles and categories'

    def handle(self, *args, **options):
        self.stdout.write("Populating Canine Atelier Journal blog articles...")

        categories_data = [
            {
                'name': 'Canine Genetics & Allergies',
                'slug': 'canine-genetics-allergies',
                'description': 'Scientific analyses of coat genetics, dander protein reduction, and hypoallergenic dog profiles.'
            },
            {
                'name': 'Puppy Care & Transition',
                'slug': 'puppy-care-transition',
                'description': 'Practical, step-by-step guidance for bringing your new companion home smoothly.'
            },
            {
                'name': 'Behavior & Training',
                'slug': 'behavior-training',
                'description': 'Early socialization, positive reinforcement, and neurological development protocols.'
            },
            {
                'name': 'Health & Nutrition',
                'slug': 'health-nutrition',
                'description': 'Pediatric feeding advice, metabolic monitoring, and dietary blueprints for toy breeds.'
            },
            {
                'name': 'Veterinary Wellness',
                'slug': 'veterinary-wellness',
                'description': 'Vaccination schedules, veterinary exam preparation, and proactive preventative medicine.'
            },
        ]

        cat_map = {}
        for c in categories_data:
            cat, _ = BlogCategory.objects.get_or_create(
                slug=c['slug'],
                defaults={'name': c['name'], 'description': c['description']}
            )
            cat_map[c['slug']] = cat

        posts_data = [
            {
                'title': 'The Science of Hypoallergenic Dogs: Maltipoo & Maltese Biology Explained',
                'slug': 'science-of-hypoallergenic-dogs-maltipoo-maltese',
                'category': cat_map['canine-genetics-allergies'],
                'author': 'Dr. Eleanor Vance, DVM',
                'author_title': 'Chief Veterinary Officer & Geneticist',
                'read_time': '7 min read',
                'is_featured': True,
                'image_url': 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=1200&q=80',
                'excerpt': 'Why are Maltipoos and Maltese hailed as the ultimate apartment companions for allergy sufferers? An in-depth veterinary examination of Can f 1 protein secretion, hair vs. fur coat structure, and dander control protocols.',
                'tags': 'Hypoallergenic, Maltipoo, Maltese, Genetics, Dander, Apartment Living',
                'content': """
<h3 class="font-serif text-2xl font-bold text-forest mb-3">Understanding the Canine Allergen: It Is Never Just Hair</h3>
<p class="mb-4">One of the most persistent myths in companion animal care is that dog allergies are caused by animal hair itself. In clinical reality, human allergic reactions are triggered by specific glycoprotein molecules secreted primarily in a dog's saliva, sebaceous skin glands, and dander—most notably the <strong>Can f 1</strong> protein.</p>
<p class="mb-4">When dogs groom themselves, saliva coats their fur. As saliva evaporates, microscopic dander flakes carry the protein into indoor air currents. In double-coated shedding breeds (such as Golden Retrievers or German Shepherds), the undercoat constantly sheds, launching clouds of dander into the home environment.</p>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">The Single-Layer Hair Coat of the Purebred Maltese</h3>
<p class="mb-4">The purebred Maltese possesses a singular, luxurious single-layer coat that shares anatomical characteristics with human hair rather than traditional animal fur. Because the Maltese lacks an undercoat:</p>
<ul class="list-disc pl-6 space-y-2 text-stone-600 mb-4">
  <li><strong>Continuous Growth Cycle:</strong> Maltese hair grows continuously in an extended anagen phase, dramatically reducing dead coat turnover.</li>
  <li><strong>Trap-Free Dander:</strong> Dead hairs remain trapped lightly in the brush rather than shedding onto rugs, sofas, and draperies.</li>
  <li><strong>Reduced Sebum Production:</strong> Maltese skin produces a more delicate lipid barrier with demonstrably lower Can f 1 concentrations than sporting or working breeds.</li>
</ul>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">The Maltipoo Advantage: Poodle Hair Density Meets Maltese Softness</h3>
<p class="mb-4">When crossed with the miniature or toy Poodle—another non-shedding breed renowned for its tight curly single coat—the resulting Maltipoo inherits a low-to-zero shed fleece or wavy coat. Our multi-generational DNA testing screens specifically for the <em>furnishings</em> gene (F locus) and low-shed alleles to guarantee high predictability.</p>

<div class="my-6 p-6 bg-[#FAF8F5] rounded-2xl border border-stone-200">
  <h4 class="font-serif text-lg font-bold text-forest mb-2">Key Clinical Takeaways for Allergy-Sensitive Homes:</h4>
  <ol class="list-decimal pl-5 space-y-1.5 text-stone-700 text-xs sm:text-sm">
    <li>Bathe your puppy every 10–14 days using a veterinary hypoallergenic lipid-restoring oatmeal shampoo.</li>
    <li>Brush daily for 3 minutes to remove ambient dust and environmental pollens caught in the silky coat.</li>
    <li>Place a medical-grade True HEPA air purifier in the bedroom and main living salon.</li>
    <li>Wash plush puppy bedding weekly in hot water (130°F+) to neutralize lingering dander.</li>
  </ol>
</div>

<p>For sensitive New York families, Maltipoo and Maltese companions represent the gold standard in allergy-compatible companionship without compromising on personality or affectionate cuddles.</p>
"""
            },
            {
                'title': 'The First 72 Hours: A Step-by-Step Transition Blueprint for Your New Puppy',
                'slug': 'first-72-hours-new-puppy-transition-blueprint',
                'category': cat_map['puppy-care-transition'],
                'author': 'Chloe Davenport',
                'author_title': 'Lead Canine Behaviorist & Placement Director',
                'read_time': '6 min read',
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=1200&q=80',
                'excerpt': 'The initial three days in your home set the tone for lifelong emotional security. Learn our exact nursery protocol for scent blankets, first-night sleep setups, and preventing separation anxiety.',
                'tags': 'Puppy Preparation, First 72 Hours, Crate Training, Sleep Setup, Anxiety Prevention',
                'content': """
<h3 class="font-serif text-2xl font-bold text-forest mb-3">The Psychology of the First Day</h3>
<p class="mb-4">Entering a brand new environment with unfamiliar scents, acoustic echoes, and faces is the most momentous transition of your puppy's life. At Royal Maltipoos, every companion leaves the nursery accompanied by a mother-scented fleece blanket and heartbeat simulator to create an unbroken scent anchor.</p>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">Hour-by-Hour Timeline: Day 1 Arrival</h3>
<p class="mb-4">Follow this exact sequence the moment your puppy steps across your threshold:</p>
<ul class="list-disc pl-6 space-y-2 text-stone-600 mb-4">
  <li><strong>Immediate Potty Visit:</strong> Carry the puppy directly to your designated indoor grass patch or outdoor relief spot before showing them the rest of the home. Quietly praise success.</li>
  <li><strong>Quiet Exploration (One Room Only):</strong> Confine exploration to a single puppy-proofed zone (kitchen or nursery salon). Avoid sudden visits from excited neighbors or extended family on Day 1.</li>
  <li><strong>Hydration & Small Meal:</strong> Offer fresh, filtered room-temperature water alongside a measured portion of their nursery transition food. Do not change food brands today.</li>
  <li><strong>Rest Intervals:</strong> Puppies aged 8 to 14 weeks require 18 to 20 hours of restorative sleep per day. Expect your companion to play for 30 minutes, then require deep rest.</li>
</ul>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">Night 1: Mastering Crate Acclimation Without Distress</h3>
<p class="mb-4">Position the crate right beside your bed at eye level. Hearing your rhythmic breathing and knowing you are close prevents the primitive terror of abandonment. Wrap their heartbeat snuggle toy inside the mother's scent blanket.</p>

<div class="my-6 p-6 bg-forest/5 rounded-2xl border border-forest/15">
  <h4 class="font-bold text-forest text-sm mb-1">Night-Time Potty Protocol:</h4>
  <p class="text-xs text-stone-600 leading-relaxed">
    If your puppy whimpers around 2:00 AM or 5:00 AM, calmly take them to the relief area on leash without speaking, playing, or turning on bright lights. As soon as they finish, place them straight back into the crate. This teaches that night wakes are strictly functional, not recreational.
  </p>
</div>
"""
            },
            {
                'title': 'Early Neurological Stimulation (ENS): How We Build Confident, Resilient Companions',
                'slug': 'early-neurological-stimulation-ens-bio-sensor',
                'category': cat_map['behavior-training'],
                'author': 'Dr. Marcus Sterling, DVM',
                'author_title': 'Director of Pediatric Medicine',
                'read_time': '5 min read',
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?auto=format&fit=crop&w=1200&q=80',
                'excerpt': 'Discover the proven 5-step Bio Sensor tactile stimulation exercises practiced during days 3 to 16 that permanently enhance cardiovascular health, stress tolerance, and problem-solving capacity.',
                'tags': 'ENS, Bio Sensor, Neurodevelopment, Stress Resilience, Puppy Socialization',
                'content': """
<h3 class="font-serif text-2xl font-bold text-forest mb-3">What Is Early Neurological Stimulation?</h3>
<p class="mb-4">Developed originally by the United States Military's canine program (often known as the <em>Bio Sensor</em> program), Early Neurological Stimulation (ENS) comprises five specific physical handling exercises performed once daily between days 3 and 16 of life—a rapid window of critical neurological cell division.</p>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">The Five Core Daily Exercises</h3>
<ol class="list-decimal pl-6 space-y-2 text-stone-600 mb-4">
  <li><strong>Tactile Stimulation:</strong> Gently tickling the webbed skin between the puppy's toes using a sterile cotton swab for 3 to 5 seconds.</li>
  <li><strong>Head Held Erect:</strong> Supporting the puppy vertically so the head is pointing straight toward the ceiling for 3 to 5 seconds.</li>
  <li><strong>Head Pointed Downward:</strong> Supporting the torso while gently holding the head downward toward the floor for 3 to 5 seconds.</li>
  <li><strong>Supine Position:</strong> Resting the puppy on its back with all four paws pointing up for 3 to 5 seconds.</li>
  <li><strong>Thermal Stimulation:</strong> Placing the puppy feet-down upon a cool, damp cloth for 3 to 5 seconds before returning to maternal warmth.</li>
</ol>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">Clinically Documented Lifelong Benefits</h3>
<p class="mb-4">Decades of peer-reviewed comparative research demonstrate that puppies undergoing ENS exhibit:</p>
<ul class="list-disc pl-6 space-y-1.5 text-stone-600">
  <li>Stronger heart rates and greater cardiovascular performance under stress.</li>
  <li>Stronger adrenal glands and superior disease resistance.</li>
  <li>Dramatically reduced anxiety in bustling urban environments like Manhattan.</li>
  <li>Faster problem-solving capacity and heightened trainability as adults.</li>
</ul>
"""
            },
            {
                'title': 'Pediatric Nutrition Foundations: Feeding Toy & Miniature Breeds Safely',
                'slug': 'pediatric-nutrition-toy-miniature-breeds',
                'category': cat_map['health-nutrition'],
                'author': 'Dr. Eleanor Vance, DVM',
                'author_title': 'Chief Veterinary Officer',
                'read_time': '6 min read',
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1568640347023-a616a30bc3bd?auto=format&fit=crop&w=1200&q=80',
                'excerpt': 'Toy breeds have extraordinary metabolic rates and minimal glycogen storage. Learn how to prevent hypoglycemia, select nutrient-dense kibble, and calculate exact daily caloric requirements.',
                'tags': 'Nutrition, Hypoglycemia, Toy Breeds, Feeding Guide, Puppy Health',
                'content': """
<h3 class="font-serif text-2xl font-bold text-forest mb-3">The Unique Physiology of Toy Breeds</h3>
<p class="mb-4">A 3-pound Maltipoo puppy burns more calories per ounce of body weight than a 50-pound Labrador puppy. Because their immature livers cannot store large reserves of glycogen, missing a single meal or undergoing extended stress can precipitate a rapid drop in blood glucose—a condition known as <em>juvenile hypoglycemia</em>.</p>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">The 4-Meal Daily Feeding Schedule</h3>
<p class="mb-4">Between 8 and 16 weeks of age, never feed your toy puppy once or twice daily. Divide total daily caloric intake into four equal, scheduled meals:</p>
<ul class="list-disc pl-6 space-y-2 text-stone-600 mb-4">
  <li><strong>7:30 AM:</strong> Breakfast meal (high protein, rich in DHA).</li>
  <li><strong>12:30 PM:</strong> Midday nourishment.</li>
  <li><strong>5:30 PM:</strong> Early evening dinner.</li>
  <li><strong>9:30 PM:</strong> Bedtime snack (stabilizes glucose across the overnight sleep window).</li>
</ul>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">Recognizing & Treating Hypoglycemia</h3>
<p class="mb-4">Signs include disorientation, glazed eyes, lethargy, or weakness in the hind legs. If observed, immediately rub a nickel-sized dab of Nutri-Cal paste or pure maple syrup onto the puppy's gums. Within 5–10 minutes, glucose will absorb directly through the mucous membranes.</p>
"""
            },
            {
                'title': 'Apartment Living in NYC: Housebreaking & Etiquette in High-Rise Buildings',
                'slug': 'apartment-living-nyc-housebreaking-high-rise',
                'category': cat_map['puppy-care-transition'],
                'author': 'Chloe Davenport',
                'author_title': 'Lead Canine Behaviorist',
                'read_time': '5 min read',
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?auto=format&fit=crop&w=1200&q=80',
                'excerpt': 'Living on the 24th floor presents unique housebreaking challenges. Our comprehensive guide to real-grass indoor patches, elevator manners, sound desensitization, and neighborly balcony safety.',
                'tags': 'Apartment Living, NYC Puppies, Housebreaking, High Rise, Balcony Safety',
                'content': """
<h3 class="font-serif text-2xl font-bold text-forest mb-3">Navigating the Vertical Terrain of Manhattan</h3>
<p class="mb-4">When you live 20 floors above the sidewalk, sprinting outside every 90 minutes when a young puppy gives the signal is rarely realistic. Modern urban dog parenting requires an intelligent two-tiered system:</p>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">The Fresh Hydroponic Grass Patch</h3>
<p class="mb-4">Rather than confusing your puppy with absorbent textile pads (which teach puppies that soft bathroom rugs and bed quilts are acceptable relief surfaces), install a fresh hydroponic real-grass patch on your balcony or tiled bathroom area. Puppies instinctively gravitate toward genuine grass texture and scent.</p>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">Elevator & Lobby Etiquette</h3>
<p class="mb-4">Keep your puppy in your arms or a structured front-facing carrier while in the elevator until full immunity (16 weeks). This prevents accidental contamination from building pets and prevents nervous barking when doors open to new neighbors.</p>
"""
            },
            {
                'title': 'Canine Vaccination & Socialization Timelines: Balancing Immunity and Exposure',
                'slug': 'vaccination-socialization-timelines-canine-immunity',
                'category': cat_map['veterinary-wellness'],
                'author': 'Dr. Marcus Sterling, DVM',
                'author_title': 'Director of Pediatric Medicine',
                'read_time': '6 min read',
                'is_featured': False,
                'image_url': 'https://images.unsplash.com/photo-1601758228041-f3b2795255f1?auto=format&fit=crop&w=1200&q=80',
                'excerpt': 'The critical behavioral socialization window closes at 16 weeks, yet full parvo immunity requires the final booster. How to socialize your puppy safely using stroller walks and controlled playdates.',
                'tags': 'Vaccines, Socialization, Parvo Prevention, Veterinary Schedule, Puppy Health',
                'content': """
<h3 class="font-serif text-2xl font-bold text-forest mb-3">The Great Veterinary Dilemma</h3>
<p class="mb-4">Between 8 and 16 weeks of age, your puppy is in the golden developmental period for socialization—experiencing sirens, umbrella openings, skateboards, and varied human voices without lifelong fear. Simultaneously, maternal antibodies are declining, making exposure to infectious pathogens like parvovirus a genuine concern.</p>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">The Safe Stroller Socialization Strategy</h3>
<p class="mb-4">Never place your puppy on public sidewalks, dog parks, or pet store floors until 10 days after their 16-week booster. However, do not isolate them at home! Use a covered puppy stroller or carrier to walk through Central Park, outdoor cafe seating, and shopping avenues. Your companion receives 100% of the visual, auditory, and olfactory exposure while remaining completely insulated from ground pathogens.</p>

<h3 class="font-serif text-2xl font-bold text-forest mt-6 mb-3">Core Pediatric Vaccination Schedule</h3>
<ul class="list-disc pl-6 space-y-2 text-stone-600 mb-4">
  <li><strong>6–8 Weeks:</strong> First DHPP (Distemper, Hepatitis, Parainfluenza, Parvovirus) + deworming exam.</li>
  <li><strong>10–12 Weeks:</strong> Second DHPP + Leptospirosis first dose + Bordetella.</li>
  <li><strong>14–16 Weeks:</strong> Final DHPP booster + Rabies (1-year certificate) + microchip verification.</li>
</ul>
"""
            }
        ]

        for p in posts_data:
            obj, created = BlogPost.objects.update_or_create(
                slug=p['slug'],
                defaults=p
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"[{status}] Blog Post: {obj.title}")

        self.stdout.write(self.style.SUCCESS(f"Blog population complete! Total articles in database: {BlogPost.objects.count()}"))
