from datetime import datetime, time, timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from apps.reporting.services.date_ranges import DateRange
from apps.sales.models import SalePayment


ZERO = 0


def calculate_payment_summary(date_range: DateRange) -> dict:
    """
    Summarize cash and M-Pesa collections for completed sales
    within an inclusive reporting date range.
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

    payments = SalePayment.objects.filter(
        sale__status="COMPLETED",
        sale__completed_at__gte=start_datetime,
        sale__completed_at__lt=end_datetime_exclusive,
    )

    summary = payments.values("payment_method").annotate(
        total_amount=Sum("amount"),
        transaction_count=Count("id"),
    )

    result = {
        "cash": {
            "total_amount": 0,
            "transaction_count": 0,
        },
        "mpesa": {
            "total_amount": 0,
            "transaction_count": 0,
        },
    }

    for item in summary:
        if item["payment_method"] == SalePayment.PaymentMethod.CASH:
            result["cash"] = {
                "total_amount": item["total_amount"],
                "transaction_count": item["transaction_count"],
            }

        elif item["payment_method"] == SalePayment.PaymentMethod.MPESA:
            result["mpesa"] = {
                "total_amount": item["total_amount"],
                "transaction_count": item["transaction_count"],
            }

    result["total_collections"] = (
        result["cash"]["total_amount"]
        + result["mpesa"]["total_amount"]
    )

    result["total_transactions"] = (
        result["cash"]["transaction_count"]
        + result["mpesa"]["transaction_count"]
    )

    return result