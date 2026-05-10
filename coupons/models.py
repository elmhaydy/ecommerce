from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("PERCENT", "Pourcentage"),
        ("FIXED", "Montant fixe"),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active
            and self.start_date <= now <= self.end_date
            and self.used_count < self.usage_limit
        )

    def __str__(self):
        return self.code