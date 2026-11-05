
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.inventory.models import (
    InventoryBalance,
    StockBatch,
    StockMovement,
)
from apps.inventory.services.stock_deduction import deduct_stock_fifo
from apps.products.models import Product


ZERO_QUANTITY = Decimal("0.000")
ZERO_COST = Decimal("0.000000")


def _parse_decimal(value, field_name):
    try:
        result = Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        raise ValidationError(f"Enter a valid {field_name}.")

    if not result.is_finite():
        raise ValidationError(f"{field_name.capitalize()} must be finite.")

    return result


@transaction.atomic
def adjust_stock(
    *,
    product,
    quantity,
    movement_type,
    created_by,
    reason,
    unit_cost=None,
    reference="",
):
    """
    Record an owner-authorized stock adjustment.

    ADJUSTMENT_IN:
        Creates a new stock batch using the owner's entered unit cost.

    ADJUSTMENT_OUT:
        Removes existing stock using FIFO.

    DAMAGE:
        Writes off damaged stock using FIFO.
    """

    # Validate the adjustment type.
    allowed_types = {
        StockMovement.MovementType.ADJUSTMENT_IN,
        StockMovement.MovementType.ADJUSTMENT_OUT,
        StockMovement.MovementType.DAMAGE,
    }

    if movement_type not in allowed_types:
        raise ValidationError("Invalid stock adjustment type.")

    # Enforce Owner authorization inside the service.
    if (
        not isinstance(created_by, User)
        or not created_by.is_authenticated
        or not created_by.is_active
        or created_by.role != User.Role.OWNER
    ):
        raise ValidationError(
            "Only an active business owner can authorize stock adjustments."
        )

    if not isinstance(product, Product) or not product.pk:
        raise ValidationError("A valid product is required.")

    quantity = _parse_decimal(quantity, "stock quantity")

    if quantity <= ZERO_QUANTITY:
        raise ValidationError("Adjustment quantity must be greater than zero.")

    if quantity.as_tuple().exponent < -3:
        raise ValidationError(
            "Stock quantity cannot have more than three decimal places."
        )

    reason = str(reason or "").strip()

    if not reason:
        raise ValidationError("An adjustment reason is required.")

    reference = str(reference or "").strip()

    if len(reference) > 100:
        raise ValidationError("Reference cannot exceed 100 characters.")

    # Stock increases require an owner-entered unit cost.
    if movement_type == StockMovement.MovementType.ADJUSTMENT_IN:
        if unit_cost is None:
            raise ValidationError(
                "Unit cost is required for stock increases."
            )

        unit_cost = _parse_decimal(unit_cost, "unit cost")

        if unit_cost < ZERO_COST:
            raise ValidationError("Unit cost cannot be negative.")

        if unit_cost.as_tuple().exponent < -6:
            raise ValidationError(
                "Unit cost cannot have more than six decimal places."
            )

    elif unit_cost is not None:
        raise ValidationError(
            "Unit cost must not be supplied for stock reductions or damage."
        )

    # Lock the product before changing inventory.
    try:
        product = (
            Product.objects
            .select_for_update()
            .get(pk=product.pk)
        )
    except Product.DoesNotExist:
        raise ValidationError("The selected product does not exist.")

    if not product.is_active:
        raise ValidationError("Cannot adjust stock for an inactive product.")

    # Stock reductions and damage use the existing FIFO engine.
    if movement_type in {
        StockMovement.MovementType.ADJUSTMENT_OUT,
        StockMovement.MovementType.DAMAGE,
    }:
        deductions = deduct_stock_fifo(
            product=product,
            quantity=quantity,
            created_by=created_by,
            reference=reference,
            notes=reason,
            movement_type=movement_type,
        )

        return {
            "movement_type": movement_type,
            "quantity": quantity,
            "deductions": deductions,
        }

    # For stock increases, obtain or create the product balance.
    InventoryBalance.objects.get_or_create(product=product)

    balance = (
        InventoryBalance.objects
        .select_for_update()
        .get(product=product)
    )

    available_quantity = sum(
        StockBatch.objects
        .select_for_update()
        .filter(
            product=product,
            remaining_quantity__gt=ZERO_QUANTITY,
        )
        .values_list("remaining_quantity", flat=True),
        ZERO_QUANTITY,
    )

    if available_quantity != balance.quantity_on_hand:
        raise ValidationError(
            "Inventory balance does not match available stock batches. "
            "Stock adjustment has been stopped."
        )

    adjustment_time = timezone.now()

    # Create a new batch without a purchase item.
    batch = StockBatch.objects.create(
        product=product,
        purchase_item=None,
        received_quantity=quantity,
        remaining_quantity=quantity,
        landed_unit_cost=unit_cost,
        received_at=adjustment_time,
    )

    # Record the stock increase in the immutable movement history.
    movement = StockMovement.objects.create(
        product=product,
        stock_batch=batch,
        movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
        direction=StockMovement.Direction.IN,
        quantity=quantity,
        unit_cost=unit_cost,
        reference=reference,
        notes=reason,
        created_by=created_by,
    )

    balance.quantity_on_hand += quantity
    balance.save(update_fields=["quantity_on_hand", "updated_at"])

    return {
        "movement_type": movement_type,
        "quantity": quantity,
        "batch": batch,
        "movement": movement,
    }
