from datetime import datetime, time, timedelta

from django.db.models import BigIntegerField, F, Sum
from django.utils import timezone

from apps.reporting.services.date_ranges import DateRange
from apps.sales.models import SaleItem


def calculate_category_performance(
    date_range: DateRange,
) -> list[dict]:
    start_datetime = timezone.make_aware(
        datetime.combine(date_range.start_date, time.min)
    )
    end_datetime_exclusive = timezone.make_aware(
        datetime.combine(
            date_range.end_date + timedelta(days=1),
            time.min,
        )
    )

    categories = (
        SaleItem.objects.filter(
            sale__status="COMPLETED",
            sale__completed_at__gte=start_datetime,
            sale__completed_at__lt=end_datetime_exclusive,
        )
        .values(
            "product__category_id",
            category_name=F("product__category__name"),
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
        .order_by("-gross_profit", "category_name")
    )

    return [
        {
            "category_id": item["product__category_id"],
            "category_name": item["category_name"],
            "quantity_sold": item["quantity_sold"],
            "revenue": item["revenue"],
            "cost_of_goods_sold": item["cost_of_goods_sold"],
            "gross_profit": item["gross_profit"],
        }
        for item in categories
    ]