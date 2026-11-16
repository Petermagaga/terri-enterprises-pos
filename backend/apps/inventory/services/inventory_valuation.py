from decimal import Decimal, ROUND_HALF_UP

from django.db.models import DecimalField, F, Sum

from apps.inventory.models import StockBatch


ZERO = Decimal("0")
MONEY_PLACES = Decimal("0.01")
UNIT_COST_PLACES = Decimal("0.000001")


def _money(value):
    return value.quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP,
    )


def get_inventory_valuation():
    """
    Calculate the current value of unsold inventory at landed cost.

    Uses remaining StockBatch quantities, so FIFO deductions,
    damage and stock reductions are automatically excluded.

    Landed unit costs already include allocated purchase transport
    costs. Adjustment-in batches use the owner's recorded unit cost.
    """

    batch_totals = (
        StockBatch.objects
        .filter(remaining_quantity__gt=ZERO)
        .values(
            "product_id",
            "product__name",
            "product__sku",
            "product__base_unit",
            "product__is_active",
        )
        .annotate(
            quantity_on_hand=Sum("remaining_quantity"),
            stock_value=Sum(
                F("remaining_quantity") * F("landed_unit_cost"),
                output_field=DecimalField(
                    max_digits=30,
                    decimal_places=6,
                ),
            ),
        )
        .order_by("product__name", "product__sku")
    )

    products = []
    total_value = ZERO

    for item in batch_totals:
        quantity = item["quantity_on_hand"] or ZERO
        stock_value = item["stock_value"] or ZERO

        if quantity <= ZERO:
            continue

        average_unit_cost = (
            stock_value / quantity
        ).quantize(
            UNIT_COST_PLACES,
            rounding=ROUND_HALF_UP,
        )

        total_value += stock_value

        products.append({
            "product_id": item["product_id"],
            "product_name": item["product__name"],
            "product_sku": item["product__sku"],
            "base_unit": item["product__base_unit"],
            "is_active": item["product__is_active"],
            "quantity_on_hand": quantity,
            "unit_cost": average_unit_cost,
            "stock_value": _money(stock_value),
        })

    return {
        "total_inventory_value": _money(total_value),
        "products_with_stock": len(products),
        "products": products,
    }
