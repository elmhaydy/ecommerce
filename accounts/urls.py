from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("activity/", views.account_activity, name="activity"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("coupons/", views.account_coupons, name="coupons"),
    path("addresses/", views.account_addresses, name="addresses"),
    path("reviews/", views.account_reviews, name="reviews"),
    path(
        "password/change/",
        views.RoleBasedPasswordChangeView.as_view(),
        name="password_change"
    ),
    path(
        "password/change/done/",
        views.RoleBasedPasswordChangeDoneView.as_view(),
        name="password_change_done"
    ),
]
