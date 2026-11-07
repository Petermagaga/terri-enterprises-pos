from decimal import Decimal

from django.db.models import Count, DecimalField, F, Q, Value
from django.db.models.functions import Coalesce

from apps.products.models import Product


ZERO_STOCK = Decimal("0.000")


def get_stock_summary() -> dict:
    """
    Summarize stock levels for active products.

    Low stock:
        Quantity is greater than zero and at or below reorder level.

    Out of stock:
        Quantity is zero or no inventory balance exists.
    """

    products = Product.objects.filter(
        is_active=True,
    ).annotate(
        stock_quantity=Coalesce(
            "inventory_balance__quantity_on_hand",
            Value(ZERO_STOCK),
            output_field=DecimalField(
                max_digits=15,
                decimal_places=3,
            ),
        )
    )

    summary = products.aggregate(
        total_products=Count("id"),
        low_stock_products=Count(
            "id",
            filter=Q(
                stock_quantity__gt=ZERO_STOCK,
                reorder_level__gt=0,
                stock_quantity__lte=F("reorder_level"),
            ),
        ),
        out_of_stock_products=Count(
            "id",
            filter=Q(stock_quantity=ZERO_STOCK),
        ),
    )

    return summary