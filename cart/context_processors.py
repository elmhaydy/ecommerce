from .models import Cart


def cart_snapshot(request):
    if not request.user.is_authenticated:
        return {
            "header_cart": None,
            "header_cart_count": 0,
            "header_cart_items": [],
        }

    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = list(cart.items.select_related("product"))

    return {
        "header_cart": cart,
        "header_cart_count": cart.get_total_items(),
        "header_cart_items": items,
    }
