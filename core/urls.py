from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search_page, name="search"),
    path("search/suggestions/", views.search_suggestions, name="search_suggestions"),
    path("support/chat/status/", views.support_chat_status, name="support_chat_status"),
    path("support/chat/history/", views.support_chat_history, name="support_chat_history"),
    path("support/chat/send/", views.support_chat_send, name="support_chat_send"),
    path("set-language/", views.set_language, name="set_language"),
    path("about-us/", views.footer_page, {"slug": "about-us"}, name="about_us"),
    path("affiliate-program/", views.footer_page, {"slug": "affiliate-program"}, name="affiliate_program"),
    path("where-to-buy/", views.footer_page, {"slug": "where-to-buy"}, name="where_to_buy"),
    path("contact-us/", views.footer_page, {"slug": "contact-us"}, name="contact_us"),
    path("points-program/", views.footer_page, {"slug": "points-program"}, name="points_program"),
    path("warranty/", views.footer_page, {"slug": "warranty"}, name="warranty"),
    path("shipping-delivery/", views.footer_page, {"slug": "shipping-delivery"}, name="shipping_delivery"),
    path("return-policy/", views.footer_page, {"slug": "return-policy"}, name="return_policy"),
    path("terms-and-conditions/", views.footer_page, {"slug": "terms-conditions"}, name="terms_conditions"),
    path("privacy-policy/", views.footer_page, {"slug": "privacy-policy"}, name="privacy_policy"),
]
