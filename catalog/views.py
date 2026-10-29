from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import date, timedelta
from catalog.models import PetCategory, PetBreed, Pet
from reviews.models import Review

def pet_list_view(request):
    pets = Pet.objects.filter(is_published=True).select_related('breed', 'category').prefetch_related('images')
    
    # Filter parameters
    category_slug = request.GET.get('category', '').strip()
    breed_slug = request.GET.get('breed', '').strip()
    lifestyle = request.GET.get('lifestyle', '').strip()
    age_stage = request.GET.get('age_stage', '').strip()
    sex = request.GET.get('sex', '').strip()
    status = request.GET.get('status', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort_by = request.GET.get('sort', '-is_featured').strip()
    
    active_category = None
    active_breed = None
    
    # Category Filter
    if category_slug:
        active_category = PetCategory.objects.filter(slug=category_slug).first()
        if active_category:
            pets = pets.filter(category=active_category)
        
    # Breed Filter
    if breed_slug:
        active_breed = PetBreed.objects.filter(slug=breed_slug).first()
        if active_breed:
            pets = pets.filter(breed=active_breed)
        
    # Gender Filter
    if sex in ('male', 'female'):
        pets = pets.filter(sex=sex)
        
    # Status Filter
    if status in ('available', 'reserved'):
        pets = pets.filter(status=status)
    else:
        # Default shows available first unless specified
        pass

    # Lifestyle & Activities Filter
    if lifestyle == 'hypoallergenic':
        pets = pets.filter(Q(breed__hypoallergenic=True) | Q(description__icontains='hypoallergenic'))
    elif lifestyle == 'apartment':
        pets = pets.filter(Q(expected_adult_size__icontains='Toy') | Q(breed__slug__in=['maltipoo', 'maltese']))
    elif lifestyle == 'family':
        pets = pets.filter(Q(description__icontains='gentle') | Q(description__icontains='sweet') | Q(description__icontains='affectionate') | Q(breed__temperament__icontains='gentle'))
    elif lifestyle == 'calm':
        pets = pets.filter(Q(description__icontains='calm') | Q(description__icontains='lap') | Q(description__icontains='sweet') | Q(breed__temperament__icontains='gentle'))
    elif lifestyle == 'playful':
        pets = pets.filter(Q(description__icontains='playful') | Q(description__icontains='lively') | Q(description__icontains='active') | Q(breed__temperament__icontains='intelligent'))

    # Age Stage Filter
    today = date.today()
    if age_stage == 'nursery':
        # Under 10 weeks
        cutoff = today - timedelta(days=70)
        pets = pets.filter(date_of_birth__gt=cutoff)
    elif age_stage == 'ready':
        # 10 to 16 weeks
        older_cutoff = today - timedelta(days=112)
        younger_cutoff = today - timedelta(days=70)
        pets = pets.filter(date_of_birth__gte=older_cutoff, date_of_birth__lte=younger_cutoff)
    elif age_stage == 'trained':
        # 16+ weeks
        cutoff = today - timedelta(days=112)
        pets = pets.filter(date_of_birth__lt=cutoff)

    # Price Range
    if min_price:
        try:
            pets = pets.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            pets = pets.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Sorting
    if sort_by == 'price_asc':
        pets = pets.order_by('price')
    elif sort_by == 'price_desc':
        pets = pets.order_by('-price')
    elif sort_by == 'newest':
        pets = pets.order_by('-created_at')
    elif sort_by == 'age':
        pets = pets.order_by('-date_of_birth')
    else:
        pets = pets.order_by('-is_featured', '-created_at')

    # Counts for sidebar filters
    all_published_pets = Pet.objects.filter(is_published=True)
    categories = PetCategory.objects.filter(is_active=True).annotate(
        pet_count=Count('pets', filter=Q(pets__is_published=True))
    )
    all_breeds = PetBreed.objects.filter(is_active=True).annotate(
        pet_count=Count('pets', filter=Q(pets__is_published=True))
    )

    # Lifestyle activity counts
    activity_counts = {
        'hypoallergenic': all_published_pets.filter(Q(breed__hypoallergenic=True) | Q(description__icontains='hypoallergenic')).count(),
        'apartment': all_published_pets.filter(Q(expected_adult_size__icontains='Toy') | Q(breed__slug__in=['maltipoo', 'maltese'])).count(),
        'family': all_published_pets.filter(Q(description__icontains='gentle') | Q(description__icontains='sweet') | Q(description__icontains='affectionate')).count(),
        'calm': all_published_pets.filter(Q(description__icontains='calm') | Q(description__icontains='lap') | Q(description__icontains='sweet')).count(),
        'playful': all_published_pets.filter(Q(description__icontains='playful') | Q(description__icontains='lively') | Q(description__icontains='active')).count(),
    }

    # Age stage counts
    age_counts = {
        'nursery': all_published_pets.filter(date_of_birth__gt=today - timedelta(days=70)).count(),
        'ready': all_published_pets.filter(date_of_birth__gte=today - timedelta(days=112), date_of_birth__lte=today - timedelta(days=70)).count(),
        'trained': all_published_pets.filter(date_of_birth__lt=today - timedelta(days=112)).count(),
    }

    # Pagination
    paginator = Paginator(pets, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Check if any filter is active
    has_active_filters = any([category_slug, breed_slug, lifestyle, age_stage, sex, min_price, max_price, status])

    context = {
        'page_obj': page_obj,
        'pets': page_obj.object_list,
        'categories': categories,
        'all_breeds': all_breeds,
        'active_category': active_category,
        'active_breed': active_breed,
        'current_category': category_slug,
        'current_breed': breed_slug,
        'current_lifestyle': lifestyle,
        'current_age_stage': age_stage,
        'current_sort': sort_by,
        'current_sex': sex,
        'current_status': status,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'has_active_filters': has_active_filters,
        'total_count': paginator.count,
        'total_atelier_count': all_published_pets.count(),
        'activity_counts': activity_counts,
        'age_counts': age_counts,
    }
    return render(request, 'catalog/pet_list.html', context)


def category_detail_view(request, category_slug):
    category = get_object_or_404(PetCategory, slug=category_slug, is_active=True)
    pets = Pet.objects.filter(category=category, is_published=True).select_related('breed').prefetch_related('images')
    
    breed_slug = request.GET.get('breed')
    if breed_slug:
        pets = pets.filter(breed__slug=breed_slug)
        
    paginator = Paginator(pets, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'pets': page_obj.object_list,
        'breeds': category.breeds.filter(is_active=True),
        'total_count': paginator.count,
    }
    return render(request, 'catalog/category_detail.html', context)


def breed_detail_view(request, category_slug=None, breed_slug=None):
    if not breed_slug and 'slug' in request.resolver_match.kwargs:
        breed_slug = request.resolver_match.kwargs['slug']
    if not breed_slug and 'breed_slug' in request.resolver_match.kwargs:
        breed_slug = request.resolver_match.kwargs['breed_slug']

    breed = get_object_or_404(PetBreed.objects.select_related('category'), slug=breed_slug, is_active=True)
    pets = Pet.objects.filter(breed=breed, is_published=True).prefetch_related('images')
    
    paginator = Paginator(pets, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # Fetch approved reviews for this breed
    reviews = Review.objects.filter(status='approved', breed=breed)[:4]
    
    context = {
        'breed': breed,
        'category': breed.category,
        'page_obj': page_obj,
        'pets': page_obj.object_list,
        'total_count': paginator.count,
        'reviews': reviews,
    }
    return render(request, 'catalog/breed_detail.html', context)


def collection_detail_view(request, slug):
    """
    Dedicated landing collections for Maltipoo and Maltese
    """
    return breed_detail_view(request, breed_slug=slug)


def pet_detail_view(request, slug):
    pet = get_object_or_404(
        Pet.objects.select_related('breed', 'category').prefetch_related('images', 'health_documents'),
        slug=slug
    )
    
    # Related companions from same breed or category
    related_pets = Pet.objects.filter(
        category=pet.category,
        is_published=True
    ).exclude(id=pet.id).select_related('breed').prefetch_related('images')[:3]
    
    reviews = Review.objects.filter(pet=pet, status='approved')
    if not reviews.exists():
        reviews = Review.objects.filter(breed=pet.breed, status='approved')[:3]

    context = {
        'pet': pet,
        'images': pet.images.all(),
        'related_pets': related_pets,
        'reviews': reviews,
    }
    return render(request, 'catalog/pet_detail.html', context)


def search_view(request):
    query = request.GET.get('q', '').strip()
    pets = Pet.objects.none()
    
    if query:
        pets = Pet.objects.filter(
            Q(name__icontains=query) |
            Q(reference_number__icontains=query) |
            Q(breed__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(coat_color__icontains=query) |
            Q(description__icontains=query),
            is_published=True
        ).select_related('breed', 'category').prefetch_related('images')
        
    paginator = Paginator(pets, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'query': query,
        'page_obj': page_obj,
        'pets': page_obj.object_list,
        'total_count': paginator.count,
    }
    return render(request, 'catalog/search_results.html', context)
