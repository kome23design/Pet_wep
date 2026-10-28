# Prestige Paws NYC &mdash; Luxury Pet Placement Atelier &amp; Chaperoned Companion Delivery

[![Django](https://img.shields.io/badge/Django-5.2-1B3B2B?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)
[![Stripe](https://img.shields.io/badge/Stripe-Card_Payments-635BFF?style=for-the-badge&logo=stripe)](https://stripe.com/)
[![Tests](https://img.shields.io/badge/Automated_Tests-23_Passed_100%25-brightgreen?style=for-the-badge)]()

**Prestige Paws NYC** is a production-ready, full-stack pet e-commerce platform and luxury placement atelier headquartered at **450 Lexington Avenue, Suite 1800, New York, NY 10017**. Designed specifically for high-trust companion pet adoption with nationwide chaperoned transport, the platform combines luxury aesthetics, database-level transactional concurrency locking, flight nanny coordination, an interactive faceted sidebar filter for breeds, lifestyle, and activities, an authoritative Canine Atelier Journal & Blog, Stripe payments with HMAC signature verification, a development payment sandbox simulator, customer review moderation queues, and an executive administration portal.

---

## 🏛️ System Architecture & App Structure

The codebase is organized into a modular Django architecture adhering to clean separation of concerns:

| Application | Core Responsibilities |
| :--- | :--- |
| **`core`** | Global settings, SEO routes (`robots.txt`, `sitemap.xml`), HTTP 404/500 error handlers, base context processors. |
| **`accounts`** | Custom `User` model with 4 distinct operational roles (`customer`, `staff`, `delivery_agent`, `admin`), address book CRUD, wishlist, and client profile. |
| **`catalog`** | Dynamic categories and breeds (admin expandable without code modifications), pet listings, USDA health credentials, age calculators, multifaceted sidebar filtering (categories, breeds, lifestyle, developmental stage, gender, price, concierge activities), search. |
| **`cart`** | Shopping cart lifecycle enforcing single-instance unique pet constraints (strict quantity = 1 per living pet). |
| **`orders`** | Concurrency-locked transactional checkout (`select_for_update`), order lifecycle tracking, printable PDF/HTML receipts, and automatic inventory restoration upon cancellation. |
| **`payments`** | Stripe Checkout integration, HMAC SHA-256 webhook signature verification, and a development payment sandbox simulator. |
| **`deliveries`** | Chaperoned companion hand-delivery dispatch models, flight nanny scheduling, milestone logistics, and courier dispatch management. |
| **`reviews`** | Verified adopter reviews, star ratings, moderation workflow queue, and verified purchase badge verification. |
| **`pages`** | Public information pages (Canine Atelier Journal & Blog, Animal Welfare Manifesto, 10-Year Health Warranty, First 72-Hours Adoption Masterguide, FAQ, Gallery, Contact Concierge, Legal Policies). |
| **`admin_dashboard`** | Executive custom administrative suite at `/portal/` featuring real-time financial metrics, inventory controls, order progression, review queues, and dispatch consoles. |

---

## 💎 Key Highlights & Differentiators

### 1. Dynamic Pet Category & Breed Inventory System with Faceted Sidebar
- Initialized with **Dogs** and signature breeds **Maltipoo** and **Maltese**.
- Administrators can dynamically register new categories (e.g., *Cats*, *Rabbits*, *Birds*) and breeds (e.g., *British Shorthair*, *Mini Lop*) directly from the management portal at `/portal/categories/add/` and `/portal/breeds/add/` **without requiring any code modifications or migrations**.
- **Integrated Sidebar Filter on "Shop All Puppies"**: Replaces cluttered navigation with an intuitive, unified sidebar allowing visitors to filter by:
  - **Dynamic Categories & Breeds** (with real-time item counts and hypoallergenic badges)
  - **Lifestyle & Activity Level** (Hypoallergenic, Apartment Friendly, Gentle Family, Calm Lap Companion, Playful & Energetic)
  - **Developmental Stage** (Nursery Pre-Reserve, Ready for Placement, Pre-Trained)
  - **Gender & Placement Price Range**
  - **Concierge Interactive Activities** (Private Manhattan Viewing, Geneticist Match, Flight Nanny Protocol, VIP Waitlist)

### 2. Double-Purchase Prevention via Database Concurrency Locking
- Because living pets are unique, individual beings, listings cannot be sold more than once.
- Checkout operations wrap order processing inside `transaction.atomic()` and execute `Pet.objects.select_for_update()` to lock the selected animal record at the database level during payment authorization.
- The listing immediately transitions from `available` &rarr; `reserved` &rarr; `sold`. If an order is subsequently cancelled, inventory status is atomically restored to `available`.

### 3. Nationwide Chaperoned Companion Delivery
- **Zero Cargo & Freight Policy**: All travel is strictly chaperoned in-cabin by trained flight nannies or in custom Mercedes-Benz Sprinter temperature-regulated vehicles.
- **Doorstep Handover Ceremony**: Includes microchip scanner verification, physical veterinary dossier transfer, 30-day transition nutrition kit, and initial health check.
- **Full 50-State Coverage**: Complete logistics coordination managed through dedicated concierge dossiers.

### 4. Resilient Payment Architecture
- **Stripe Hosted Checkout**: Redirects customers to Stripe's payment interface for PCI-compliant card processing.
- **Cryptographic Webhook Verification**: Standalone HMAC SHA-256 signature verification protects against replay attacks and forged webhook notifications.
- **Development Payment Sandbox Simulator**: Built-in test checkout sandbox allowing full end-to-end checkout, payment confirmation, and delivery initiation without requiring active external Stripe test credentials.

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.11, 3.12, or 3.13
- Git

### 1. Clone & Enter Project Directory
```bash
cd "c:\Users\EG\Desktop\Pet website"
```

### 2. Create and Activate Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables Configuration
Copy the sample environment file:
```bash
copy .env.example .env
```
*(On macOS/Linux: `cp .env.example .env`)*

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Populate Comprehensive Demonstration Data
Run the custom management command to initialize demonstration accounts, categories, breeds, puppies, health records, reviews, and an active in-transit delivery with live tracking:
```bash
python manage.py populate_demo_data
```

### 7. Run the Development Server
```bash
python manage.py runserver
```
Navigate your browser to `http://127.0.0.1:8000/`.

---

## 🔑 Pre-Configured Demonstration Accounts

| Role | Username | Password | Access Area |
| :--- | :--- | :--- | :--- |
| **Executive Admin** | `admin` | `AdminPass2026!` | Full access to `/portal/` and `/admin/` |
| **Atelier Staff** | `staff_lisa` | `StaffPass2026!` | Management portal `/portal/` |
| **Certified Courier** | `courier_dave` | `CourierPass2026!` | Courier GPS portal `/deliveries/courier/portal/` |
| **Verified Client** | `customer_sophie`| `CustomerPass2026!` | Customer dashboard `/accounts/dashboard/` |

---

## 🗺️ Complete Page Directory (All 35 Pages Implemented)

### Public Storefront & Collections
1. **Home Page** (`/`): 14 luxury sections including Hero, Featured Puppies, Category Cards, Welfare Pledge, Live Tracking Showcase, and FAQs.
2. **Shop All Puppies** (`/pets/`): Full catalog with price, breed, gender, and sorting filters.
3. **Dogs Category** (`/category/dogs/`): Dynamic category collection page.
4. **Maltipoo Collection** (`/collection/maltipoo/`): Dedicated hypoallergenic Maltipoo showcase.
5. **Maltese Collection** (`/collection/maltese/`): Dedicated purebred Maltese showcase.
6. **Dynamic Category Page** (`/category/<slug>/`): Renders any new animal category added via admin.
7. **Pet Details Page** (`/pet/<slug>/`): Medical records, 10-year warranty, microchip ID, and reserve CTA.
8. **Search Results** (`/search/?q=...`): Real-time keyword search across names, breeds, and traits.
9. **About Our Atelier** (`/about/`): Manhattan flagship story, ethics, and private viewing suite.
10. **Animal Welfare Standards** (`/animal-welfare-standards/`): Strict socialization and ethical breeding protocol.
11. **Adoption & Ownership Information** (`/adoption-ownership-info/`): Puppy preparation checklist and settling-in guide.
12. **Verified Client Reviews** (`/reviews/`): Star distribution, approved reviews, and verified badges.
13. **Puppy Portrait Gallery** (`/gallery/`): High-resolution imagery of placed and nursery companions.
14. **Frequently Asked Questions** (`/faq/`): Categorized questions with interactive accordions.
15. **Contact Concierge** (`/contact/`): Inquiry form for private viewing requests and travel logistics.
16. **Health & Documentation Policy** (`/health-documentation-policy/`): 10-Year Genetic Health Warranty details.
17. **Privacy Policy** (`/privacy-policy/`): Adherence to US privacy guidelines and customer data handling.
18. **Terms & Conditions** (`/terms-and-conditions/`): Placement covenant, terms, and conditions.
19. **Refund & Cancellation Policy** (`/refund-cancellation-policy/`): Deposit policies and welfare provisions.

### Commerce & Checkout
21. **Shopping Cart** (`/cart/`): Itemized summary, single-pet restrictions, delivery fee, and NYC sales tax.
22. **Checkout** (`/orders/checkout/`): Address validation, travel date picker, animal welfare acknowledgments.
23. **Order Confirmation** (`/orders/confirmation/<order_number>/`): Order receipt and direct tracking link.

### Customer Authentication & Management
24. **Client Login** (`/accounts/login/`): Secure session login with role redirection.
25. **Client Registration** (`/accounts/register/`): New account creation with immediate profile initialization.
26. **Password Reset Request** (`/accounts/password-reset/`): Email-based password reset workflow.
27. **Password Reset Done** (`/accounts/password-reset/done/`): Reset confirmation notice.
28. **Customer Dashboard** (`/accounts/dashboard/`): Overview of active adoptions, orders, and addresses.
29. **Order History** (`/orders/history/`): Complete historical list of all placements and orders.
30. **Individual Order Details** (`/orders/<order_number>/`): Detailed timeline, puppy dossier, and invoice receipt.
31. **Live Delivery Tracking** (`/deliveries/track/<tracking_number>/`): Interactive Leaflet map with 5s polling.
32. **Customer Profile** (`/accounts/profile/`): Experience level, contact details, and preferences.
33. **Address Book** (`/accounts/addresses/`): Multiple saved delivery destinations with default flag.
34. **Wishlist** (`/accounts/wishlist/`): One-click favorited companion puppies.
35. **Write a Review** (`/reviews/write/`): Customer review form with automated verified purchase detection.

### Error Handlers
- **404 Not Found** (`templates/core/404.html`)
- **500 Server Error** (`templates/core/500.html`)

---

## 🧪 Automated Test Suite

The test suite validates authentication, permissions, inventory behavior, transactional locking, cart rules, delivery GPS telemetry, and review moderation:

```bash
python manage.py test
```

### Test Coverage Highlights
- `accounts.tests.AccountsTestCase`: User roles, secure login/logout, address book CRUD, and unauthenticated redirects.
- `catalog.tests.CatalogTestCase`: Dynamic category/breed creation without code changes, publication filters, calculated age property, and search.
- `cart.tests.CartTestCase`: Single-pet quantity enforcement, duplicate add prevention, and cart subtotal calculation.
- `orders.tests.OrdersTestCase`: Transactional checkout, concurrency locking (`select_for_update`), and inventory restoration on cancellation.
- `deliveries.tests.DeliveriesTestCase`: Real-time telemetry JSON API, courier coordinate range validation (`-90 <= lat <= 90`, `-180 <= lon <= 180`), and unauthorized GPS update rejection.
- `reviews.tests.ReviewsTestCase`: Automatic verified purchase badge detection, pending moderation requirement, and public visibility filters.

---

## 🚢 Production Deployment Guide

### 1. Gunicorn Configuration
Run Gunicorn with multiple worker processes:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### 2. Static Assets with Whitenoise
Static assets are served via WhiteNoise with compression and unique hash caching:
```bash
python manage.py collectstatic --noinput
```

### 3. Production PostgreSQL Database
Configure `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgres://user:password@db-host:5432/prestigepaws_db
```

### 4. Security Checklist
Before launching in production, verify these settings in `.env`:
```env
DEBUG=False
DJANGO_SECRET_KEY="generate-a-strong-random-key"
ALLOWED_HOSTS="prestigepaws.nyc,www.prestigepaws.nyc"
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 📄 License & Disclaimer
This software is developed for **Prestige Paws NYC**. All demo animal photography, USDA license numbers, and sample addresses represent demonstration mock assets designed for testing and development.
