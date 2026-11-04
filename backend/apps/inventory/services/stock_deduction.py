from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.inventory.models import (
    InventoryBalance,
    StockBatch,
    StockMovement,
)
from apps.products.models import Product


ZERO_QUANTITY = Decimal("0.000")


@transaction.atomic
def deduct_stock_fifo(
    *,
    product,
    quantity,
    created_by,
    reference="",
    notes="",
):
    """
    Deduct product stock using First In, First Out (FIFO).

    The oldest available stock batches are consumed first.

    Returns a list describing the quantity and cost deducted
    from each batch.
    """

    if not isinstance(product, Product):
        raise ValidationError("A valid product is required.")

    try:
        quantity = Decimal(str(quantity))
    except (TypeError, ValueError, ArithmeticError):
        raise ValidationError("A valid stock quantity is required.")

    if not quantity.is_finite() or quantity <= ZERO_QUANTITY:
        raise ValidationError(
            "Stock deduction quantity must be greater than zero."
        )

    if quantity.as_tuple().exponent < -3:
        raise ValidationError(
            "Stock quantity cannot have more than three decimal places."
        )

    if not created_by or not getattr(created_by, "is_active", False):
        raise ValidationError("An active user is required.")

    # Lock the product first. All inventory-changing services
    # should follow this same locking order.
    try:
        product = (
            Product.objects
            .select_for_update()
            .get(pk=product.pk)
        )
    except Product.DoesNotExist:
        raise ValidationError("The selected product does not exist.")

    if not product.is_active:
        raise ValidationError("Cannot deduct stock for an inactive product.")

    # Lock the inventory balance.
    try:
        balance = (
            InventoryBalance.objects
            .select_for_update()
            .get(product=product)
        )
    except InventoryBalance.DoesNotExist:
        raise ValidationError(
            "This product does not have an inventory balance."
        )

    # Lock all available batches in FIFO order.
    batches = list(
        StockBatch.objects
        .select_for_update()
        .filter(
            product=product,
            remaining_quantity__gt=ZERO_QUANTITY,
        )
        .order_by("received_at", "id")
    )

    available_quantity = sum(
        (batch.remaining_quantity for batch in batches),
        ZERO_QUANTITY,
    )

    # Detect inconsistencies before changing inventory.
    if available_quantity != balance.quantity_on_hand:
        raise ValidationError(
            "Inventory balance does not match available stock batches. "
            "Stock deduction has been stopped."
        )

    if quantity > available_quantity:
        raise ValidationError(
            f"Insufficient stock. Available: {available_quantity}, "
            f"requested: {quantity}."
        )

    remaining_to_deduct = quantity
    deductions = []

    for batch in batches:
        if remaining_to_deduct <= ZERO_QUANTITY:
            break

        deducted_quantity = min(
            batch.remaining_quantity,
            remaining_to_deduct,
        )

        batch.remaining_quantity -= deducted_quantity
        batch.save(update_fields=["remaining_quantity"])

        movement = StockMovement.objects.create(
            product=product,
            stock_batch=batch,
            movement_type=StockMovement.MovementType.SALE,
            direction=StockMovement.Direction.OUT,
            quantity=deducted_quantity,
            unit_cost=batch.landed_unit_cost,
            reference=reference,
            notes=notes,
            created_by=created_by,
        )

        deductions.append({
            "batch_id": batch.pk,
            "quantity": deducted_quantity,
            "unit_cost": batch.landed_unit_cost,
            "total_cost": (
                deducted_quantity * batch.landed_unit_cost
            ),
            "movement_id": movement.pk,
        })

        remaining_to_deduct -= deducted_quantity

    balance.quantity_on_hand -= quantity
    balance.save(update_fields=["quantity_on_hand", "updated_at"])

    return deductions