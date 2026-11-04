from decimal import Decimal, ROUND_DOWN

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.inventory.models import Purchase, PurchaseItem


CENT = Decimal("0.01")


@transaction.atomic
def allocate_transport_cost(*, purchase):
    """
    Allocate purchase transport costs proportionally by item subtotal.

    Uses the largest-remainder method to distribute rounding cents
    without losing or creating any money.
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
            "Transport costs can only be allocated to draft purchases."
        )

    items = list(
        PurchaseItem.objects
        .select_for_update()
        .filter(purchase=purchase)
        .order_by("id")
    )

    if not items:
        if purchase.transport_cost > 0:
            raise ValidationError(
                "Cannot allocate transport costs without purchase items."
            )
        return []

    total_subtotal = sum(
        (item.line_subtotal for item in items),
        Decimal("0.00"),
    )

    if purchase.transport_cost == 0:
        for item in items:
            if item.allocated_transport_cost != Decimal("0.00"):
                item.allocated_transport_cost = Decimal("0.00")
                item.save(update_fields=["allocated_transport_cost"])

        return items

    if total_subtotal <= 0:
        raise ValidationError(
            "Cannot allocate transport costs when the purchase subtotal is zero."
        )

    eligible_items = [
        item for item in items
        if item.line_subtotal > 0
    ]

    allocations = {}
    remainders = {}

    allocated_total = Decimal("0.00")

    # First allocate each item's share rounded down to cents.
    for item in eligible_items:
        exact_share = (
            purchase.transport_cost
            * item.line_subtotal
            / total_subtotal
        )

        rounded_share = exact_share.quantize(
            CENT,
            rounding=ROUND_DOWN,
        )

        allocations[item.pk] = rounded_share
        remainders[item.pk] = exact_share - rounded_share
        allocated_total += rounded_share

    # Distribute remaining cents to the largest fractional remainders.
    remaining_cents = int(
        (purchase.transport_cost - allocated_total) / CENT
    )

    ranked_items = sorted(
        eligible_items,
        key=lambda item: (-remainders[item.pk], item.pk),
    )

    for item in ranked_items[:remaining_cents]:
        allocations[item.pk] += CENT

    # Zero-value lines receive no transport allocation.
    for item in items:
        item.allocated_transport_cost = allocations.get(
            item.pk,
            Decimal("0.00"),
        )
        item.save(update_fields=["allocated_transport_cost"])

    return items