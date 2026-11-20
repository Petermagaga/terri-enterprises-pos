
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
        "apps.dashboard.services.owner_summary.calculate_category_performance"
    )
    @patch(
        "apps.dashboard.services.owner_summary.get_inventory_valuation"
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
    def test_returns_weekly_financial_and_payment_summaries(
        self,

        mock_get_date_range,
        mock_calculate_profit_loss,
        mock_calculate_payment_summary,
        mock_calculate_sales_summary,
        mock_get_stock_summary,
        mock_calculate_product_profitability,
        mock_get_inventory_valuation,
        mock_calculate_category_performance,
    ):
        start = date(2026, 11, 2)
        end = date(2026, 11, 7)

        expected_range = DateRange(
            start_date=start,
            end_date=end,
        )

        expected_sales_summary = [
            {
                "period": date(2026, 11, 2),
                "sale_count": 3,
                "revenue": Decimal("6000.00"),
                "cost_of_goods_sold": Decimal("4200.00"),
                "gross_profit": Decimal("1800.00"),
            },
            {
                "period": date(2026, 11, 5),
                "sale_count": 2,
                "revenue": Decimal("4000.00"),
                "cost_of_goods_sold": Decimal("2800.00"),
                "gross_profit": Decimal("1200.00"),
            },
        ]

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

        expected_inventory_valuation = {
            "total_inventory_value": Decimal("25000.00"),
            "products_with_stock": 10,
            "products": [],
        }
        mock_calculate_category_performance.return_value = []

        mock_calculate_product_profitability.return_value = (
            expected_top_products
        )
        mock_get_inventory_valuation.return_value = (
            expected_inventory_valuation
        )
        mock_get_date_range.return_value = expected_range
        mock_calculate_profit_loss.return_value = (
            expected_financial_summary
        )
        mock_calculate_payment_summary.return_value = (
            expected_payment_summary
        )
        mock_calculate_sales_summary.return_value = (
            expected_sales_summary
        )
        mock_get_stock_summary.return_value = {
            "total_products": 20,
            "low_stock_products": 3,
            "out_of_stock_products": 2,
        }

        result = get_owner_dashboard_summary()

        mock_get_date_range.assert_called_once_with(
            preset="this_week",
            start_date=None,
            end_date=None,
        )

        mock_calculate_profit_loss.assert_called_once_with(
            expected_range
        )
        mock_calculate_payment_summary.assert_called_once_with(
            expected_range
        )
        mock_calculate_sales_summary.assert_called_once_with(
            expected_range,
            group_by="daily",
        )
        mock_calculate_product_profitability.assert_called_once_with(
            expected_range
        )

        self.assertEqual(result["date"], end)
        self.assertEqual(
            result["date_range"],
            {
                "start_date": start,
                "end_date": end,
            },
        )

        self.assertEqual(
            result["sales_summary"],
            {
                "sale_count": 5,
                "revenue": Decimal("10000.00"),
                "cost_of_goods_sold": Decimal("7000.00"),
                "gross_profit": Decimal("3000.00"),
            },
        )

        self.assertEqual(
            result["sales_trend"],
            [
                {
                    "period": date(2026, 11, 2),
                    "sale_count": 3,
                    "revenue": Decimal("6000.00"),
                    "cost_of_goods_sold": Decimal("4200.00"),
                    "gross_profit": Decimal("1800.00"),
                },
                {
                    "period": date(2026, 11, 3),
                    "sale_count": 0,
                    "revenue": Decimal("0.00"),
                    "cost_of_goods_sold": Decimal("0.00"),
                    "gross_profit": Decimal("0.00"),
                },
                {
                    "period": date(2026, 11, 4),
                    "sale_count": 0,
                    "revenue": Decimal("0.00"),
                    "cost_of_goods_sold": Decimal("0.00"),
                    "gross_profit": Decimal("0.00"),
                },
                {
                    "period": date(2026, 11, 5),
                    "sale_count": 2,
                    "revenue": Decimal("4000.00"),
                    "cost_of_goods_sold": Decimal("2800.00"),
                    "gross_profit": Decimal("1200.00"),
                },
                {
                    "period": date(2026, 11, 6),
                    "sale_count": 0,
                    "revenue": Decimal("0.00"),
                    "cost_of_goods_sold": Decimal("0.00"),
                    "gross_profit": Decimal("0.00"),
                },
                {
                    "period": date(2026, 11, 7),
                    "sale_count": 0,
                    "revenue": Decimal("0.00"),
                    "cost_of_goods_sold": Decimal("0.00"),
                    "gross_profit": Decimal("0.00"),
                },
            ],
        )
        self.assertEqual(
            result["financial_summary"],
            expected_financial_summary,
        )
        self.assertEqual(
            result["payment_summary"],
            expected_payment_summary,
        )
        self.assertEqual(
            result["top_products"],
            expected_top_products,
        )
        self.assertEqual(
            result["stock_summary"],
            {
                "total_products": 20,
                "low_stock_products": 3,
                "out_of_stock_products": 2,
            },
        )
        self.assertEqual(
            result["inventory_valuation"],
            expected_inventory_valuation,
        )
    @patch(
        "apps.dashboard.services.owner_summary.calculate_category_performance"
    )

    @patch(
        "apps.dashboard.services.owner_summary.get_inventory_valuation"
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
        mock_get_inventory_valuation,
        mock_calculate_category_performance,
    ):
        today = date(2026, 11, 7)
        expected_range = DateRange(today, today)
        mock_calculate_category_performance.return_value = []
        mock_get_date_range.return_value = expected_range
        mock_calculate_profit_loss.return_value = {}
        mock_calculate_payment_summary.return_value = {}
        mock_calculate_sales_summary.return_value = []
        mock_calculate_product_profitability.return_value = []
        mock_get_stock_summary.return_value = {
            "total_products": 20,
            "low_stock_products": 3,
            "out_of_stock_products": 2,
        }
        mock_get_inventory_valuation.return_value = {
            "total_inventory_value": Decimal("25000.00"),
            "products_with_stock": 10,
            "products": [],
        }

        result = get_owner_dashboard_summary()

        self.assertEqual(
            result["sales_summary"],
            {
                "sale_count": 0,
                "revenue": 0,
                "cost_of_goods_sold": 0,
                "gross_profit": 0,
            },
        )

        self.assertEqual(
            result["sales_trend"],
            [
                {
                    "period": today,
                    "sale_count": 0,
                    "revenue": Decimal("0.00"),
                    "cost_of_goods_sold": Decimal("0.00"),
                    "gross_profit": Decimal("0.00"),
                },
            ],
        )
        self.assertEqual(result["top_products"], [])

    @patch(
        "apps.dashboard.services.owner_summary.calculate_category_performance"
    )

    @patch(
        "apps.dashboard.services.owner_summary.get_inventory_valuation"
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
    def test_passes_custom_date_range_to_reporting_services(
        self,
        mock_get_date_range,
        mock_calculate_profit_loss,
        mock_calculate_payment_summary,
        mock_calculate_sales_summary,
        mock_get_stock_summary,
        mock_calculate_product_profitability,
        mock_get_inventory_valuation,
        mock_calculate_category_performance,
    ):
        start = date(2026, 11, 1)
        end = date(2026, 11, 6)
        expected_range = DateRange(start, end)

        mock_get_date_range.return_value = expected_range
        mock_calculate_profit_loss.return_value = {}
        mock_calculate_payment_summary.return_value = {}
        mock_calculate_sales_summary.return_value = []
        mock_calculate_category_performance.return_value = []
        mock_calculate_product_profitability.return_value = []
        mock_get_stock_summary.return_value = {}
        mock_get_inventory_valuation.return_value = {}

        get_owner_dashboard_summary(
            period="custom",
            start_date=start,
            end_date=end,
        )

        mock_get_date_range.assert_called_once_with(
            preset="custom",
            start_date=start,
            end_date=end,
        )

        mock_calculate_profit_loss.assert_called_once_with(
            expected_range
        )
        mock_calculate_payment_summary.assert_called_once_with(
            expected_range
        )
        mock_calculate_category_performance.assert_called_once_with(
            expected_range
        )