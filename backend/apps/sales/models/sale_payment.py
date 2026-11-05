from django.db import models
from django.db.models import Q


class SalePayment(models.Model):

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        MPESA = "MPESA", "M-Pesa"

    sale = models.ForeignKey(
        "sales.Sale",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
    )

    received_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="sale_payments_received",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="sale_payment_amount_positive",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.payment_method == self.PaymentMethod.MPESA and not self.reference.strip():
            raise ValidationError({
                "reference": "An M-Pesa transaction reference is required."
            })

        if self.payment_method == self.PaymentMethod.CASH and self.reference.strip():
            raise ValidationError({
                "reference": "Cash payments should not have an M-Pesa reference."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_method} - KSh {self.amount}"