from django.db import models
from coupons.models import Coupon
from django.conf import settings
from django.db import models
from catalog.models import Product


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts"
    )
    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        self.items.all().delete()

    def get_discount_amount(self):
        total = self.get_total()

        if not self.coupon:
            return 0

        if not self.coupon.is_valid():
            return 0

        if total < self.coupon.min_order_amount:
            return 0

        if self.coupon.discount_type == "PERCENT":
            return total * self.coupon.value / 100

        if self.coupon.discount_type == "FIXED":
            return min(self.coupon.value, total)

        return 0


    def get_final_total(self):
        return self.get_total() - self.get_discount_amount()
    
    def __str__(self):
        return f"Panier de {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Article panier"
        verbose_name_plural = "Articles panier"
        unique_together = ("cart", "product")

    def get_subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name_fr} x {self.quantity}"