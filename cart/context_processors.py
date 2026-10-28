from cart.models import Cart

def cart_context(request):
    cart = None
    item_count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        elif request.session.session_key:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()
            
        if cart:
            item_count = cart.items.count()
    except Exception:
        pass

    return {
        'cart': cart,
        'cart_item_count': item_count,
    }
