
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class StockMovement(models.Model):

    class MovementType(models.TextChoices):
        PURCHASE_RECEIPT = "PURCHASE_RECEIPT", "Purchase Receipt"
        SALE = "SALE", "Sale"
        ADJUSTMENT_IN = "ADJUSTMENT_IN", "Stock Adjustment In"
        ADJUSTMENT_OUT = "ADJUSTMENT_OUT", "Stock Adjustment Out"
        DAMAGE = "DAMAGE", "Damaged Stock"

    class Direction(models.TextChoices):
        IN = "IN", "Stock In"
        OUT = "OUT", "Stock Out"

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )

    stock_batch = models.ForeignKey(
        "inventory.StockBatch",
        on_delete=models.PROTECT,
        related_name="movements",
        null=True,
        blank=True,
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
    )

    direction = models.CharField(
        max_length=3,
        choices=Direction.choices,
    )

    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
    )

    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000000"))],
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Reference to the transaction that caused this movement.",
    )

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="stock_movements_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="stock_movement_quantity_positive",
            ),
            models.CheckConstraint(
                condition=Q(unit_cost__isnull=True) | Q(unit_cost__gte=0),
                name="stock_movement_unit_cost_nonnegative",
            ),
        ]

    def clean(self):
        super().clean()

        if self.stock_batch_id and self.product_id:
            if self.stock_batch.product_id != self.product_id:
                raise ValidationError({
                    "stock_batch": (
                        "The selected batch belongs to a different product."
                    )
                })

        expected_directions = {
            self.MovementType.PURCHASE_RECEIPT: self.Direction.IN,
            self.MovementType.SALE: self.Direction.OUT,
            self.MovementType.ADJUSTMENT_IN: self.Direction.IN,
            self.MovementType.ADJUSTMENT_OUT: self.Direction.OUT,
            self.MovementType.DAMAGE: self.Direction.OUT,
        }

        if (
            self.movement_type in expected_directions
            and self.direction != expected_directions[self.movement_type]
        ):
            raise ValidationError({
                "direction": (
                    "The direction does not match the selected movement type."
                )
            })

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError(
                "Stock movements are immutable and cannot be edited."
            )

        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "Stock movements are immutable and cannot be deleted."
        )

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.movement_type} - {self.quantity}"
        )