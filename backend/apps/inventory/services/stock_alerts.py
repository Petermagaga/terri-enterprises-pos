from django.utils import timezone

from apps.inventory.models import InventoryBalance, StockAlert


def sync_product_stock_alert(*, product, quantity_on_hand=None):
    """
    Synchronize the persistent stock alert for one product.

    An alert is active when the product is active and:
    - Its stock is zero, or
    - Its reorder level is positive and stock is at/below that level.

    Existing unresolved alerts are updated rather than duplicated.
    Resolved alerts remain in history.
    """

    if quantity_on_hand is None:
        try:
            quantity_on_hand = (
                InventoryBalance.objects
                .only("quantity_on_hand")
                .get(product=product)
                .quantity_on_hand
            )
        except InventoryBalance.DoesNotExist:
            quantity_on_hand = 0

    should_alert = (
        product.is_active
        and (
            quantity_on_hand <= 0
            or (
                product.reorder_level > 0
                and quantity_on_hand <= product.reorder_level
            )
        )
    )

    active_alert = (
        StockAlert.objects
        .filter(
            product=product,
            resolved_at__isnull=True,
        )
        .first()
    )

    if should_alert:
        if active_alert is None:
            return StockAlert.objects.create(
                product=product,
                quantity_on_hand=quantity_on_hand,
                reorder_level=product.reorder_level,
            )

        changed_fields = []

        if active_alert.quantity_on_hand != quantity_on_hand:
            active_alert.quantity_on_hand = quantity_on_hand
            changed_fields.append("quantity_on_hand")

        if active_alert.reorder_level != product.reorder_level:
            active_alert.reorder_level = product.reorder_level
            changed_fields.append("reorder_level")

        if changed_fields:
            active_alert.save(update_fields=changed_fields)

        return active_alert

    if active_alert is not None:
        active_alert.resolved_at = timezone.now()
        active_alert.save(update_fields=["resolved_at"])

    return None
