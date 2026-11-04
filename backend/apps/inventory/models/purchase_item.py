
from decimal import Decimal,ROUND_HALF_UP
from django.db.models import Q

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        "inventory.Purchase",
        on_delete=models.PROTECT,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="purchase_items",
    )

    packaging = models.ForeignKey(
        "inventory.ProductPackaging",
        on_delete=models.PROTECT,
        related_name="purchase_items",
    )

    # Preserve the packaging details used when this purchase was recorded.
    packaging_name_snapshot = models.CharField(max_length=50)

    conversion_factor_snapshot = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    package_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
    )

    purchase_unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Cost of one selected package.",
    )

    allocated_transport_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Purchase Item"
        verbose_name_plural = "Purchase Items"

        constraints = [
            models.CheckConstraint(
                condition=Q(conversion_factor_snapshot__gt=0),
                name="purchase_item_conversion_positive",
            ),
            models.CheckConstraint(
                condition=Q(package_quantity__gt=0),
                name="purchase_item_package_quantity_positive",
            ),
            models.CheckConstraint(
                condition=Q(purchase_unit_cost__gte=0),
                name="purchase_item_unit_cost_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(allocated_transport_cost__gte=0),
                name="purchase_item_transport_nonnegative",
            ),
        ]

    @property
    def base_quantity(self):
        return self.package_quantity * self.conversion_factor_snapshot


    @property
    def line_subtotal(self):
        return (self.package_quantity * self.purchase_unit_cost).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @property
    def landed_total_cost(self):
        return self.line_subtotal + self.allocated_transport_cost

    @property
    def landed_unit_cost(self):
        if self.base_quantity == 0:
            return Decimal("0.00")

        return self.landed_total_cost / self.base_quantity

    def clean(self):
        super().clean()

        if self.product_id and self.packaging_id:
            if self.packaging.product_id != self.product_id:
                raise ValidationError({
                    "packaging": "This packaging option belongs to a different product."
                })

            if not self.packaging.purchase_enabled:
                raise ValidationError({
                    "packaging": "This packaging option is not enabled for purchasing."
                })

            if not self.packaging.is_active:
                raise ValidationError({
                    "packaging": "This packaging option is inactive."
                })

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.package_quantity} {self.packaging_name_snapshot}"
        )