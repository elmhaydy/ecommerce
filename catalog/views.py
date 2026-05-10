from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Product, Category


def product_list(request):
    language = request.session.get("site_language", "fr")
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    query = (request.GET.get("q") or "").strip()
    selected_categories = [slug for slug in request.GET.getlist("category") if slug]
    selected_colors = [color.strip().lower() for color in request.GET.getlist("color") if color.strip()]
    min_price = (request.GET.get("min_price") or "").strip()
    max_price = (request.GET.get("max_price") or "").strip()
    sort = (request.GET.get("sort") or "").strip()

    available_color_values = (
        Product.objects.filter(is_active=True)
        .exclude(colors="")
        .values_list("colors", flat=True)
    )
    color_order = ["noir", "blanc", "bleu", "rouge", "gris", "vert", "rose", "gold", "dore"]
    discovered_colors = set()
    for color_group in available_color_values:
        for color in color_group.split(","):
            normalized = color.strip().lower()
            if normalized:
                discovered_colors.add(normalized)

    ordered_discovered_colors = [
        color for color in color_order if color in discovered_colors
    ] + sorted(discovered_colors - set(color_order))

    color_labels_fr = {
        "noir": "Noir",
        "blanc": "Blanc",
        "bleu": "Bleu",
        "rouge": "Rouge",
        "gris": "Gris",
        "vert": "Vert",
        "rose": "Rose",
        "gold": "Gold",
        "dore": "Dore",
    }
    color_labels_en = {
        "noir": "Black",
        "blanc": "White",
        "bleu": "Blue",
        "rouge": "Red",
        "gris": "Gray",
        "vert": "Green",
        "rose": "Pink",
        "gold": "Gold",
        "dore": "Golden",
    }
    color_labels = color_labels_en if language == "en" else color_labels_fr
    color_swatches = {
        "noir": "#000000",
        "blanc": "#ffffff",
        "bleu": "#1d19ff",
        "rouge": "#ff1d1d",
        "gris": "#808080",
        "vert": "#4e9f3d",
        "rose": "#f6a6c9",
        "gold": "#c6a25a",
        "dore": "#c6a25a",
    }
    available_colors = [
        {
            "value": color,
            "label": color_labels.get(color, color.replace("-", " ").title()),
            "swatch": color_swatches.get(color, "#d6d6d6"),
        }
        for color in ordered_discovered_colors
    ]

    if query:
        products = products.filter(
            Q(name_fr__icontains=query)
            | Q(name_en__icontains=query)
            | Q(description_fr__icontains=query)
            | Q(description_en__icontains=query)
        )

    if selected_categories:
        products = products.filter(category__slug__in=selected_categories)

    if selected_colors:
        color_query = Q()
        for color in selected_colors:
            color_query |= Q(colors__icontains=color)
        products = products.filter(color_query).distinct()

    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except InvalidOperation:
            min_price = ""

    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except InvalidOperation:
            max_price = ""

    if sort == "price_asc":
        products = products.order_by("price", "-created_at")
    elif sort == "price_desc":
        products = products.order_by("-price", "-created_at")
    elif sort == "newest":
        products = products.order_by("-created_at", "-id")
    else:
        products = products.order_by("-is_featured", "-created_at", "-id")

    paginator = Paginator(products, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    query_params.pop("page", None)
    filter_query = query_params.urlencode()

    active_filter_pairs = []
    for key, values in request.GET.lists():
        if key in {"sort", "page"}:
            continue
        for value in values:
            active_filter_pairs.append((key, value))

    return render(request, "catalog/product_list.html", {
        "products": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "available_colors": available_colors,
        "selected_categories": selected_categories,
        "selected_colors": selected_colors,
        "min_price": min_price,
        "max_price": max_price,
        "query": query,
        "sort": sort,
        "active_filter_pairs": active_filter_pairs,
        "filter_query": filter_query,
    })

from django.db.models import Avg
from .models import Product


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    reviews = product.reviews.filter(is_approved=True).select_related("user")

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    average_rating = reviews.aggregate(avg=Avg("rating"))["avg"] or 0

    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = product.wishlist_items.filter(user=request.user).exists()

    return render(request, "catalog/product_detail.html", {
        "product": product,
        "reviews": reviews,
        "related_products": related_products,
        "average_rating": round(average_rating, 1),
        "is_in_wishlist": is_in_wishlist,
    })
