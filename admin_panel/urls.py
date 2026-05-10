from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("me/", views.my_profile_admin, name="my_profile"),
    path("me/settings/", views.my_settings_admin, name="my_settings"),
    path("me/password/", views.my_password_admin, name="my_password"),

    path("products/", views.product_list_admin, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/<int:product_id>/edit/", views.product_update, name="product_update"),
    path("products/<int:product_id>/delete/", views.product_delete, name="product_delete"),

    path("orders/<int:order_id>/status/", views.update_order_status, name="update_order_status"),

    path("categories/", views.category_list, name="category_list"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/<int:category_id>/edit/", views.category_update, name="category_update"),
    path("categories/<int:category_id>/delete/", views.category_delete, name="category_delete"),

    path("orders/", views.order_list_admin, name="order_list"),
    path("orders/<int:order_id>/", views.order_detail_admin, name="order_detail"),
    path("support/", views.support_conversation_list_admin, name="support_conversation_list"),
    path("support/data/", views.support_conversation_list_data_admin, name="support_conversation_list_data"),
    path("support/<int:conversation_id>/", views.support_conversation_detail_admin, name="support_conversation_detail"),
    path("support/<int:conversation_id>/messages/", views.support_conversation_messages_admin, name="support_conversation_messages"),
    path("support/<int:conversation_id>/reply/", views.support_conversation_reply_admin, name="support_conversation_reply"),
    path("support/<int:conversation_id>/close/", views.support_conversation_close_admin, name="support_conversation_close"),

    path("coupons/", views.coupon_list, name="coupon_list"),
    path("coupons/create/", views.coupon_create, name="coupon_create"),
    path("coupons/<int:coupon_id>/edit/", views.coupon_update, name="coupon_update"),
    path("coupons/<int:coupon_id>/delete/", views.coupon_delete, name="coupon_delete"),

    path("orders/<int:order_id>/invoice/", views.order_invoice_pdf, name="order_invoice_pdf"),

    path("shipping/", views.shipping_list, name="shipping_list"),
    path("shipping/create/", views.shipping_create, name="shipping_create"),
    path("shipping/<int:zone_id>/edit/", views.shipping_update, name="shipping_update"),
    path("shipping/<int:zone_id>/delete/", views.shipping_delete, name="shipping_delete"),

    path("users/", views.user_list_admin, name="user_list"),
    path("users/<int:user_id>/toggle-active/", views.user_toggle_active, name="user_toggle_active"),  

    path("reviews/", views.review_list_admin, name="review_list"),
    path("reviews/<int:review_id>/toggle/", views.review_toggle_approval, name="review_toggle_approval"),
    path("reviews/<int:review_id>/delete/", views.review_delete, name="review_delete"),

    path("users/<int:user_id>/", views.user_detail_admin, name="user_detail"),

    path("users/create/", views.user_create_admin, name="user_create"),
    path("users/<int:user_id>/edit/", views.user_update_admin, name="user_edit"),

    path("users/<int:user_id>/password/", views.user_change_password_admin, name="user_change_password"),
]
