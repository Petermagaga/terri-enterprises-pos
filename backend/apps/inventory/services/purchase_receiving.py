
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.inventory.models import Purchase, PurchaseItem, StockBatch
from apps.inventory.services.transport_allocation import (
    allocate_transport_cost,
)


SIX_DECIMAL_PLACES = Decimal("0.000001")


@transaction.atomic
def receive_purchase(*, purchase, received_at=None):
    """
    Receive a draft purchase into inventory.

    Each purchase item creates one stock batch.
    Transport costs are allocated before batch valuation.
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

        batch = StockBatch.objects.create(
            product=item.product,
            purchase_item=item,
            received_quantity=base_quantity,
            remaining_quantity=base_quantity,
            landed_unit_cost=landed_unit_cost,
            received_at=received_at,
        )

        received_batches.append(batch)

    purchase.status = Purchase.Status.RECEIVED
    purchase.received_at = received_at
    purchase.save(update_fields=["status", "received_at", "updated_at"])

    return received_batches