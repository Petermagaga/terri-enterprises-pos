from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.dashboard.services.owner_summary import (
    get_owner_dashboard_summary,
)
from apps.reporting.services.date_ranges import DateRange


class OwnerDashboardSummaryTests(SimpleTestCase):

    @patch(
        "apps.dashboard.services.owner_summary.calculate_product_profitability"
    )
    @patch(
        "apps.dashboard.services.owner_summary.get_stock_summary"
    )
    @patch(
        "apps.dashboard.services.owner_summary.calculate_sales_summary"
    )
    @patch(
        "apps.dashboard.services.owner_summary.calculate_payment_summary"
    )
    @patch(
        "apps.dashboard.services.owner_summary.calculate_profit_loss"
    )
    @patch(
        "apps.dashboard.services.owner_summary.get_date_range"
    )
    def test_returns_today_financial_and_payment_summaries(
        self,
        
        mock_get_date_range,
        mock_calculate_profit_loss,
        mock_calculate_payment_summary,
        mock_calculate_sales_summary,
        mock_get_stock_summary,
        mock_calculate_product_profitability,
    ):
        today = date(2026, 11, 7)

        expected_range = DateRange(
            start_date=today,
            end_date=today,
        )

        expected_sales_summary = [{
            "sale_count": 5,
            "revenue": Decimal("10000.00"),
            "cost_of_goods_sold": Decimal("7000.00"),
            "gross_profit": Decimal("3000.00"),
        }]

        mock_calculate_sales_summary.return_value = (
            expected_sales_summary
        )

        expected_financial_summary = {
            "sales_revenue": Decimal("10000.00"),
            "cost_of_goods_sold": Decimal("7000.00"),
            "gross_profit": Decimal("3000.00"),
            "operating_expenses": Decimal("500.00"),
            "net_profit": Decimal("2500.00"),
        }

        expected_payment_summary = {
            "cash": {
                "total_amount": Decimal("6000.00"),
                "transaction_count": 3,
            },
            "mpesa": {
                "total_amount": Decimal("4000.00"),
                "transaction_count": 2,
            },
            "total_collections": Decimal("10000.00"),
            "total_transactions": 5,
        }

        expected_top_products = [
            {
                "product_id": 1,
                "product_name": "Margarine 500G",
                "product_sku": "MARG-500G",
                "quantity_sold": 10,
                "revenue": Decimal("2000.00"),
                "cost_of_goods_sold": Decimal("1500.00"),
                "gross_profit": Decimal("500.00"),
            }
        ]

        mock_calculate_product_profitability.return_value = (
            expected_top_products
        )


        mock_get_date_range.return_value = expected_range
        mock_calculate_profit_loss.return_value = (
            expected_financial_summary
        )
        mock_calculate_payment_summary.return_value = (
            expected_payment_summary
        )

        mock_get_stock_summary.return_value = {
            "total_products": 20,
            "low_stock_products": 3,
            "out_of_stock_products": 2,
        }
        result = get_owner_dashboard_summary()

        mock_calculate_product_profitability.assert_called_once_with(
            expected_range
        )

        self.assertEqual(
            result["top_products"],
            expected_top_products,
        )

        mock_calculate_sales_summary.assert_called_once_with(
            expected_range,
            group_by="daily",
        )

        self.assertEqual(
            result["sales_summary"],
            expected_sales_summary[0],
        )

        mock_get_date_range.assert_called_once_with("today")
        mock_calculate_profit_loss.assert_called_once_with(
            expected_range
        )
        mock_calculate_payment_summary.assert_called_once_with(
            expected_range
        )

        self.assertEqual(result["date"], today)
        self.assertEqual(
            result["financial_summary"],
            expected_financial_summary,
        )
        self.assertEqual(
            result["payment_summary"],
            expected_payment_summary,
        )

        self.assertEqual(
            result["stock_summary"],
            {
                "total_products": 20,
                "low_stock_products": 3,
                "out_of_stock_products": 2,
            },
        )

    @patch(
        "apps.dashboard.services.owner_summary.calculate_product_profitability"
    )

    @patch(
    "apps.dashboard.services.owner_summary.get_stock_summary"
)

    @patch(
        "apps.dashboard.services.owner_summary.calculate_sales_summary"
    )
    @patch(
        "apps.dashboard.services.owner_summary.calculate_payment_summary"
    )
    @patch(
        "apps.dashboard.services.owner_summary.calculate_profit_loss"
    )
    @patch(
        "apps.dashboard.services.owner_summary.get_date_range"
    )
    def test_returns_zero_sales_when_no_sales_exist(
        self,
        mock_get_date_range,
        mock_calculate_profit_loss,
        mock_calculate_payment_summary,
        mock_calculate_sales_summary,
        mock_get_stock_summary,
        mock_calculate_product_profitability,
    ):
        today = date(2026, 11, 7)

        expected_range = DateRange(today, today)

        expected_top_products = [
            {
                "product_id": 1,
                "product_name": "Margarine 500G",
                "product_sku": "MARG-500G",
                "quantity_sold": 10,
                "revenue": Decimal("2000.00"),
                "cost_of_goods_sold": Decimal("1500.00"),
                "gross_profit": Decimal("500.00"),
            }
        ]

        mock_calculate_product_profitability.return_value = (
            expected_top_products
        )


        mock_get_date_range.return_value = expected_range
        mock_calculate_profit_loss.return_value = {}
        mock_calculate_payment_summary.return_value = {}
        mock_calculate_sales_summary.return_value = []
        mock_get_stock_summary.return_value = {
            "total_products": 20,
            "low_stock_products": 3,
            "out_of_stock_products": 2,
        }
        result = get_owner_dashboard_summary()

        mock_calculate_product_profitability.assert_called_once_with(
            expected_range
        )

        self.assertEqual(
            result["top_products"],
            expected_top_products,
        )


        self.assertEqual(
            result["sales_summary"],
            {
                "sale_count": 0,
                "revenue": 0,
                "cost_of_goods_sold": 0,
                "gross_profit": 0,
            },
        )