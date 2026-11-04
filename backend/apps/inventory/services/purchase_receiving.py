
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.inventory.models import (
    InventoryBalance,
    Purchase,
    PurchaseItem,
    StockBatch,
    StockMovement,
)
from apps.inventory.services.transport_allocation import (
    allocate_transport_cost,
)
from apps.products.models import Product


SIX_DECIMAL_PLACES = Decimal("0.000001")


@transaction.atomic
def receive_purchase(*, purchase, received_at=None):
    """
    Receive a draft purchase into inventory.

    Each purchase item creates:
    - One stock batch.
    - One purchase receipt stock movement.
    - An update to the product inventory balance.

    The entire operation is atomic.
    """

    if not isinstance(purchase, Purchase):
        raise ValidationError("A valid purchase is required.")

    try:
        purchase = (
            Purchase.objects
            .select_for_update()
            .get(pk=purchase.pk)
        )
    except Purchase.DoesNotExist:
        raise ValidationError("The selected purchase does not exist.")

    if purchase.status != Purchase.Status.DRAFT:
        raise ValidationError(
            "Only draft purchases can be received."
        )

    items = list(
        PurchaseItem.objects
        .select_for_update()
        .filter(purchase=purchase)
        .order_by("id")
    )

    if not items:
        raise ValidationError(
            "A purchase must contain at least one item before receiving."
        )

    if received_at is None:
        received_at = timezone.now()

    # Lock product records in a consistent order.
    # This helps prevent concurrent inventory updates from conflicting.
    product_ids = sorted({item.product_id for item in items})

    list(
        Product.objects
        .select_for_update()
        .filter(pk__in=product_ids)
        .order_by("pk")
    )

    # Allocate transport costs before calculating landed unit costs.
    allocate_transport_cost(purchase=purchase)

    # Reload allocations because the allocation service updates the database.
    for item in items:
        item.refresh_from_db(fields=["allocated_transport_cost"])

    received_batches = []

    for item in items:
        if item.product_id != item.packaging.product_id:
            raise ValidationError(
                "A purchase item has packaging belonging to another product."
            )

        base_quantity = item.base_quantity

        if base_quantity <= 0:
            raise ValidationError(
                "Purchase item quantity must be greater than zero."
            )

        landed_unit_cost = item.landed_unit_cost.quantize(
            SIX_DECIMAL_PLACES,
            rounding=ROUND_HALF_UP,
        )

        # 1. Create the stock batch.
        batch = StockBatch.objects.create(
            product=item.product,
            purchase_item=item,
            received_quantity=base_quantity,
            remaining_quantity=base_quantity,
            landed_unit_cost=landed_unit_cost,
            received_at=received_at,
        )

        # 2. Record the stock receipt in the movement ledger.
        StockMovement.objects.create(
            product=item.product,
            stock_batch=batch,
            movement_type=StockMovement.MovementType.PURCHASE_RECEIPT,
            direction=StockMovement.Direction.IN,
            quantity=base_quantity,
            unit_cost=landed_unit_cost,
            reference=f"PURCHASE-{purchase.pk}",
            notes="Stock received from supplier purchase.",
            created_by=purchase.created_by,
        )

        # 3. Create or update the product's current stock balance.
        InventoryBalance.objects.get_or_create(
            product=item.product,
            defaults={"quantity_on_hand": Decimal("0.000")},
        )

        balance = (
            InventoryBalance.objects
            .select_for_update()
            .get(product=item.product)
        )

        balance.quantity_on_hand += base_quantity
        balance.save(update_fields=["quantity_on_hand", "updated_at"])

        received_batches.append(batch)

    # Mark the purchase received only after all stock records are created.
    purchase.status = Purchase.Status.RECEIVED
    purchase.received_at = received_at
    purchase.save(
        update_fields=["status", "received_at", "updated_at"]
    )

    return received_batches
