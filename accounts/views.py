from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import ProfileUpdateForm
from coupons.models import Coupon


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("core:home")
    else:
        form = UserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("core:home")


def _account_template(request, client_template, admin_template):
    return admin_template if request.user.is_staff else client_template


@login_required
def profile_view(request):
    orders = request.user.orders.all().order_by("-created_at")[:5]
    template_name = _account_template(
        request,
        "accounts/profile_client.html",
        "accounts/profile.html",
    )

    return render(request, template_name, {"orders": orders})


@login_required
def profile_edit(request):
    template_name = _account_template(
        request,
        "accounts/profile_edit_client.html",
        "accounts/profile_edit.html",
    )

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Profil modifie avec succes.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, template_name, {"form": form})


@login_required
def account_activity(request):
    orders = request.user.orders.all().order_by("-created_at")
    wishlist_count = request.user.wishlist_items.count()
    review_count = request.user.reviews.count()
    delivered_count = orders.filter(status="DELIVERED").count()
    total_spent = orders.exclude(status="CANCELLED").aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    return render(request, "accounts/activity_client.html", {
        "recent_orders": orders[:5],
        "wishlist_count": wishlist_count,
        "review_count": review_count,
        "delivered_count": delivered_count,
        "total_spent": total_spent,
    })


@login_required
def account_coupons(request):
    now = timezone.now()
    coupons = Coupon.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now,
    ).order_by("end_date")

    available_coupons = [
        coupon for coupon in coupons
        if coupon.used_count < coupon.usage_limit
    ]

    return render(request, "accounts/coupons_client.html", {
        "coupons": available_coupons,
    })


@login_required
def account_addresses(request):
    orders = request.user.orders.exclude(address="").order_by("-created_at")
    addresses = []
    seen = set()

    for order in orders:
        key = (order.address, order.city, order.postal_code, order.phone)
        if key in seen:
            continue
        seen.add(key)
        addresses.append(order)

    return render(request, "accounts/addresses_client.html", {
        "addresses": addresses,
    })


@login_required
def account_reviews(request):
    reviews = request.user.reviews.select_related("product").order_by("-created_at")
    approved_count = reviews.filter(is_approved=True).count()

    return render(request, "accounts/reviews_client.html", {
        "reviews": reviews,
        "approved_count": approved_count,
    })


class RoleBasedPasswordChangeView(PasswordChangeView):
    def get_template_names(self):
        return [
            _account_template(
                self.request,
                "accounts/password_change_client.html",
                "accounts/password_change.html",
            )
        ]


class RoleBasedPasswordChangeDoneView(PasswordChangeDoneView):
    def get_template_names(self):
        return [
            _account_template(
                self.request,
                "accounts/password_change_done_client.html",
                "accounts/password_change_done.html",
            )
        ]
