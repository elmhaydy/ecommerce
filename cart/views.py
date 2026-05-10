from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from catalog.models import Product
from .models import Cart, CartItem
from coupons.models import Coupon


def _is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _redirect_back(request, fallback):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect(fallback)


def _serialize_cart(cart):
    items = []
    for item in cart.items.select_related("product"):
        items.append({
            "id": item.id,
            "product_name": item.product.name_fr,
            "product_slug": item.product.slug,
            "product_url": reverse("catalog:product_detail", args=[item.product.slug]),
            "image_url": item.product.image.url if item.product.image else "",
            "quantity": item.quantity,
            "price": str(item.product.price),
            "old_price": str(item.product.old_price) if item.product.old_price else "",
            "subtotal": str(item.get_subtotal()),
        })

    return {
        "count": cart.get_total_items(),
        "total": str(cart.get_total()),
        "items": items,
    }

from django.shortcuts import render
from catalog.models import Product


def cart_detail(request):
    cart = request.user.cart

    related_products = Product.objects.filter(
        is_active=True
    ).order_by("-created_at")[:4]

    return render(request, "cart/cart_detail.html", {
        "cart": cart,
        "related_products": related_products,
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity_raw = request.POST.get("quantity", "1") if request.method == "POST" else "1"

    try:
        quantity = max(int(quantity_raw), 1)
    except (TypeError, ValueError):
        quantity = 1

    if request.user.is_staff:
        if _is_ajax(request):
            return JsonResponse({"success": False, "message": "Les administrateurs ne peuvent pas utiliser le panier."}, status=403)
        messages.error(request, "Les administrateurs ne peuvent pas utiliser le panier.")
        return redirect("catalog:product_detail", slug=product.slug)

    if product.stock <= 0:
        if _is_ajax(request):
            return JsonResponse({"success": False, "message": "Ce produit est en rupture de stock."}, status=400)
        messages.error(request, "Ce produit est en rupture de stock.")
        return redirect("catalog:product_detail", slug=product.slug)

    cart, created = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        if item.quantity + quantity > product.stock:
            if _is_ajax(request):
                return JsonResponse({"success": False, "message": "Stock insuffisant."}, status=400)
            messages.error(request, "Stock insuffisant.")
            return redirect("cart:cart_detail")
        item.quantity += quantity
    else:
        item.quantity = quantity
        if item.quantity > product.stock:
            if _is_ajax(request):
                return JsonResponse({"success": False, "message": "Stock insuffisant."}, status=400)
            messages.error(request, "Stock insuffisant.")
            return redirect("catalog:product_detail", slug=product.slug)

    item.save()

    if _is_ajax(request):
        return JsonResponse({
            "success": True,
            "cart": _serialize_cart(cart),
        })

    return _redirect_back(request, "cart:cart_detail")


@login_required
def remove_from_cart(request, item_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()

    if _is_ajax(request):
        return JsonResponse({
            "success": True,
            "cart": _serialize_cart(cart),
        })

    return _redirect_back(request, "cart:cart_detail")

@login_required
def update_cart_item(request, item_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    action = request.POST.get("action")

    if action == "increase":
        if item.quantity + 1 > item.product.stock:
            messages.error(request, "Stock insuffisant.")
        else:
            item.quantity += 1
            item.save()

    elif action == "decrease":
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    if _is_ajax(request):
        return JsonResponse({
            "success": True,
            "cart": _serialize_cart(cart),
        })

    return _redirect_back(request, "cart:cart_detail")

@login_required
def apply_coupon(request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    if request.method == "POST":
        code = request.POST.get("code")

        try:
            coupon = Coupon.objects.get(code__iexact=code)

            if not coupon.is_valid():
                messages.error(request, "Coupon invalide ou expiré.")
            elif cart.get_total() < coupon.min_order_amount:
                messages.error(request, "Montant minimum non atteint pour ce coupon.")
            else:
                cart.coupon = coupon
                cart.save()
                messages.success(request, "Coupon appliqué avec succès.")

        except Coupon.DoesNotExist:
            messages.error(request, "Coupon introuvable.")

    return _redirect_back(request, "cart:cart_detail")


@login_required
def remove_coupon(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.coupon = None
    cart.save()
    messages.success(request, "Coupon retiré.")
    return _redirect_back(request, "cart:cart_detail")



@login_required
def toggle_cart_product(request, product_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    item = CartItem.objects.filter(cart=cart, product=product).first()

    if item:
        item.delete()
        messages.success(request, "Produit retiré du panier.")
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        messages.success(request, "Produit ajouté au panier.")

    return _redirect_back(request, "orders:checkout")