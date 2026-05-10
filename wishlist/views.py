from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Product
from .models import WishlistItem
from django.contrib import messages

@login_required
def wishlist_detail(request):
    items = WishlistItem.objects.filter(user=request.user)
    return render(request, "wishlist/wishlist_detail.html", {"items": items})


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    WishlistItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect("wishlist:wishlist_detail")


@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    item.delete()

    return redirect("wishlist:wishlist_detail")


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    item = WishlistItem.objects.filter(
        user=request.user,
        product=product
    ).first()

    if item:
        item.delete()
        messages.success(request, "Produit retiré des favoris.")
    else:
        WishlistItem.objects.create(user=request.user, product=product)
        messages.success(request, "Produit ajouté aux favoris.")

    return redirect("catalog:product_detail", slug=product.slug)