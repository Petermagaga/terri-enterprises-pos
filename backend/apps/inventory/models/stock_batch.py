
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q


class StockBatch(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="stock_batches",
    )

    purchase_item = models.OneToOneField(
        "inventory.PurchaseItem",
        on_delete=models.PROTECT,
        related_name="stock_batch",
    )

    received_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
    )

    remaining_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.000"))],
    )

    landed_unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

    received_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["received_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(received_quantity__gt=0),
                name="stock_batch_received_quantity_positive",
            ),
            models.CheckConstraint(
                condition=Q(remaining_quantity__gte=0),
                name="stock_batch_remaining_quantity_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(remaining_quantity__lte=F("received_quantity")),
                name="stock_batch_remaining_lte_received",
            ),
            models.CheckConstraint(
                condition=Q(landed_unit_cost__gte=0),
                name="stock_batch_landed_cost_nonnegative",
            ),
        ]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.remaining_quantity} remaining"
        )
