
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q


class Sale(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        COMPLETED = "COMPLETED", "Completed"
        VOIDED = "VOIDED", "Voided"

    receipt_number = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sales_processed",
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(total_amount__gte=0),
                name="sale_total_amount_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(total_cost__gte=0),
                name="sale_total_cost_nonnegative",
            ),
        ]

    @property
    def gross_profit(self):
        return self.total_amount - self.total_cost

    def __str__(self):
        return self.receipt_number or f"Draft Sale #{self.pk}"
