from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from cart.models import Cart, CartItem
from catalog.models import Pet

def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # If there's an existing anonymous session cart, merge items into user cart
        if request.session.session_key:
            anon_cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if anon_cart and anon_cart != cart:
                for item in anon_cart.items.all():
                    if not cart.items.filter(pet=item.pet).exists():
                        item.cart = cart
                        item.save()
                    else:
                        item.delete()
                anon_cart.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def view_cart(request):
    cart = _get_or_create_cart(request)
    items = cart.items.select_related('pet', 'pet__breed', 'pet__category')
    
    # Check if any items are no longer available and warn customer
    unavailable_items = [i for i in items if not i.pet.is_purchasable]

    context = {
        'cart': cart,
        'items': items,
        'unavailable_items': unavailable_items,
    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, is_published=True)
    
    if not pet.is_purchasable:
        messages.error(request, f"We apologize, but {pet.name} is currently {pet.get_status_display().lower()} and cannot be reserved at this time.")
        return redirect('catalog:pet_detail', slug=pet.slug)
        
    cart = _get_or_create_cart(request)
    
    # Check if already in cart
    if cart.items.filter(pet=pet).exists():
        messages.info(request, f"{pet.name} is already in your reservation cart.")
        return redirect('cart:view_cart')
        
    # Since each animal is unique, check if another active cart has reserved it
    CartItem.objects.create(cart=cart, pet=pet)
    messages.success(request, f"{pet.name} ({pet.breed.name}) has been added to your reservation cart.")
    return redirect('cart:view_cart')


def remove_from_cart(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    pet_name = item.pet.name
    item.delete()
    messages.info(request, f"{pet_name} was removed from your reservation cart.")
    return redirect('cart:view_cart')
