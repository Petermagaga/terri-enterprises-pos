
from decimal import Decimal
from django.db.models import Q
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Purchase(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        RECEIVED = "RECEIVED", "Received"

    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="purchases",
    )

    supplier_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Supplier invoice or delivery reference.",
    )

    purchase_date = models.DateField(
        default=timezone.localdate,
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    transport_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Transport cost directly attributable to this stock purchase.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inventory_purchases_created",
    )

    received_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-purchase_date", "-created_at"]
        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"

        constraints = [
            models.CheckConstraint(
                condition=Q(transport_cost__gte=0),
                name="purchase_transport_cost_nonnegative",
            ),
        ]

    def __str__(self):
        return f"Purchase #{self.pk} - {self.supplier.name}"
