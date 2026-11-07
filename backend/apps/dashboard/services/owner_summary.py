from apps.reporting.services.date_ranges import get_date_range
from apps.reporting.services.profit_loss import calculate_profit_loss
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

def get_owner_dashboard_summary() -> dict:
    """
    Build the Owner dashboard's daily financial and sales summary.
    """

    date_range = get_date_range("today")

    financial_summary = calculate_profit_loss(date_range)
    payment_summary = calculate_payment_summary(date_range)

    sales_summary = calculate_sales_summary(
        date_range,
        group_by="daily",
    )
    stock_summary = get_stock_summary()
    top_products = calculate_product_profitability(date_range)[:5]

    today_sales = sales_summary[0] if sales_summary else {
        "sale_count": 0,
        "revenue": 0,
        "cost_of_goods_sold": 0,
        "gross_profit": 0,
    }

    return {
        "date": date_range.start_date,
        "financial_summary": financial_summary,
        "payment_summary": payment_summary,
        "sales_summary": today_sales,
        "stock_summary": stock_summary,
        "top_products": top_products,
    }