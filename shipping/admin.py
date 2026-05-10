from django.contrib import admin
from .models import ShippingZone


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ("city", "fee", "free_shipping_threshold", "is_active")
    list_filter = ("is_active",)
    search_fields = ("city",)