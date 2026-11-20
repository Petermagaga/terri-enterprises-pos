
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from apps.expenses.models import Expense
from apps.reporting.services.date_ranges import DateRange
from apps.sales.models import Sale

from django.db import models

ZERO = Decimal("0.00")


def calculate_profit_loss(date_range: DateRange) -> dict:
    """
    Calculate revenue, COGS, gross profit, and expense classifications
    for an inclusive reporting date range.

    Only operating expenses reduce ordinary operating net profit.
    Setup and capital expenses are reported separately.
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

    expenses = Expense.objects.filter(
        expense_date__range=(
            date_range.start_date,
            date_range.end_date,
        )
    )

    expense_totals = expenses.aggregate(
        operating_expenses=Sum(
            "amount",
            filter=models.Q(expense_type=Expense.ExpenseType.OPERATING),
            default=ZERO,
        ),
        setup_expenses=Sum(
            "amount",
            filter=models.Q(expense_type=Expense.ExpenseType.SETUP),
            default=ZERO,
        ),
        capital_expenses=Sum(
            "amount",
            filter=models.Q(expense_type=Expense.ExpenseType.CAPITAL),
            default=ZERO,
        ),
    )

    revenue = sales_totals["revenue"]
    cogs = sales_totals["cost_of_goods_sold"]

    operating_expenses = expense_totals["operating_expenses"]
    setup_expenses = expense_totals["setup_expenses"]
    capital_expenses = expense_totals["capital_expenses"]

    gross_profit = revenue - cogs
    net_profit = gross_profit - operating_expenses

    return {
        "start_date": date_range.start_date,
        "end_date": date_range.end_date,
        "sales_revenue": revenue,
        "cost_of_goods_sold": cogs,
        "gross_profit": gross_profit,
        "operating_expenses": operating_expenses,
        "setup_expenses": setup_expenses,
        "capital_expenses": capital_expenses,
        "net_profit": net_profit,
    }
