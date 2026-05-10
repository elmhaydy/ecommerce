from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from catalog.models import Product
from .models import Review


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    has_purchased = request.user.orders.filter(
        items__product=product,
        status__in=["PAID", "SHIPPED", "DELIVERED"]
    ).exists()

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        review, created = Review.objects.get_or_create(
            product=product,
            user=request.user,
            defaults={
                "rating": rating,
                "comment": comment,
                "is_verified_purchase": has_purchased,
            }
        )

        if not created:
            messages.warning(request, "Vous avez déjà laissé un avis pour ce produit.")
        else:
            messages.success(request, "Votre avis a été ajouté.")

    return redirect("catalog:product_detail", slug=product.slug)
