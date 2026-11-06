from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from apps.accounts.models import User
from apps.sales.models import Sale, SalePayment


@transaction.atomic
def add_sale_payment(
    *,
    sale,
    payment_method,
    amount,
    received_by,
    reference="",
):
    """
    Record a payment against a draft sale.

    Supports cash, M-Pesa, and split payments.
    Payments cannot exceed the sale total.
    """

    if not isinstance(sale, Sale):
        raise ValidationError("A valid sale is required.")

    if not isinstance(received_by, User):
        raise ValidationError("A valid receiving user is required.")

    if not received_by.is_active:
        raise ValidationError("An inactive user cannot receive payments.")

    if received_by.role not in {
        User.Role.OWNER,
        User.Role.CASHIER,
    }:
        raise ValidationError("This user is not allowed to receive payments.")

    if payment_method not in SalePayment.PaymentMethod.values:
        raise ValidationError("Invalid payment method.")

    if isinstance(amount, bool):
        raise ValidationError("Payment amount must be a valid number.")

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Payment amount must be a valid number.")

    if not amount.is_finite() or amount <= 0:
        raise ValidationError("Payment amount must be greater than zero.")

    if not isinstance(reference, str):
        raise ValidationError("Payment reference must be text.")

    try:
        sale = (
            Sale.objects
            .select_for_update()
            .get(pk=sale.pk)
        )
    except Sale.DoesNotExist:
        raise ValidationError("The selected sale does not exist.")

    if sale.status != Sale.Status.DRAFT:
        raise ValidationError("Payments can only be added to draft sales.")

    if sale.total_amount <= 0:
        raise ValidationError("Cannot receive payment for an empty sale.")

    existing_payments = sale.payments.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    if existing_payments + amount > sale.total_amount:
        raise ValidationError(
            "Payment amount exceeds the outstanding sale balance."
        )

    payment = SalePayment(
        sale=sale,
        payment_method=payment_method,
        amount=amount,
        reference=reference.strip(),
        received_by=received_by,
    )

    payment.full_clean()
    payment.save()

    return payment