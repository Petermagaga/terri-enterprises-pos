from django.db import models


class ProductFamily(models.Model):
    name = models.CharField(max_length=100, unique=True)

    # Allocated by the SKU generation service.
    # Never manually editable.
    sku_prefix = models.CharField(
        max_length=4,
        unique=True,
        editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Family"
        verbose_name_plural = "Product Families"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku_prefix})"