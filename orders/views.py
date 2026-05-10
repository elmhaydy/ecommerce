from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from cart.models import Cart
from .models import Order, OrderItem
from django.contrib import messages
from django.contrib import messages
from django.shortcuts import get_object_or_404
from shipping.models import ShippingZone
from django.utils import timezone
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from cart.models import Cart
from catalog.models import Product
from shipping.models import ShippingZone
from .models import Order, OrderItem


@login_required
def checkout(request):
    if request.user.is_staff:
        messages.error(request, "Les administrateurs ne peuvent pas passer de commande.")
        return redirect("core:home")

    cart, created = Cart.objects.get_or_create(user=request.user)

    if not cart.items.exists():
        return redirect("cart:cart_detail")

    shipping_zones = ShippingZone.objects.filter(is_active=True)

    recommended_products = Product.objects.filter(
        is_active=True
    ).exclude(
        id__in=cart.items.values_list("product_id", flat=True)
    )[:6]

    selected_shipping_fee = 0

    if shipping_zones.exists():
        first_zone = shipping_zones.first()
        selected_shipping_fee = first_zone.fee

        if first_zone.free_shipping_threshold > 0 and cart.get_final_total() >= first_zone.free_shipping_threshold:
            selected_shipping_fee = 0

    checkout_total = cart.get_final_total() + selected_shipping_fee

    if request.method == "POST":
        for item in cart.items.select_related("product"):
            if item.quantity > item.product.stock:
                messages.error(
                    request,
                    f"Stock insuffisant pour {item.product.name_fr}. Stock disponible : {item.product.stock}"
                )
                return redirect("cart:cart_detail")

        shipping_zone = get_object_or_404(
            ShippingZone,
            id=request.POST.get("shipping_zone"),
            is_active=True
        )

        shipping_fee = shipping_zone.fee

        if shipping_zone.free_shipping_threshold > 0 and cart.get_final_total() >= shipping_zone.free_shipping_threshold:
            shipping_fee = 0

        final_total = cart.get_final_total() + shipping_fee

        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            postal_code=request.POST.get("postal_code"),
            city=shipping_zone.city,
            shipping_city=shipping_zone.city,
            shipping_fee=shipping_fee,
            total_amount=final_total,
            payment_method=request.POST.get("payment_method"),
        )

        for item in cart.items.select_related("product"):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity,
            )

            item.product.stock -= item.quantity
            item.product.save()

        if cart.coupon:
            cart.coupon.used_count += 1
            cart.coupon.save()

        cart.clear()

        messages.success(request, "Votre commande a été créée avec succès.")

        if order.payment_method == "CARD":
            return redirect("orders:payment_page", order_id=order.id)

        return redirect("orders:order_success", order_id=order.id)

    return render(request, "orders/checkout.html", {
        "cart": cart,
        "shipping_zones": shipping_zones,
        "recommended_products": recommended_products,
        "selected_shipping_fee": selected_shipping_fee,
        "checkout_total": checkout_total,
    })

@login_required
def order_success(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, "orders/order_success.html", {"order": order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/order_history.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status not in ["PENDING", "PAID"]:
        messages.error(request, "Cette commande ne peut plus être annulée.")
        return redirect("orders:order_detail", order_id=order.id)

    order.status = "CANCELLED"
    order.save()

    for item in order.items.all():
        if item.product:
            item.product.stock += item.quantity
            item.product.save()

    messages.success(request, "Commande annulée avec succès.")
    return redirect("orders:order_detail", order_id=order.id)

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.is_paid:
        messages.info(request, "Cette commande est déjà payée.")
        return redirect("orders:order_detail", order_id=order.id)

    if order.payment_method == "COD":
        messages.info(request, "Cette commande sera payée à la livraison.")
        return redirect("orders:order_detail", order_id=order.id)

    if request.method == "POST":
        order.is_paid = True
        order.paid_at = timezone.now()
        order.status = "PAID"
        order.save()

        messages.success(request, "Paiement simulé effectué avec succès.")
        return redirect("orders:order_success", order_id=order.id)

    return render(request, "orders/payment.html", {"order": order})
