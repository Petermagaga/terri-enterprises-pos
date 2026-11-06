from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal


class Expense(models.Model):

    class Category(models.TextChoices):
        RENT = "RENT", "Rent"
        ELECTRICITY = "ELECTRICITY", "Electricity"
        WATER = "WATER", "Water"
        SALARIES = "SALARIES", "Salaries and wages"
        TRANSPORT = "TRANSPORT", "Transport"
        REPAIRS = "REPAIRS", "Repairs and maintenance"
        LICENSES = "LICENSES", "Licenses and permits"
        INTERNET = "INTERNET", "Internet and communication"
        OTHER = "OTHER", "Other"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        MPESA = "MPESA", "M-Pesa"
        BANK = "BANK", "Bank"

    description = models.CharField(
        max_length=255,
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    expense_date = models.DateField(
        default=timezone.localdate,
    )

    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
    )

    payment_reference = models.CharField(
        max_length=100,
        blank=True,
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="expenses_recorded",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-expense_date", "-created_at"]
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="expense_amount_positive",
            ),
            models.CheckConstraint(
                condition=(
                    Q(payment_method="CASH", payment_reference="")
                    | Q(
                        payment_method__in=["MPESA", "BANK"],
                    ) & ~Q(payment_reference="")
                ),
                name="expense_payment_reference_valid",
            ),
        ]

    def clean(self):
        if self.payment_method in [
            self.PaymentMethod.MPESA,
            self.PaymentMethod.BANK,
        ] and not self.payment_reference.strip():
            raise ValidationError({
                "payment_reference": (
                    "A transaction reference is required for M-Pesa and bank payments."
                )
            })

        if (
            self.payment_method == self.PaymentMethod.CASH
            and self.payment_reference.strip()
        ):
            raise ValidationError({
                "payment_reference": (
                    "Cash expenses should not have a payment reference."
                )
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category} - KSh {self.amount}"