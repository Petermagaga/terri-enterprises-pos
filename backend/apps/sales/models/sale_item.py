from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class SaleItem(models.Model):

    class PricingType(models.TextChoices):
        RETAIL = "RETAIL", "Retail"
        WHOLESALE = "WHOLESALE", "Wholesale"

    sale = models.ForeignKey(
        "sales.Sale",
        on_delete=models.PROTECT,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="sale_items",
    )

    packaging = models.ForeignKey(
        "inventory.ProductPackaging",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sale_items",
    )

    # Historical product snapshots
    product_name_snapshot = models.CharField(max_length=150)
    product_sku_snapshot = models.CharField(max_length=20)
    base_unit_snapshot = models.CharField(max_length=30)

    # Historical packaging snapshots
    packaging_name_snapshot = models.CharField(max_length=50)
    conversion_factor_snapshot = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    pricing_type = models.CharField(
        max_length=10,
        choices=PricingType.choices,
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    selling_price_per_package = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
    )

    total_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="sale_item_quantity_positive",
            ),
            models.CheckConstraint(
                condition=Q(conversion_factor_snapshot__gt=0),
                name="sale_item_conversion_positive",
            ),
            models.CheckConstraint(
                condition=Q(selling_price_per_package__gte=0),
                name="sale_item_price_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(total_amount__gte=0),
                name="sale_item_total_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(total_cost__gte=0),
                name="sale_item_cost_nonnegative",
            ),
        ]

    @property
    def base_quantity(self):
        return self.quantity * self.conversion_factor_snapshot

    def __str__(self):
        return (
            f"{self.product_name_snapshot} "
            f"x {self.quantity} {self.packaging_name_snapshot}"
        )