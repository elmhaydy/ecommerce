from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "created_at")
    list_filter = ("rating", "is_approved", "created_at")
    search_fields = ("product__name_fr", "user__username", "comment")