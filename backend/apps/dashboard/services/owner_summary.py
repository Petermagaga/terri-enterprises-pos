
from datetime import date, datetime, timedelta
from decimal import Decimal

from apps.reporting.services.date_ranges import get_date_range
from apps.reporting.services.profit_loss import calculate_profit_loss
from apps.reporting.services.category_performance import (
    calculate_category_performance,
)

from apps.reporting.services.payment_summary import (
    calculate_payment_summary,
)
from apps.dashboard.services.stock_summary import get_stock_summary
from apps.reporting.services.sales_summary import (
    calculate_sales_summary,
)
from apps.reporting.services.product_profitability import (
    calculate_product_profitability,
)
from apps.inventory.services.inventory_valuation import (
    get_inventory_valuation,
)


def build_daily_sales_trend(
    start_date: date,
    end_date: date,
    sales_series: list[dict],
) -> list[dict]:
    """
    Build a continuous daily sales trend, including dates
    without completed sales.
    """

    sales_by_date = {}

    for item in sales_series:
        period = item["period"]

        if isinstance(period, datetime):
            period = period.date()

        sales_by_date[period] = item

    trend = []
    current_date = start_date

    while current_date <= end_date:
        item = sales_by_date.get(current_date)

        trend.append({
            "period": current_date,
            "sale_count": item["sale_count"] if item else 0,
            "revenue": (
                item["revenue"] if item else Decimal("0.00")
            ),
            "cost_of_goods_sold": (
                item["cost_of_goods_sold"]
                if item else Decimal("0.00")
            ),
            "gross_profit": (
                item["gross_profit"]
                if item else Decimal("0.00")
            ),
        })

        current_date += timedelta(days=1)

    return trend


def get_owner_dashboard_summary(
    period: str = "this_week",
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    """
    Build the Owner dashboard summary for a selected reporting period.

    Financial and sales figures use the selected date range.
    Stock availability and inventory valuation represent current position.
    """

    date_range = get_date_range(
        preset=period,
        start_date=start_date,
        end_date=end_date,
    )

    financial_summary = calculate_profit_loss(date_range)
    payment_summary = calculate_payment_summary(date_range)

    sales_series = calculate_sales_summary(
        date_range,
        group_by="daily",
    )

    sales_trend = build_daily_sales_trend(
        date_range.start_date,
        date_range.end_date,
        sales_series,
    )

    stock_summary = get_stock_summary()
    inventory_valuation = get_inventory_valuation()

    top_products = calculate_product_profitability(
        date_range
    )[:5]
    category_performance = calculate_category_performance(
        date_range
    )


    sales_summary = {
        "sale_count": sum(
            item["sale_count"] for item in sales_trend
        ),
        "revenue": sum(
            (item["revenue"] for item in sales_trend),
            start=Decimal("0.00"),
        ),
        "cost_of_goods_sold": sum(
            (
                item["cost_of_goods_sold"]
                for item in sales_trend
            ),
            start=Decimal("0.00"),
        ),
        "gross_profit": sum(
            (item["gross_profit"] for item in sales_trend),
            start=Decimal("0.00"),
        ),
    }

    return {
        "date": date_range.end_date,
        "date_range": {
            "start_date": date_range.start_date,
            "end_date": date_range.end_date,
        },
        "financial_summary": financial_summary,
        "payment_summary": payment_summary,
        "sales_summary": sales_summary,
        "sales_trend": sales_trend,
        "stock_summary": stock_summary,
        "inventory_valuation": inventory_valuation,
        "top_products": top_products,
        "category_performance": category_performance,
    }
