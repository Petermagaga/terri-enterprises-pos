from django.db import models
from django.db.models import Q


class StockAlert(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="stock_alerts",
    )

    quantity_on_hand = models.DecimalField(
        max_digits=15,
        decimal_places=3,
    )

    reorder_level = models.PositiveIntegerField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Stock Alert"
        verbose_name_plural = "Stock Alerts"
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(resolved_at__isnull=True),
                name="unique_unresolved_stock_alert_per_product",
            ),
        ]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.quantity_on_hand} "
            f"(reorder level: {self.reorder_level})"
        )
