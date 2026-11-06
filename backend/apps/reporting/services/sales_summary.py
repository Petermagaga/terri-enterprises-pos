from datetime import datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.db.models.functions import (
    TruncDay,
    TruncWeek,
    TruncMonth,
    TruncQuarter,
    TruncYear,
)
from django.utils import timezone

from apps.reporting.services.date_ranges import DateRange
from apps.sales.models import Sale


GROUPING_OPTIONS = {
    "daily": TruncDay,
    "weekly": TruncWeek,
    "monthly": TruncMonth,
    "quarterly": TruncQuarter,
    "yearly": TruncYear,
}


ZERO = 0


def calculate_sales_summary(
    date_range: DateRange,
    group_by: str = "daily",
) -> list[dict]:
    """
    Summarize completed sales grouped by calendar period.

    Supported groupings:
        daily, weekly, monthly, quarterly, yearly

    Only periods containing completed sales are returned.
    """

    truncation_function = GROUPING_OPTIONS.get(group_by)

    if truncation_function is None:
        raise ValidationError(
            f"Unsupported sales grouping: {group_by}."
        )

    start_datetime = timezone.make_aware(
        datetime.combine(date_range.start_date, time.min)
    )

    end_datetime_exclusive = timezone.make_aware(
        datetime.combine(
            date_range.end_date + timedelta(days=1),
            time.min,
        )
    )

    sales = (
        Sale.objects.filter(
            status=Sale.Status.COMPLETED,
            completed_at__gte=start_datetime,
            completed_at__lt=end_datetime_exclusive,
        )
        .annotate(
            period=truncation_function(
                "completed_at",
                tzinfo=timezone.get_current_timezone(),
            )
        )
        .values("period")
        .annotate(
            sale_count=Count("id"),
            revenue=Sum("total_amount"),
            cost_of_goods_sold=Sum("total_cost"),
            gross_profit=(
                Sum("total_amount") - Sum("total_cost")
            ),
        )
        .order_by("period")
    )

    return list(sales)