from django.conf import settings
from django.db import models

from product.models import Product


class Order(models.Model):
    product = models.ManyToManyField(Product, related_name="orders")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    def __str__(self):
        return f"Pedido {self.pk} - {self.user.username}"
