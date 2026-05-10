from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from catalog.models import Product


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    is_verified_purchase = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ("product", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product} - {self.rating}/5"