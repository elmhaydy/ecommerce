from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import WishlistItem


@admin.register(WishlistItem)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "added_at")
    search_fields = ("user__username", "product__name_fr")