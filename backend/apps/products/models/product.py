from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal

class Product(models.Model):

    class SizeUnit(models.TextChoices):
        GRAM = "G", "Gram"
        KILOGRAM = "KG", "Kilogram"
        MILLILITRE = "ML", "Millilitre"
        LITRE = "L", "Litre"

    name = models.CharField(max_length=150)

    # Products with different sizes can belong to the same family.
    # Example: Margarine 50g and Margarine 500g.
    product_family = models.ForeignKey(
        "products.ProductFamily",
        on_delete=models.PROTECT,related_name="products",)

    sku = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    category = models.ForeignKey(
        "products.Category",
        on_delete=models.PROTECT,
        related_name="products",
    )

    brand = models.CharField(max_length=100, blank=True)

    size_value = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
    )

    size_unit = models.CharField(
        max_length=2,
        choices=SizeUnit.choices,
    )


    base_unit = models.CharField(max_length=30)

    retail_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    wholesale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    wholesale_min_quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Minimum quantity in base units required for wholesale pricing.",
    )

    reorder_level = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        # Prevent an existing product's SKU from being changed.
        if self.pk:
            original_sku = (
                type(self).objects
                .only("sku")
                .get(pk=self.pk)
                .sku
            )

            if original_sku != self.sku:
                raise ValidationError("A product SKU cannot be changed.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"