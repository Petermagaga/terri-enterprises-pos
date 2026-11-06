
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from apps.expenses.models import Expense
from apps.reporting.services.date_ranges import DateRange
from apps.sales.models import Sale


ZERO = Decimal("0.00")


def calculate_profit_loss(date_range: DateRange) -> dict:
    """
    Calculate revenue, COGS, gross profit, expenses, and net profit
    for an inclusive reporting date range.

    Sale timestamps are filtered using Nairobi-aware datetime boundaries.
    Expenses are filtered using their local calendar dates.
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

    sales_totals = Sale.objects.filter(
        status=Sale.Status.COMPLETED,
        completed_at__gte=start_datetime,
        completed_at__lt=end_datetime_exclusive,
    ).aggregate(
        revenue=Sum("total_amount", default=ZERO),
        cost_of_goods_sold=Sum("total_cost", default=ZERO),
    )

    expense_totals = Expense.objects.filter(
        expense_date__range=(
            date_range.start_date,
            date_range.end_date,
        )
    ).aggregate(
        operating_expenses=Sum("amount", default=ZERO),
    )

    revenue = sales_totals["revenue"]
    cogs = sales_totals["cost_of_goods_sold"]
    operating_expenses = expense_totals["operating_expenses"]

    gross_profit = revenue - cogs
    net_profit = gross_profit - operating_expenses

    return {
        "start_date": date_range.start_date,
        "end_date": date_range.end_date,
        "sales_revenue": revenue,
        "cost_of_goods_sold": cogs,
        "gross_profit": gross_profit,
        "operating_expenses": operating_expenses,
        "net_profit": net_profit,
    }
