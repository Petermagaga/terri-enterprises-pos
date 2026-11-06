
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.accounts.models import User
from apps.inventory.models import StockMovement
from apps.inventory.services.stock_deduction import deduct_stock_fifo
from apps.sales.models import Sale, SaleItem


CENT = Decimal("0.01")


@transaction.atomic
def complete_sale(*, sale):
    """
    Complete a fully paid draft sale.

    Deducts stock using FIFO, records actual item costs,
    generates a receipt number, and completes the sale.

    The entire operation is atomic. Any failure rolls back
    all stock deductions and sale updates.
    """

    if not isinstance(sale, Sale):
        raise ValidationError("A valid sale is required.")

    try:
        sale = (
            Sale.objects
            .select_for_update()
            .get(pk=sale.pk)
        )
    except Sale.DoesNotExist:
        raise ValidationError("The selected sale does not exist.")

    if sale.status != Sale.Status.DRAFT:
        raise ValidationError("Only draft sales can be completed.")

    if not sale.processed_by.is_active:
        raise ValidationError(
            "The user who processed this sale is inactive."
        )

    if sale.processed_by.role not in {
        User.Role.OWNER,
        User.Role.CASHIER,
    }:
        raise ValidationError(
            "The user who processed this sale is not authorized."
        )

    # Lock sale items in a consistent product order.
    items = list(
        SaleItem.objects
        .select_for_update()
        .filter(sale=sale)
        .order_by("product_id", "id")
    )

    if not items:
        raise ValidationError(
            "A sale must contain at least one item before completion."
        )

    if sale.total_amount <= 0:
        raise ValidationError("Sale total must be greater than zero.")

    # Verify that recorded payments exactly cover the sale.
    total_paid = sale.payments.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    if total_paid != sale.total_amount:
        raise ValidationError(
            f"Sale must be fully paid. "
            f"Sale total: {sale.total_amount}, "
            f"amount paid: {total_paid}."
        )

    if sale.receipt_number:
        raise ValidationError(
            "This sale already has a receipt number."
        )

    # The sale primary key makes this receipt number unique.
    receipt_number = (
        f"TE-{sale.created_at:%Y%m%d}-{sale.pk:06d}"
    )

    total_cost = Decimal("0.00")

    for item in items:
        # Packaging conversion is already preserved in the snapshot.
        # For example, 2 cartons x 12 = 24 individual units.
        deductions = deduct_stock_fifo(
            product=item.product,
            quantity=item.base_quantity,
            created_by=sale.processed_by,
            reference=receipt_number,
            notes=f"Stock deducted for sale {receipt_number}.",
            movement_type=StockMovement.MovementType.SALE,
        )

        # Sum the actual FIFO cost across all consumed batches.
        item_cost = sum(
            (deduction["total_cost"] for deduction in deductions),
            Decimal("0.00"),
        ).quantize(
            CENT,
            rounding=ROUND_HALF_UP,
        )

        item.total_cost = item_cost
        item.save(update_fields=["total_cost"])

        total_cost += item_cost

    # Complete the sale only after every stock deduction succeeds.
    sale.total_cost = total_cost
    sale.receipt_number = receipt_number
    sale.status = Sale.Status.COMPLETED
    sale.completed_at = timezone.now()

    sale.save(
        update_fields=[
            "total_cost",
            "receipt_number",
            "status",
            "completed_at",
        ]
    )

    return sale
