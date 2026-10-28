from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from reviews.models import Review
from reviews.forms import ReviewForm
from orders.models import OrderItem

def review_list_view(request):
    reviews = Review.objects.filter(status='approved').select_related('customer', 'pet', 'breed').order_by('-created_at')
    
    # Aggregates
    stats = reviews.aggregate(
        avg_rating=Avg('rating'),
        total_count=Count('id')
    )
    
    # Rating distribution
    distribution = {
        5: reviews.filter(rating=5).count(),
        4: reviews.filter(rating=4).count(),
        3: reviews.filter(rating=3).count(),
        2: reviews.filter(rating=2).count(),
        1: reviews.filter(rating=1).count(),
    }

    paginator = Paginator(reviews, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'reviews': page_obj.object_list,
        'page_obj': page_obj,
        'avg_rating': round(stats['avg_rating'] or 5.0, 1),
        'total_count': stats['total_count'] or 0,
        'distribution': distribution,
    }
    return render(request, 'reviews/review_list.html', context)


@login_required
def write_review_view(request):
    # Pre-select pet if pet_id passed
    pet_id = request.GET.get('pet_id')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, user=request.user)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.status = 'pending'  # Strictly requires moderator approval
            
            # Check for verified purchase
            if review.pet:
                is_verified = OrderItem.objects.filter(
                    order__customer=request.user,
                    order__payment_status='paid',
                    pet=review.pet
                ).exists()
                review.is_verified_purchase = is_verified
            else:
                # Any paid order makes the customer verified
                review.is_verified_purchase = request.user.orders.filter(payment_status='paid').exists()

            review.save()
            messages.success(
                request,
                "Thank you for sharing your experience! Your review has been safely submitted and is undergoing moderation before appearing on our verified client wall."
            )
            return redirect('reviews:review_list')
    else:
        initial = {}
        if pet_id:
            initial['pet'] = pet_id
        form = ReviewForm(initial=initial, user=request.user)

    return render(request, 'reviews/write_review.html', {'form': form})
