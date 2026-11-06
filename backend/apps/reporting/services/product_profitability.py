from datetime import datetime, time, timedelta

from django.db.models import (
    BigIntegerField,
    F,
    Sum,
)
from django.utils import timezone

from apps.reporting.services.date_ranges import DateRange
from apps.sales.models import SaleItem


def calculate_product_profitability(date_range: DateRange) -> list[dict]:
    """
    Calculate revenue, cost, gross profit and base units sold
    for each product within an inclusive reporting date range.

    Only completed sales are included.
    """

    start_datetime = timezone.make_aware(
        datetime.combine(date_range.start_date, time.min)
    )

    end_datetime_exclusive = timezone.make_aware(
        datetime.combine(
            date_range.end_date + timedelta(days=1),
            time.min,
        )
    )

    products = (
        SaleItem.objects.filter(
            sale__status="COMPLETED",
            sale__completed_at__gte=start_datetime,
            sale__completed_at__lt=end_datetime_exclusive,
        )
        .values(
            "product_id",
            product_name=F("product__name"),
            product_sku=F("product__sku"),
        )
        .annotate(
            quantity_sold=Sum(
                F("quantity") * F("conversion_factor_snapshot"),
                output_field=BigIntegerField(),
            ),
            revenue=Sum("total_amount"),
            cost_of_goods_sold=Sum("total_cost"),
            gross_profit=(
                Sum("total_amount") - Sum("total_cost")
            ),
        )
        .order_by("-gross_profit", "product_name")
    )

    return list(products)