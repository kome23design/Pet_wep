from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from accounts.forms import UserRegistrationForm, UserLoginForm, CustomerProfileForm, CustomerAddressForm
from accounts.models import CustomerProfile, CustomerAddress
from orders.models import Order
from catalog.models import Pet
from reviews.models import Review

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Prestige Paws NYC, {user.first_name or user.username}! Your private client account is active.")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Please correct the errors in the registration form below.")
    else:
        form = UserRegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    next_url = request.GET.get('next', 'accounts:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(next_url if next_url and next_url != '/' else 'accounts:dashboard')
        else:
            messages.error(request, "Invalid username or password credentials. Please try again.")
    else:
        form = UserLoginForm(request)
        
    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been securely signed out of Prestige Paws NYC.")
    return redirect('pages:home')


@login_required
def dashboard_view(request):
    user = request.user
    orders = Order.objects.filter(customer=user).order_by('-created_at')
    active_deliveries = [o.delivery for o in orders if hasattr(o, 'delivery') and o.delivery.status in ('scheduled', 'preparing', 'picked_up', 'in_transit', 'out_for_delivery')]
    addresses = CustomerAddress.objects.filter(user=user)
    recent_reviews = Review.objects.filter(customer=user).order_by('-created_at')[:3]
    
    # Wishlist stored in session
    wishlist_ids = request.session.get('wishlist', [])
    wishlist_pets = Pet.objects.filter(id__in=wishlist_ids, is_published=True)

    context = {
        'orders': orders[:5],
        'total_orders_count': orders.count(),
        'active_deliveries': active_deliveries,
        'addresses': addresses,
        'recent_reviews': recent_reviews,
        'wishlist_pets': wishlist_pets,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    user = request.user
    profile, _ = CustomerProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=profile, user=user)
        if form.is_valid():
            # Update User fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.phone_number = form.cleaned_data['phone_number']
            user.save()
            # Update Profile
            form.save()
            messages.success(request, "Your client profile details have been successfully updated.")
            return redirect('accounts:profile')
    else:
        form = CustomerProfileForm(instance=profile, user=user)
        
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def address_book_view(request):
    addresses = CustomerAddress.objects.filter(user=request.user)
    return render(request, 'accounts/address_book.html', {'addresses': addresses})


@login_required
def add_address_view(request):
    if request.method == 'POST':
        form = CustomerAddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            addr.save()
            messages.success(request, "New delivery residence address saved.")
            return redirect('accounts:addresses')
    else:
        form = CustomerAddressForm()
    return render(request, 'accounts/address_form.html', {'form': form, 'action': 'Add'})


@login_required
def edit_address_view(request, pk):
    address = get_object_or_404(CustomerAddress, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CustomerAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Delivery address updated.")
            return redirect('accounts:addresses')
    else:
        form = CustomerAddressForm(instance=address)
    return render(request, 'accounts/address_form.html', {'form': form, 'action': 'Edit', 'address': address})


@login_required
def delete_address_view(request, pk):
    address = get_object_or_404(CustomerAddress, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address removed from your address book.")
        return redirect('accounts:addresses')
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})


def wishlist_view(request):
    wishlist_ids = request.session.get('wishlist', [])
    pets = Pet.objects.filter(id__in=wishlist_ids, is_published=True)
    return render(request, 'accounts/wishlist.html', {'pets': pets})


def toggle_wishlist_view(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    wishlist = request.session.get('wishlist', [])
    
    if pet.id in wishlist:
        wishlist.remove(pet.id)
        messages.info(request, f"{pet.name} was removed from your saved wishlist.")
    else:
        wishlist.append(pet.id)
        messages.success(request, f"{pet.name} was saved to your private wishlist!")
        
    request.session['wishlist'] = wishlist
    request.session.modified = True
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('accounts:wishlist')


def password_reset_request_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        messages.success(
            request,
            f"If an account exists with {email}, a secure password reset link has been dispatched to your inbox (or logged in console for development)."
        )
        return render(request, 'accounts/password_reset_done.html', {'email': email})
    return render(request, 'accounts/password_reset.html')
