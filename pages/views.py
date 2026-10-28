from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from catalog.models import Pet, PetBreed, PetCategory
from reviews.models import Review
from pages.models import FAQ, GalleryItem, ContactInquiry, NewsletterSubscriber, BlogPost, BlogCategory

def home_view(request):
    featured_maltipoos = Pet.objects.filter(
        breed__slug='maltipoo',
        is_published=True,
        status='available'
    ).select_related('breed', 'category').prefetch_related('images')[:4]

    featured_maltese = Pet.objects.filter(
        breed__slug='maltese',
        is_published=True,
        status='available'
    ).select_related('breed', 'category').prefetch_related('images')[:4]

    recent_pets = Pet.objects.filter(
        is_published=True,
        status='available'
    ).select_related('breed', 'category').prefetch_related('images').order_by('-created_at')[:6]

    approved_reviews = Review.objects.filter(
        status='approved'
    ).select_related('customer', 'pet', 'breed').order_by('-created_at')[:3]

    faqs = FAQ.objects.filter(is_published=True).order_by('display_order')[:4]
    categories = PetCategory.objects.filter(is_active=True).prefetch_related('breeds')

    context = {
        'featured_maltipoos': featured_maltipoos,
        'featured_maltese': featured_maltese,
        'recent_pets': recent_pets,
        'approved_reviews': approved_reviews,
        'faqs': faqs,
        'categories': categories,
    }
    return render(request, 'pages/home.html', context)


def about_view(request):
    return render(request, 'pages/about.html')


def welfare_standards_view(request):
    return render(request, 'pages/animal_welfare.html')


def adoption_info_view(request):
    return render(request, 'pages/adoption_info.html')


def gallery_view(request):
    items = GalleryItem.objects.all().order_by('display_order', '-created_at')
    return render(request, 'pages/gallery.html', {'gallery_items': items})


def faq_view(request):
    categories = ['adoption', 'delivery', 'health', 'care']
    faq_groups = {}
    for cat in categories:
        qs = FAQ.objects.filter(category=cat, is_published=True).order_by('display_order')
        if qs.exists():
            faq_groups[dict(FAQ.CATEGORY_CHOICES).get(cat, cat)] = qs
    return render(request, 'pages/faq.html', {'faq_groups': faq_groups})


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', 'adoption_inquiry')
        pet_interest = request.POST.get('pet_interest', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            ContactInquiry.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                pet_interest=pet_interest,
                message=message,
            )
            messages.success(
                request,
                f"Thank you, {name}. Your inquiry has been delivered directly to our Manhattan Concierge Directorate. A private pet placement specialist will contact you shortly."
            )
            return redirect('pages:contact')
        else:
            messages.error(request, "Please fill in all required fields (Name, Email, Message).")

    return render(request, 'pages/contact.html')


def health_policy_view(request):
    return render(request, 'pages/health_policy.html')


def privacy_policy_view(request):
    return render(request, 'pages/privacy_policy.html')


def terms_policy_view(request):
    return render(request, 'pages/terms_policy.html')


def refund_policy_view(request):
    return render(request, 'pages/refund_policy.html')


def blog_list_view(request):
    posts = BlogPost.objects.filter(is_published=True).select_related('category')
    categories = BlogCategory.objects.annotate(post_count=Count('posts', filter=Q(posts__is_published=True)))

    active_category_slug = request.GET.get('category', '').strip()
    selected_category = None
    if active_category_slug:
        selected_category = get_object_or_404(BlogCategory, slug=active_category_slug)
        posts = posts.filter(category=selected_category)

    search_query = request.GET.get('q', '').strip()
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    featured_post = BlogPost.objects.filter(is_published=True, is_featured=True).first()
    recent_posts = BlogPost.objects.filter(is_published=True).exclude(id=featured_post.id if featured_post else None)[:4]

    paginator = Paginator(posts, 6)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'posts': page_obj.object_list,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'featured_post': featured_post,
        'recent_posts': recent_posts,
        'total_count': paginator.count,
    }
    return render(request, 'pages/blog_list.html', context)


def blog_detail_view(request, slug):
    post = get_object_or_404(BlogPost.objects.select_related('category'), slug=slug, is_published=True)
    related_posts = BlogPost.objects.filter(
        category=post.category,
        is_published=True
    ).exclude(id=post.id)[:3]

    if related_posts.count() < 3:
        fallback_posts = BlogPost.objects.filter(
            is_published=True
        ).exclude(id=post.id).exclude(id__in=[p.id for p in related_posts])[:3 - related_posts.count()]
        related_posts = list(related_posts) + list(fallback_posts)

    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'pages/blog_detail.html', context)


def newsletter_subscribe_api(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email and '@' in email:
            NewsletterSubscriber.objects.get_or_create(email=email, defaults={'is_active': True})
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Welcome to the Prestige Paws NYC private newsletter.'})
            messages.success(request, "Thank you for subscribing to our private VIP pet placement newsletter.")
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Invalid email address.'}, status=400)
            messages.error(request, "Please enter a valid email address.")
    return redirect(request.META.get('HTTP_REFERER', 'pages:home'))
