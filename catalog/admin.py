from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_fr", "name_en", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name_fr", "name_en")
    prepopulated_fields = {"slug": ("name_fr",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name_fr", "category", "price", "stock", "is_active", "is_featured")
    list_filter = ("category", "is_active", "is_featured")
    search_fields = ("name_fr", "name_en")
    prepopulated_fields = {"slug": ("name_fr",)}