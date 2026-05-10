from catalog.models import Category, Product


def site_language(request):
    language = request.session.get("site_language", "fr")
    if language not in {"fr", "en"}:
        language = "fr"
    return {"site_language": language}


def search_snapshot(request):
    language = request.session.get("site_language", "fr")
    recommendations = Product.objects.filter(is_active=True).order_by("-created_at")[:10]
    trending_terms = [
        {"label_fr": "Watch", "label_en": "Watch"},
        {"label_fr": "Power bank", "label_en": "Power bank"},
        {"label_fr": "Tondeuse", "label_en": "Trimmer"},
        {"label_fr": "Casque", "label_en": "Headphones"},
        {"label_fr": "Aspirateur", "label_en": "Vacuum"},
    ]

    return {
        "header_search_recommendations": recommendations,
        "header_search_terms": trending_terms,
        "header_search_language": language,
    }


def header_mega_menu(request):
    language = request.session.get("site_language", "fr")
    categories = list(Category.objects.filter(is_active=True))

    def find_category(*names):
        lowered = {name.lower() for name in names}
        for category in categories:
            if (category.name_fr and category.name_fr.lower() in lowered) or (
                category.name_en and category.name_en.lower() in lowered
            ):
                return category
        return None

    menu_config = [
        {
            "label_fr": "Audio",
            "label_en": "Audio",
            "category": find_category("audio"),
        },
        {
            "label_fr": "Montre & Bureau",
            "label_en": "Smart & Office",
            "category": find_category("montre & bureau", "smart & office"),
        },
        {
            "label_fr": "Electromenager",
            "label_en": "Home Appliances",
            "category": find_category("électronique", "electronique", "home appliances"),
        },
        {
            "label_fr": "Soin personnel",
            "label_en": "Personal Care",
            "category": find_category("soin personnel", "personal care"),
        },
        {
            "label_fr": "Power",
            "label_en": "Power",
            "category": find_category("power"),
        },
    ]

    menu_items = []
    fallback_products = list(Product.objects.filter(is_active=True).order_by("-created_at")[:6])

    for item in menu_config:
        category = item["category"]
        if category:
            products = list(
                Product.objects.filter(is_active=True, category=category).order_by("-created_at")[:6]
            )
            slug = category.slug
        else:
            products = fallback_products
            slug = ""

        if not products:
            products = fallback_products

        display_name = item["label_en"] if language == "en" else item["label_fr"]

        menu_items.append({
            "label": display_name,
            "label_fr": item["label_fr"],
            "label_en": item["label_en"],
            "slug": slug,
            "category_name": category.name_en if language == "en" and category and category.name_en else (category.name_fr if category else display_name),
            "products": products,
        })

    return {
        "header_mega_menu_items": menu_items,
        "header_mega_menu_language": language,
    }
