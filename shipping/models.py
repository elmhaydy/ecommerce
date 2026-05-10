from django.db import models


class ShippingZone(models.Model):
    city = models.CharField(max_length=100, unique=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["city"]
        verbose_name = "Zone de livraison"
        verbose_name_plural = "Zones de livraison"

    def __str__(self):
        return f"{self.city} - {self.fee} DH"