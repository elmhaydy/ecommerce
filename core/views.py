import json
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q

from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from catalog.models import Category, Product
from .models import SupportConversation, SupportMessage


def _serialize_support_message(message, status):
    localized_created_at = timezone.localtime(message.created_at)
    return {
        "id": message.id,
        "body": message.body,
        "is_staff": message.is_staff,
        "created_at": localized_created_at.strftime("%H:%M"),
        "created_at_iso": localized_created_at.isoformat(),
        "status": status,
    }


def home(request):
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True,
    ).annotate(
        average_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
        review_count=Count("reviews", filter=Q(reviews__is_approved=True), distinct=True),
    )
    if not featured_products.exists():
        featured_products = Product.objects.filter(
            is_active=True
        ).annotate(
            average_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
            review_count=Count("reviews", filter=Q(reviews__is_approved=True), distinct=True),
        )

    categories = Category.objects.filter(is_active=True)[:6]
    new_arrivals = Product.objects.filter(is_active=True).order_by("-created_at")[:4]

    category_spotlights = []
    for category in categories:
        product = Product.objects.filter(is_active=True, category=category).first()
        if product:
            category_spotlights.append({
                "category": category,
                "product": product,
            })

    context = {
        "products": featured_products[:8],
        "new_arrivals": new_arrivals,
        "categories": categories,
        "category_spotlights": category_spotlights[:4],
    }
    return render(request, "core/home.html", context)


def set_language(request):
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    language = request.POST.get("language", "fr")
    if language in {"fr", "en"}:
        request.session["site_language"] = language
    return redirect(next_url)


def search_suggestions(request):
    language = request.session.get("site_language", "fr")
    query = (request.GET.get("q") or "").strip()

    if len(query) < 2:
        return JsonResponse({"query": query, "results": []})

    products = Product.objects.filter(
        is_active=True,
    ).filter(
        Q(name_fr__icontains=query)
        | Q(name_en__icontains=query)
        | Q(description_fr__icontains=query)
        | Q(description_en__icontains=query)
        | Q(category__name_fr__icontains=query)
        | Q(category__name_en__icontains=query)
    ).select_related("category")[:8]

    results = []
    for product in products:
        name = product.name_en if language == "en" and product.name_en else product.name_fr
        category_name = ""
        if product.category:
            category_name = (
                product.category.name_en
                if language == "en" and product.category.name_en
                else product.category.name_fr
            )

        results.append({
            "name": name,
            "category": category_name,
            "slug": product.slug,
            "url": reverse("catalog:product_detail", args=[product.slug]),
            "image_url": product.image.url if product.image else "",
            "price": f"{product.price:.2f}",
            "old_price": f"{product.old_price:.2f}" if product.old_price else "",
            "is_featured": product.is_featured,
        })

    return JsonResponse({"query": query, "results": results})


@login_required
def support_chat_status(request):
    conversation, _ = SupportConversation.objects.get_or_create(user=request.user)
    unread_count = conversation.unread_for_client
    return JsonResponse({
        "ok": True,
        "conversation_id": conversation.id,
        "unread_count": unread_count,
    })


@login_required
def support_chat_history(request):
    conversation, _ = SupportConversation.objects.get_or_create(user=request.user)
    visible_messages = conversation.messages.select_related("sender")
    if conversation.client_visible_from:
        visible_messages = visible_messages.filter(created_at__gte=conversation.client_visible_from)

    now = timezone.now()
    visible_messages.filter(is_staff=True, delivered_at__isnull=True).update(delivered_at=now)
    visible_messages.filter(is_staff=True, is_read=False).update(is_read=True, read_at=now)

    def message_status(message):
        if message.read_at:
            return "read"
        if message.delivered_at:
            return "delivered"
        return "sent"

    messages_payload = [
        _serialize_support_message(message, message_status(message))
        for message in visible_messages
    ]

    return JsonResponse({
        "ok": True,
        "conversation_id": conversation.id,
        "unread_count": 0,
        "messages": messages_payload,
    })


@login_required
def support_chat_send(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Method not allowed."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "message": "Invalid JSON payload."}, status=400)

    body = (payload.get("message") or "").strip()
    if not body:
        return JsonResponse({"ok": False, "message": "Empty message."}, status=400)

    conversation, _ = SupportConversation.objects.get_or_create(user=request.user)
    conversation.is_closed = False
    conversation.save(update_fields=["is_closed", "updated_at", "last_message_at"])

    support_message = SupportMessage.objects.create(
        conversation=conversation,
        sender=request.user,
        body=body,
        is_staff=False,
    )

    conversation.last_message_at = support_message.created_at
    conversation.save(update_fields=["last_message_at", "updated_at"])

    return JsonResponse({
        "ok": True,
        "message": _serialize_support_message(support_message, "sent"),
    })


def _footer_pages(language):
    is_en = language == "en"

    pages = {
        "about-us": {
            "title": "About Us" if is_en else "A propos de nous",
            "intro": (
                "Discover M&Y, our vision, and the way we build a modern shopping experience."
                if is_en else
                "Decouvrez M&Y, notre vision et la facon dont nous construisons une experience d'achat moderne."
            ),
            "sections": [
                {
                    "heading": "Who we are" if is_en else "Qui sommes-nous",
                    "body": (
                        "M&Y is an online store focused on audio, power, smart devices and home essentials, with a simple goal: offer reliable products with a cleaner customer experience."
                        if is_en else
                        "M&Y est une boutique en ligne orientee audio, power, objets connectes et essentiels de la maison, avec un objectif simple : proposer des produits fiables avec une experience client plus claire."
                    ),
                },
                {
                    "heading": "Our promise" if is_en else "Notre promesse",
                    "body": (
                        "We focus on curated products, transparent pricing, fast support and a checkout flow that stays easy from discovery to delivery."
                        if is_en else
                        "Nous misons sur une selection soignee, des prix transparents, une assistance rapide et un parcours d'achat simple du produit jusqu'a la livraison."
                    ),
                },
            ],
        },
        "affiliate-program": {
            "title": "Affiliate Program" if is_en else "Programme d'affiliation",
            "intro": (
                "Partner with M&Y and promote products that fit your audience."
                if is_en else
                "Travaillez avec M&Y et recommandez des produits adaptes a votre audience."
            ),
            "sections": [
                {
                    "heading": "How it works" if is_en else "Comment ca marche",
                    "body": (
                        "Affiliates share approved links to M&Y products and receive commissions on eligible sales generated through their channels."
                        if is_en else
                        "Les affilies partagent des liens approuves vers les produits M&Y et recoivent une commission sur les ventes eligibles generees par leurs canaux."
                    ),
                },
                {
                    "heading": "Apply" if is_en else "Candidater",
                    "body": (
                        "To join, contact our partnership team with your activity, traffic sources and audience profile."
                        if is_en else
                        "Pour rejoindre le programme, contactez notre equipe partenariat avec votre activite, vos sources de trafic et le profil de votre audience."
                    ),
                },
            ],
        },
        "where-to-buy": {
            "title": "Where to Buy" if is_en else "Ou acheter",
            "intro": (
                "Find the best way to shop M&Y products."
                if is_en else
                "Retrouvez la meilleure facon d'acheter les produits M&Y."
            ),
            "sections": [
                {
                    "heading": "Online store" if is_en else "Boutique en ligne",
                    "body": (
                        "You can order directly on our website for home delivery, order tracking and access to current promotions."
                        if is_en else
                        "Vous pouvez commander directement sur notre site pour profiter de la livraison a domicile, du suivi de commande et des promotions en cours."
                    ),
                },
                {
                    "heading": "Partner channels" if is_en else "Canaux partenaires",
                    "body": (
                        "Selected products may also be available through approved partner resellers depending on region and stock."
                        if is_en else
                        "Certaines references peuvent aussi etre disponibles via des revendeurs partenaires approuves selon la region et le stock."
                    ),
                },
            ],
        },
        "contact-us": {
            "title": "Contact Us" if is_en else "Contactez-nous",
            "intro": (
                "Reach our customer service team for orders, delivery, returns or product questions."
                if is_en else
                "Contactez notre service client pour vos commandes, la livraison, les retours ou les questions produit."
            ),
            "sections": [
                {
                    "heading": "Customer service" if is_en else "Service client",
                    "body": (
                        "Monday to Friday, 9:00 to 17:30. WhatsApp: 0660000000. Phone: 0665003521. Email: support@myshop.com."
                        if is_en else
                        "Du lundi au vendredi, de 9h00 a 17h30. WhatsApp : 0660000000. Telephone : 0665003521. Email : support@myshop.com."
                    ),
                },
                {
                    "heading": "Response time" if is_en else "Delai de reponse",
                    "body": (
                        "We aim to respond as quickly as possible during business hours, especially for active order support."
                        if is_en else
                        "Nous faisons le maximum pour repondre rapidement pendant les heures d'ouverture, en particulier pour les commandes en cours."
                    ),
                },
            ],
        },
        "points-program": {
            "title": "Points Program" if is_en else "Programme de points",
            "intro": (
                "Earn points through your customer journey and use them for future benefits."
                if is_en else
                "Cumulez des points tout au long de votre parcours client et profitez d'avantages sur vos prochaines commandes."
            ),
            "sections": [
                {
                    "heading": "Earning points" if is_en else "Comment gagner des points",
                    "body": (
                        "Points may be granted through purchases, campaigns or account activities depending on active promotional rules."
                        if is_en else
                        "Des points peuvent etre attribues via les achats, certaines campagnes ou des actions sur le compte selon les regles promotionnelles actives."
                    ),
                },
                {
                    "heading": "Using points" if is_en else "Utiliser les points",
                    "body": (
                        "Available points can be converted into benefits or discounts when eligible offers are active on your account."
                        if is_en else
                        "Les points disponibles peuvent etre transformes en avantages ou remises lorsque des offres eligibles sont actives sur votre compte."
                    ),
                },
            ],
        },
        "warranty": {
            "title": "Warranty" if is_en else "Garantie",
            "intro": (
                "Understand the warranty conditions applied to eligible M&Y products."
                if is_en else
                "Consultez les conditions de garantie appliquees aux produits M&Y eligibles."
            ),
            "sections": [
                {
                    "heading": "Coverage" if is_en else "Couverture",
                    "body": (
                        "Warranty terms depend on the product category, supplier conditions and proof of purchase."
                        if is_en else
                        "Les conditions de garantie dependent de la categorie du produit, des conditions fournisseur et de la preuve d'achat."
                    ),
                },
                {
                    "heading": "Request support" if is_en else "Demander une prise en charge",
                    "body": (
                        "Please contact customer service with your order number, product reference and a clear description of the issue."
                        if is_en else
                        "Merci de contacter le service client avec votre numero de commande, la reference produit et une description claire du probleme."
                    ),
                },
            ],
        },
        "shipping-delivery": {
            "title": "Shipping & Delivery" if is_en else "Expedition & Livraison",
            "intro": (
                "Learn how shipping fees, delivery timelines and service areas work."
                if is_en else
                "Consultez le fonctionnement des frais d'expedition, des delais de livraison et des zones desservies."
            ),
            "sections": [
                {
                    "heading": "Delivery timing" if is_en else "Delais de livraison",
                    "body": (
                        "Delivery timing depends on stock availability, destination city and the selected shipping method."
                        if is_en else
                        "Les delais de livraison dependent de la disponibilite du stock, de la ville de destination et du mode d'expedition selectionne."
                    ),
                },
                {
                    "heading": "Shipping fees" if is_en else "Frais d'expedition",
                    "body": (
                        "Shipping fees are calculated according to the delivery zone and may become free when a minimum threshold is reached."
                        if is_en else
                        "Les frais d'expedition sont calcules selon la zone de livraison et peuvent devenir gratuits a partir d'un certain seuil."
                    ),
                },
            ],
        },
        "return-policy": {
            "title": "Return Policy" if is_en else "Politique de retour",
            "intro": (
                "Check the return conditions before requesting a return."
                if is_en else
                "Consultez les conditions de retour avant d'initier une demande."
            ),
            "sections": [
                {
                    "heading": "Eligibility" if is_en else "Conditions d'eligibilite",
                    "body": (
                        "Returns may require the original packaging, proof of purchase and a product in acceptable condition."
                        if is_en else
                        "Les retours peuvent necessiter l'emballage d'origine, la preuve d'achat et un produit dans un etat acceptable."
                    ),
                },
                {
                    "heading": "How to request" if is_en else "Comment faire la demande",
                    "body": (
                        "Contact customer service first so we can guide you through the correct validation and return process."
                        if is_en else
                        "Contactez d'abord le service client afin que nous puissions vous orienter vers la bonne procedure de validation et de retour."
                    ),
                },
            ],
        },
        "terms-conditions": {
            "title": "Terms and Conditions" if is_en else "Termes et conditions",
            "intro": (
                "Review the general rules governing the use of the M&Y website and services."
                if is_en else
                "Consultez les regles generales qui encadrent l'utilisation du site et des services M&Y."
            ),
            "sections": [
                {
                    "heading": "Website usage" if is_en else "Utilisation du site",
                    "body": (
                        "By using the website, customers agree to provide accurate information and respect all purchase and account rules."
                        if is_en else
                        "En utilisant le site, les clients s'engagent a fournir des informations exactes et a respecter les regles liees aux achats et au compte."
                    ),
                },
                {
                    "heading": "Orders and pricing" if is_en else "Commandes et tarification",
                    "body": (
                        "Product availability, pricing and promotional conditions may change depending on stock, campaigns and operational constraints."
                        if is_en else
                        "La disponibilite des produits, les prix et les conditions promotionnelles peuvent evoluer selon le stock, les campagnes et les contraintes operationnelles."
                    ),
                },
            ],
        },
        "privacy-policy": {
            "title": "Privacy Policy" if is_en else "Politique de confidentialite",
            "intro": (
                "Learn how M&Y handles customer data across browsing, account creation and orders."
                if is_en else
                "Decouvrez comment M&Y traite les donnees clients pendant la navigation, la creation de compte et les commandes."
            ),
            "sections": [
                {
                    "heading": "Collected data" if is_en else "Donnees collectees",
                    "body": (
                        "We may collect account, order, contact and navigation data required to operate the store and improve service quality."
                        if is_en else
                        "Nous pouvons collecter des donnees de compte, de commande, de contact et de navigation necessaires au fonctionnement de la boutique et a l'amelioration du service."
                    ),
                },
                {
                    "heading": "Usage of data" if is_en else "Utilisation des donnees",
                    "body": (
                        "This data is used for order processing, customer support, security and service improvement within the limits of applicable rules."
                        if is_en else
                        "Ces donnees servent au traitement des commandes, au support client, a la securite et a l'amelioration du service dans les limites des regles applicables."
                    ),
                },
            ],
        },
    }

    return pages


def footer_page(request, slug):
    language = request.session.get("site_language", "fr")
    pages = _footer_pages(language)
    page = pages.get(slug)

    if not page:
        raise Http404("Footer page not found")

    return render(request, "core/footer_page.html", {"page": page})


def search_page(request):
    language = request.session.get("site_language", "fr")
    query = (request.GET.get("q") or "").strip()

    products = Product.objects.filter(is_active=True)
    if query:
        products = products.filter(
            Q(name_fr__icontains=query)
            | Q(name_en__icontains=query)
            | Q(description_fr__icontains=query)
            | Q(description_en__icontains=query)
            | Q(category__name_fr__icontains=query)
            | Q(category__name_en__icontains=query)
        )

    recommendations = Product.objects.filter(is_active=True).order_by("-created_at")[:10]
    trending_terms = [
        {"label_fr": "Watch", "label_en": "Watch"},
        {"label_fr": "Power bank", "label_en": "Power bank"},
        {"label_fr": "Tondeuse", "label_en": "Trimmer"},
        {"label_fr": "Casque", "label_en": "Headphones"},
        {"label_fr": "Aspirateur", "label_en": "Vacuum"},
    ]

    return render(request, "core/search.html", {
        "query": query,
        "results": products[:12],
        "results_count": products.count() if query else 0,
        "recommendations": recommendations,
        "trending_terms": trending_terms,
        "site_language": language,
    })
