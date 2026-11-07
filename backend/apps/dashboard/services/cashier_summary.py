from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone

from apps.dashboard.services.stock_summary import get_stock_summary
from apps.sales.models import Sale, SalePayment


ZERO_AMOUNT = Decimal("0.00")


def get_cashier_dashboard_summary(cashier) -> dict:
    """
    Build a dashboard summary containing only the authenticated
    cashier's sales and collections.
    """

    today = timezone.localdate()
    seven_days_ago = timezone.now() - timedelta(days=7)

    today_sales = Sale.objects.filter(
        processed_by=cashier,
        status=Sale.Status.COMPLETED,
        completed_at__date=today,
    )

    sales_totals = today_sales.aggregate(
        sale_count=Count("id"),
        revenue=Sum("total_amount"),
    )

    payments = SalePayment.objects.filter(
        sale__processed_by=cashier,
        sale__status=Sale.Status.COMPLETED,
        sale__completed_at__date=today,
    )

    payment_totals = payments.values("payment_method").annotate(
        total_amount=Sum("amount"),
        transaction_count=Count("id"),
    )

    payment_summary = {
        "cash": {
            "total_amount": ZERO_AMOUNT,
            "transaction_count": 0,
        },
        "mpesa": {
            "total_amount": ZERO_AMOUNT,
            "transaction_count": 0,
        },
    }

    for item in payment_totals:
        if item["payment_method"] == SalePayment.PaymentMethod.CASH:
            payment_summary["cash"] = {
                "total_amount": item["total_amount"],
                "transaction_count": item["transaction_count"],
            }

        elif item["payment_method"] == SalePayment.PaymentMethod.MPESA:
            payment_summary["mpesa"] = {
                "total_amount": item["total_amount"],
                "transaction_count": item["transaction_count"],
            }

    payment_summary["total_collections"] = (
        payment_summary["cash"]["total_amount"]
        + payment_summary["mpesa"]["total_amount"]
    )

    payment_summary["total_transactions"] = (
        payment_summary["cash"]["transaction_count"]
        + payment_summary["mpesa"]["transaction_count"]
    )

    recent_sales = Sale.objects.filter(
        processed_by=cashier,
        status=Sale.Status.COMPLETED,
        created_at__gte=seven_days_ago,
    ).order_by("-completed_at", "-id")[:10]

    return {
        "date": today,
        "sales_summary": {
            "sale_count": sales_totals["sale_count"],
            "revenue": sales_totals["revenue"] or ZERO_AMOUNT,
        },
        "payment_summary": payment_summary,
        "stock_summary": get_stock_summary(),
        "recent_sales": [
            {
                "id": sale.id,
                "receipt_number": sale.receipt_number,
                "total_amount": sale.total_amount,
                "completed_at": sale.completed_at,
            }
            for sale in recent_sales
        ],
    }