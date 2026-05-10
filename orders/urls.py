from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("success/<int:order_id>/", views.order_success, name="order_success"),
    path("history/", views.order_history, name="order_history"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("cancel/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("payment/<int:order_id>/", views.payment_page, name="payment_page"),
]