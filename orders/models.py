from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from catalog.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "En attente"),
        ("PAID", "Payée"),
        ("SHIPPED", "Expédiée"),
        ("DELIVERED", "Livrée"),
        ("CANCELLED", "Annulée"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    PAYMENT_METHOD_CHOICES = [
        ("COD", "Paiement à la livraison"),
        ("CARD", "Carte bancaire simulée"),
    ]

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="COD"
    )

    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    shipping_city = models.CharField(max_length=100, blank=True, null=True)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
        
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"

    def __str__(self):
        return f"Commande #{self.id} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def get_subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"