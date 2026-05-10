from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import Group, User
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from catalog.models import Category, Product
from core.models import SupportConversation, SupportMessage
from coupons.models import Coupon
from orders.models import Order, OrderItem
from reviews.models import Review
from shipping.models import ShippingZone

from .decorators import group_required
from .forms import (
    AdminUserCreateForm,
    AdminSelfUpdateForm,
    AdminUserUpdateForm,
    CategoryForm,
    CouponForm,
    ProductForm,
    ShippingZoneForm,
)


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def dashboard_home(request):
    today = timezone.localdate()
    valid_orders_qs = Order.objects.exclude(status="CANCELLED")
    paid_orders_qs = Order.objects.filter(is_paid=True)
    recent_days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]

    daily_sales_rows = (
        valid_orders_qs.filter(created_at__date__gte=recent_days[0], created_at__date__lte=today)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("total_amount"))
        .order_by("day")
    )
    daily_sales_map = {row["day"]: float(row["total"] or 0) for row in daily_sales_rows}

    sales_chart = {
        "labels": [day.strftime("%d/%m") for day in recent_days],
        "values": [daily_sales_map.get(day, 0) for day in recent_days],
    }

    order_status_chart = {
        "labels": ["En attente", "Payées", "Expédiées", "Livrées", "Annulées"],
        "values": [
            Order.objects.filter(status="PENDING").count(),
            Order.objects.filter(status="PAID").count(),
            Order.objects.filter(status="SHIPPED").count(),
            Order.objects.filter(status="DELIVERED").count(),
            Order.objects.filter(status="CANCELLED").count(),
        ],
    }

    context = {
        "total_sales": valid_orders_qs.aggregate(total=Sum("total_amount"))["total"] or 0,
        "today_sales": valid_orders_qs.filter(created_at__date=today).aggregate(
            total=Sum("total_amount")
        )["total"] or 0,
        "total_products": Product.objects.count(),
        "total_categories": Category.objects.count(),
        "total_orders": Order.objects.count(),
        "total_users": User.objects.count(),
        "paid_orders_count": paid_orders_qs.count(),
        "today_orders_count": valid_orders_qs.filter(created_at__date=today).count(),
        "pending_orders": Order.objects.filter(status="PENDING").count(),
        "delivered_orders": Order.objects.filter(status="DELIVERED").count(),
        "latest_orders": Order.objects.select_related("user").order_by("-created_at")[:5],
        "low_stock_products": Product.objects.filter(
            stock__lte=F("low_stock_threshold")
        ).order_by("stock")[:5],
        "dashboard_chart_data": {
            "sales": sales_chart,
            "orders": order_status_chart,
        },
    }
    return render(request, "admin_panel/dashboard.html", context)


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def product_list_admin(request):
    products = Product.objects.all().order_by("-created_at")
    return render(request, "admin_panel/product/list.html", {"products": products})


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Produit ajouté avec succès.")
            return redirect("admin_panel:product_list")
    else:
        form = ProductForm()

    return render(request, "admin_panel/product/form.html", {"form": form})


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès.")
            return redirect("admin_panel:product_list")
    else:
        form = ProductForm(instance=product)

    return render(request, "admin_panel/product/form.html", {
        "form": form,
        "product": product,
    })


@staff_member_required
@group_required("SUPER_ADMIN")
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Produit supprimé avec succès.")
        return redirect("admin_panel:product_list")

    return render(request, "admin_panel/product/confirm_delete.html", {
        "object": product,
        "type": "Produit"
    })


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def category_list(request):
    categories = Category.objects.annotate(products_count=Count("products")).order_by("name_fr")
    return render(request, "admin_panel/caterory/list.html", {
        "categories": categories
    })


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée avec succès.")
            return redirect("admin_panel:category_list")
    else:
        form = CategoryForm()

    return render(request, "admin_panel/caterory/form.html", {"form": form})


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def category_update(request, category_id):
    category = get_object_or_404(
        Category.objects.annotate(products_count=Count("products")),
        id=category_id,
    )

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie modifiée avec succès.")
            return redirect("admin_panel:category_list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "admin_panel/caterory/form.html", {
        "form": form,
        "category": category,
    })


@staff_member_required
@group_required("SUPER_ADMIN")
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.delete()
        messages.success(request, "Catégorie supprimée avec succès.")
        return redirect("admin_panel:category_list")

    return render(request, "admin_panel/caterory/confirm_delete.html", {
        "object": category,
        "type": "Catégorie"
    })


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER", "PREPARATEUR", "SUPPORT")
def order_list_admin(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "admin_panel/order/list.html", {
        "orders": orders
    })


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER", "PREPARATEUR", "SUPPORT")
def order_detail_admin(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin_panel/order/detail.html", {
        "order": order
    })


@staff_member_required
@group_required("SUPER_ADMIN", "SUPPORT")
def support_conversation_list_data_admin(request):
    conversations = SupportConversation.objects.select_related("user").prefetch_related("messages")
    payload = [
        {
            "id": conversation.id,
            "username": conversation.user.username,
            "email": conversation.user.email or "Sans email",
            "unread_for_support": conversation.unread_for_support,
            "last_message": (
                conversation.messages.last().body[:70]
                if conversation.messages.last()
                else "Aucun message"
            ),
            "is_closed": conversation.is_closed,
            "url": request.build_absolute_uri(
                request.path.replace("/data/", f"/{conversation.id}/")
            ),
        }
        for conversation in conversations
    ]

    return JsonResponse({
        "ok": True,
        "count": len(payload),
        "conversations": payload,
    })


@staff_member_required
@group_required("SUPER_ADMIN", "SUPPORT")
def support_conversation_list_admin(request):
    SupportMessage.objects.filter(is_staff=False, delivered_at__isnull=True).update(delivered_at=timezone.now())
    conversations = SupportConversation.objects.select_related("user").prefetch_related("messages")
    selected_conversation = conversations.first()

    return render(request, "admin_panel/support/list.html", {
        "conversations": conversations,
        "selected_conversation": selected_conversation,
    })


@staff_member_required
@group_required("SUPER_ADMIN", "SUPPORT")
def support_conversation_detail_admin(request, conversation_id):
    conversations = SupportConversation.objects.select_related("user").prefetch_related("messages")
    selected_conversation = get_object_or_404(
        SupportConversation.objects.select_related("user").prefetch_related("messages__sender"),
        id=conversation_id,
    )
    now = timezone.now()
    selected_conversation.messages.filter(is_staff=False, delivered_at__isnull=True).update(delivered_at=now)
    selected_conversation.messages.filter(is_staff=False, is_read=False).update(is_read=True, read_at=now)

    return render(request, "admin_panel/support/list.html", {
        "conversations": conversations,
        "selected_conversation": selected_conversation,
    })


@staff_member_required
@group_required("SUPER_ADMIN", "SUPPORT")
def support_conversation_messages_admin(request, conversation_id):
    conversation = get_object_or_404(
        SupportConversation.objects.select_related("user").prefetch_related("messages__sender"),
        id=conversation_id,
    )
    now = timezone.now()
    conversation.messages.filter(is_staff=False, delivered_at__isnull=True).update(delivered_at=now)
    conversation.messages.filter(is_staff=False, is_read=False).update(is_read=True, read_at=now)

    def message_status(message):
        if message.read_at:
            return "read"
        if message.delivered_at:
            return "delivered"
        return "sent"

    messages_payload = [
        {
            "id": message.id,
            "body": message.body,
            "is_staff": message.is_staff,
            "sender": "Support" if message.is_staff else message.sender.username,
            "created_at": message.created_at.strftime("%d/%m/%Y %H:%M"),
            "status": message_status(message) if message.is_staff else "",
        }
        for message in conversation.messages.all()
    ]

    return JsonResponse({
        "ok": True,
        "conversation_id": conversation.id,
        "is_closed": conversation.is_closed,
        "messages": messages_payload,
        "unread_for_support": conversation.unread_for_support,
    })


@staff_member_required
@group_required("SUPER_ADMIN", "SUPPORT")
def support_conversation_reply_admin(request, conversation_id):
    conversation = get_object_or_404(SupportConversation, id=conversation_id)

    if request.method == "POST":
        body = (request.POST.get("body") or "").strip()
        if body:
            message = SupportMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                body=body,
                is_staff=True,
                is_read=False,
            )
            conversation.is_closed = False
            conversation.last_message_at = message.created_at
            conversation.save(update_fields=["is_closed", "last_message_at", "updated_at"])
            messages.success(request, "Reponse envoyee au client.")
        else:
            messages.error(request, "Le message est vide.")

    return redirect("admin_panel:support_conversation_detail", conversation_id=conversation.id)


@staff_member_required
@group_required("SUPER_ADMIN", "SUPPORT")
def support_conversation_close_admin(request, conversation_id):
    conversation = get_object_or_404(SupportConversation, id=conversation_id)
    conversation.is_closed = True
    conversation.client_visible_from = timezone.now()
    conversation.messages.filter(is_staff=True, is_read=False).update(is_read=True)
    conversation.save(update_fields=["is_closed", "client_visible_from", "updated_at"])
    messages.success(request, "Conversation marquee comme fermee.")
    return redirect("admin_panel:support_conversation_detail", conversation_id=conversation.id)


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER", "PREPARATEUR")
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")

        valid_statuses = ["PENDING", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"]

        if new_status in valid_statuses:
            order.status = new_status
            order.save()

            if new_status == "DELIVERED":
                messages.success(request, f"La commande #{order.id} est marquée comme livrée.")
            elif new_status == "SHIPPED":
                messages.success(request, f"La commande #{order.id} est expédiée.")
            else:
                messages.success(request, "Statut de la commande mis à jour.")
        else:
            messages.error(request, "Statut invalide.")

    return redirect("admin_panel:home")


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, "admin_panel/coupon/list.html", {
        "coupons": coupons
    })


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def coupon_create(request):
    if request.method == "POST":
        form = CouponForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Coupon ajouté avec succès.")
            return redirect("admin_panel:coupon_list")
    else:
        form = CouponForm()

    return render(request, "admin_panel/coupon/form.html", {
        "form": form
    })


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def coupon_update(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)

    if request.method == "POST":
        form = CouponForm(request.POST, instance=coupon)

        if form.is_valid():
            form.save()
            messages.success(request, "Coupon modifié avec succès.")
            return redirect("admin_panel:coupon_list")
    else:
        form = CouponForm(instance=coupon)

    return render(request, "admin_panel/coupon/form.html", {
        "form": form,
        "coupon": coupon
    })


@staff_member_required
@group_required("SUPER_ADMIN")
def coupon_delete(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)

    if request.method == "POST":
        coupon.delete()
        messages.success(request, "Coupon supprimé avec succès.")
        return redirect("admin_panel:coupon_list")

    return render(request, "admin_panel/coupon/confirm_delete.html", {
        "coupon": coupon
    })


@staff_member_required
def order_invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="facture_commande_{order.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50

    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, y, "Facture - E-commerce")
    y -= 40

    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Commande N° : {order.id}")
    y -= 20
    p.drawString(50, y, f"Date : {order.created_at.strftime('%d/%m/%Y %H:%M')}")
    y -= 20
    p.drawString(50, y, f"Client : {order.first_name} {order.last_name}")
    y -= 20
    p.drawString(50, y, f"Email : {order.email}")
    y -= 20
    p.drawString(50, y, f"Téléphone : {order.phone}")
    y -= 20
    p.drawString(50, y, f"Adresse : {order.address}, {order.city}, {order.postal_code}")
    y -= 40

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Produit")
    p.drawString(300, y, "Qté")
    p.drawString(360, y, "Prix")
    p.drawString(450, y, "Sous-total")
    y -= 20

    p.setFont("Helvetica", 10)

    for item in order.items.all():
        product_name = item.product.name_fr if item.product else "Produit supprimé"

        p.drawString(50, y, product_name[:35])
        p.drawString(300, y, str(item.quantity))
        p.drawString(360, y, f"{item.price} DH")
        p.drawString(450, y, f"{item.get_subtotal()} DH")
        y -= 20

        if y < 80:
            p.showPage()
            y = height - 50

    y -= 20
    p.setFont("Helvetica-Bold", 13)
    p.drawString(360, y, f"Total : {order.total_amount} DH")

    y -= 50
    p.setFont("Helvetica", 10)
    p.drawString(50, y, "Merci pour votre achat.")

    p.showPage()
    p.save()

    return response


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def shipping_list(request):
    zones = ShippingZone.objects.all().order_by("city")
    return render(request, "admin_panel/shipping/list.html", {"zones": zones})


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def shipping_create(request):
    if request.method == "POST":
        form = ShippingZoneForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Zone de livraison ajoutée.")
            return redirect("admin_panel:shipping_list")
    else:
        form = ShippingZoneForm()

    return render(request, "admin_panel/shipping/form.html", {"form": form})


@staff_member_required
@group_required("SUPER_ADMIN", "MANAGER")
def shipping_update(request, zone_id):
    zone = get_object_or_404(ShippingZone, id=zone_id)

    if request.method == "POST":
        form = ShippingZoneForm(request.POST, instance=zone)
        if form.is_valid():
            form.save()
            messages.success(request, "Zone de livraison modifiée.")
            return redirect("admin_panel:shipping_list")
    else:
        form = ShippingZoneForm(instance=zone)

    return render(request, "admin_panel/shipping/form.html", {
        "form": form,
        "zone": zone,
    })


@staff_member_required
@group_required("SUPER_ADMIN")
def shipping_delete(request, zone_id):
    zone = get_object_or_404(ShippingZone, id=zone_id)

    if request.method == "POST":
        zone.delete()
        messages.success(request, "Zone de livraison supprimée.")
        return redirect("admin_panel:shipping_list")

    return render(request, "admin_panel/shipping/confirm_delete.html", {"zone": zone})


@staff_member_required
@group_required("SUPER_ADMIN", "SUPPORT")
def user_list_admin(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "admin_panel/user/list.html", {
        "users": users
    })


@staff_member_required
@group_required("SUPER_ADMIN")
def user_toggle_active(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect("admin_panel:user_list")

    user.is_active = not user.is_active
    user.save()

    if user.is_active:
        messages.success(request, "Utilisateur activé avec succès.")
    else:
        messages.success(request, "Utilisateur désactivé avec succès.")

    return redirect("admin_panel:user_list")


@staff_member_required
@group_required("SUPER_ADMIN", "SUPPORT")
def user_detail_admin(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    orders = user_obj.orders.all().order_by("-created_at")
    reviews = user_obj.reviews.all().order_by("-created_at")
    wishlist_items = user_obj.wishlist_items.all().order_by("-added_at")

    return render(request, "admin_panel/user/detail.html", {
        "user_obj": user_obj,
        "orders": orders,
        "reviews": reviews,
        "wishlist_items": wishlist_items,
    })


@staff_member_required
def my_profile_admin(request):
    user_obj = request.user
    orders = user_obj.orders.all().order_by("-created_at")
    reviews = user_obj.reviews.all().order_by("-created_at")
    wishlist_items = user_obj.wishlist_items.all().order_by("-added_at")

    return render(request, "admin_panel/user/detail.html", {
        "user_obj": user_obj,
        "orders": orders,
        "reviews": reviews,
        "wishlist_items": wishlist_items,
        "is_self_profile": True,
        "page_title_override": "Mon profil",
    })


@staff_member_required
@group_required("SUPER_ADMIN", "SUPPORT")
def review_list_admin(request):
    reviews = Review.objects.all().order_by("-created_at")
    return render(request, "admin_panel/review/list.html", {
        "reviews": reviews
    })


@staff_member_required
@group_required("SUPER_ADMIN", "SUPPORT")
def review_toggle_approval(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    review.is_approved = not review.is_approved
    review.save()

    if review.is_approved:
        messages.success(request, "Avis approuvé.")
    else:
        messages.success(request, "Avis refusé.")

    return redirect("admin_panel:review_list")


@staff_member_required
@group_required("SUPER_ADMIN")
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == "POST":
        review.delete()
        messages.success(request, "Avis supprimé.")
        return redirect("admin_panel:review_list")

    return render(request, "admin_panel/review/confirm_delete.html", {
        "review": review
    })


@staff_member_required
@group_required("SUPER_ADMIN")
def user_create_admin(request):
    if request.method == "POST":
        form = AdminUserCreateForm(request.POST)

        if form.is_valid():
            user = form.save()
            role = request.POST.get("role")

            if role:
                group = Group.objects.get(name=role)
                user.groups.add(group)

            messages.success(request, "Utilisateur créé avec succès.")
            return redirect("admin_panel:user_list")
    else:
        form = AdminUserCreateForm()

    roles = Group.objects.all()

    return render(request, "admin_panel/user/form.html", {
        "form": form,
        "roles": roles
    })


@staff_member_required
@group_required("SUPER_ADMIN")
def user_update_admin(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = AdminUserUpdateForm(request.POST, instance=user_obj)

        if form.is_valid():
            user = form.save()
            role = request.POST.get("role")

            if role:
                user.groups.clear()
                group = Group.objects.get(name=role)
                user.groups.add(group)

            messages.success(request, "Utilisateur modifié avec succès.")
            return redirect("admin_panel:user_list")
    else:
        form = AdminUserUpdateForm(instance=user_obj)

    roles = Group.objects.all()
    current_role = user_obj.groups.first()

    return render(request, "admin_panel/user/edit.html", {
        "form": form,
        "roles": roles,
        "current_role": current_role,
        "user_obj": user_obj
    })


@staff_member_required
def my_settings_admin(request):
    user_obj = request.user

    if request.method == "POST":
        form = AdminSelfUpdateForm(request.POST, instance=user_obj)

        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect("admin_panel:my_profile")
    else:
        form = AdminSelfUpdateForm(instance=user_obj)

    return render(request, "admin_panel/user/edit.html", {
        "form": form,
        "user_obj": user_obj,
        "is_self_profile": True,
        "page_title_override": "Paramètres",
        "form_title_override": "Modifier mon profil",
        "form_description_override": "Mettez à jour vos informations de compte.",
        "return_url": "admin_panel:my_profile",
    })


@staff_member_required
@group_required("SUPER_ADMIN")
def user_change_password_admin(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = SetPasswordForm(user_obj, request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Mot de passe modifié avec succès.")
            return redirect("admin_panel:user_list")
    else:
        form = SetPasswordForm(user_obj)

    return render(request, "admin_panel/user/change_password.html", {
        "form": form,
        "user_obj": user_obj
    })


@staff_member_required
def my_password_admin(request):
    user_obj = request.user

    if request.method == "POST":
        form = PasswordChangeForm(user_obj, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Mot de passe modifié avec succès.")
            return redirect("admin_panel:my_profile")
    else:
        form = PasswordChangeForm(user_obj)

    return render(request, "admin_panel/user/change_password.html", {
        "form": form,
        "user_obj": user_obj,
        "is_self_profile": True,
        "page_title_override": "Mon mot de passe",
        "return_url": "admin_panel:my_profile",
    })
