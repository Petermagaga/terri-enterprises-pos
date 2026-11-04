
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class InventoryBalance(models.Model):
    product = models.OneToOneField(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="inventory_balance",
    )

    quantity_on_hand = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        default=Decimal("0.000"),
        validators=[MinValueValidator(Decimal("0.000"))],
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventory Balance"
        verbose_name_plural = "Inventory Balances"
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity_on_hand__gte=0),
                name="inventory_balance_quantity_nonnegative",
            ),
        ]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.quantity_on_hand} {self.product.base_unit}"
        )
