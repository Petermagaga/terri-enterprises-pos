
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.inventory.models import Purchase, PurchaseItem


@transaction.atomic
def remove_purchase_item(*, purchase_item):
    """
    Remove an item from a draft purchase.

    Received purchases cannot be modified.
    Removing a draft item does not affect inventory.
    """

    if not isinstance(purchase_item, PurchaseItem):
        raise ValidationError("A valid purchase item is required.")

    try:
        item = (
            PurchaseItem.objects
            .select_for_update()
            .get(pk=purchase_item.pk)
        )
    except PurchaseItem.DoesNotExist:
        raise ValidationError("The purchase item does not exist.")

    # Lock the parent purchase before checking its status.
    try:
        purchase = (
            Purchase.objects
            .select_for_update()
            .get(pk=item.purchase_id)
        )
    except Purchase.DoesNotExist:
        raise ValidationError("The associated purchase does not exist.")

    if purchase.status != Purchase.Status.DRAFT:
        raise ValidationError(
            "Items can only be removed from draft purchases."
        )

    item.delete()
