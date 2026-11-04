from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class ProductPackaging(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="packaging_options",
    )

    name = models.CharField(max_length=50)

    conversion_factor = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of product base units contained in one package.",
    )

    purchase_enabled = models.BooleanField(default=True)
    sales_enabled = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product__name", "conversion_factor"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "name"],
                name="unique_product_packaging_name",
            ),
            models.CheckConstraint(
                condition=Q(conversion_factor__gt=0),
                name="packaging_conversion_factor_positive",
            ),
        ]

    def clean(self):
        super().clean()

        self.name = self.name.strip()

        if not self.name:
            raise ValidationError({
                "name": "Packaging name cannot be empty."
            })

        if not self.purchase_enabled and not self.sales_enabled:
            raise ValidationError(
                "Enable packaging for purchasing, selling, or both."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.product.name} - {self.name} "
            f"({self.conversion_factor} {self.product.base_unit})"
        )