
from django.db import models


class ProductFamily(models.Model):
    name = models.CharField(max_length=100, unique=True)

    sku_prefix = models.CharField(
        max_length=4,
        unique=True,
        editable=False,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Family"
        verbose_name_plural = "Product Families"
        ordering = ["name"]

    def __str__(self):
        if self.sku_prefix:
            return f"{self.name} ({self.sku_prefix})"

        return self.name
