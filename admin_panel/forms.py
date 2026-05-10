from django import forms
from catalog.models import Category, Product
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name_fr", "name_en", "slug", "is_active"]
        widgets = {
            "name_fr": forms.TextInput(attrs={"placeholder": "Ex: Robes"}),
            "name_en": forms.TextInput(attrs={"placeholder": "Ex: Dresses"}),
            "slug": forms.TextInput(attrs={"placeholder": "Ex: robes"}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name_fr",
            "name_en",
            "slug",
            "description_fr",
            "description_en",
            "price",
            "old_price",
            "stock",
            "low_stock_threshold",
            "image",
            "gallery_image_1",
            "gallery_image_2",
            "gallery_image_3",
            "gallery_image_4",
            "feature_1",
            "feature_2",
            "feature_3",
            "feature_4",
            "colors",
            "is_active",
            "is_featured",
        ]
        widgets = {
            "name_fr": forms.TextInput(attrs={"placeholder": "Ex: Oraimo Watch 5 Lite"}),
            "name_en": forms.TextInput(attrs={"placeholder": "Ex: Oraimo Watch 5 Lite"}),
            "slug": forms.TextInput(attrs={"placeholder": "Ex: oraimo-watch-5-lite"}),
            "description_fr": forms.Textarea(attrs={"rows": 5, "placeholder": "Description détaillée du produit"}),
            "description_en": forms.Textarea(attrs={"rows": 5, "placeholder": "English description"}),
            "feature_1": forms.TextInput(attrs={"placeholder": 'Ex: 2.01" HD Screen'}),
            "feature_2": forms.TextInput(attrs={"placeholder": "Ex: HD Voice in Calls"}),
            "feature_3": forms.TextInput(attrs={"placeholder": "Ex: AI-Generated Watch Faces"}),
            "feature_4": forms.TextInput(attrs={"placeholder": "Ex: IP68 Dust & Water Resistance"}),
            "colors": forms.TextInput(attrs={"placeholder": "Ex: Noir, Beige, Bleu"}),
        }


from coupons.models import Coupon


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            "code",
            "discount_type",
            "value",
            "min_order_amount",
            "start_date",
            "end_date",
            "usage_limit",
            "is_active",
        ]

        widgets = {
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

from shipping.models import ShippingZone


class ShippingZoneForm(forms.ModelForm):
    class Meta:
        model = ShippingZone
        fields = ["city", "fee", "free_shipping_threshold", "is_active"]

class AdminUserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active"]


class AdminSelfUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

