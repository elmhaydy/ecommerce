from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from catalog.models import Product


class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        unique_together = ("user", "product")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user} - {self.product.name_fr}"