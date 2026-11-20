
from datetime import date, datetime, time
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.reporting.services.date_ranges import DateRange
from apps.reporting.services.category_performance import (
    calculate_category_performance,
)
from apps.sales.models import Sale, SaleItem


pytestmark = pytest.mark.django_db


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="category_performance_cashier",
        email="category-performance@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def category_products():
    groceries = Category.objects.create(name="Performance Groceries")
    beverages = Category.objects.create(name="Performance Beverages")

    oil_family = ProductFamily.objects.create(name="Performance Oil")
    juice_family = ProductFamily.objects.create(name="Performance Juice")

    oil = create_product(
        name="Performance Cooking Oil",
        product_family=oil_family,
        category=groceries,
        size_value=1000,
        size_unit="ML",
        base_unit="bottle",
        retail_price=250,
        wholesale_price=230,
    )

    juice = create_product(
        name="Performance Orange Juice",
        product_family=juice_family,
        category=beverages,
        size_value=500,
        size_unit="ML",
        base_unit="bottle",
        retail_price=100,
        wholesale_price=90,
    )

    return groceries, beverages, oil, juice


@pytest.fixture
def reporting_period():
    return DateRange(
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 6),
    )


def create_sale(cashier, *, status, completed_at=None):
    return Sale.objects.create(
        processed_by=cashier,
        status=status,
        completed_at=completed_at,
    )


def add_sale_item(
    sale,
    product,
    *,
    quantity,
    conversion_factor,
    total_amount,
    total_cost,
):
    return SaleItem.objects.create(
        sale=sale,
        product=product,
        product_name_snapshot=product.name,
        product_sku_snapshot=product.sku,
        base_unit_snapshot=product.base_unit,
        packaging_name_snapshot="Test Packaging",
        conversion_factor_snapshot=conversion_factor,
        pricing_type=SaleItem.PricingType.RETAIL,
        quantity=quantity,
        selling_price_per_package=Decimal("250.00"),
        total_amount=Decimal(total_amount),
        total_cost=Decimal(total_cost),
    )


def test_calculates_performance_for_multiple_categories(
    cashier,
    category_products,
    reporting_period,
):
    groceries, beverages, oil, juice = category_products

    completed_at = timezone.make_aware(
        datetime.combine(date(2026, 11, 3), time(12, 0))
    )

    sale = create_sale(
        cashier,
        status=Sale.Status.COMPLETED,
        completed_at=completed_at,
    )

    add_sale_item(
        sale,
        oil,
        quantity=2,
        conversion_factor=1,
        total_amount="500.00",
        total_cost="200.00",
    )

    add_sale_item(
        sale,
        juice,
        quantity=3,
        conversion_factor=1,
        total_amount="300.00",
        total_cost="150.00",
    )

    result = calculate_category_performance(reporting_period)

    assert len(result) == 2

    groceries_result = next(
        item for item in result
        if item["category_id"] == groceries.id
    )
    beverages_result = next(
        item for item in result
        if item["category_id"] == beverages.id
    )

    assert groceries_result["category_name"] == groceries.name
    assert groceries_result["quantity_sold"] == 2
    assert groceries_result["revenue"] == Decimal("500.00")
    assert groceries_result["cost_of_goods_sold"] == Decimal("200.00")
    assert groceries_result["gross_profit"] == Decimal("300.00")

    assert beverages_result["category_name"] == beverages.name
    assert beverages_result["quantity_sold"] == 3
    assert beverages_result["revenue"] == Decimal("300.00")
    assert beverages_result["cost_of_goods_sold"] == Decimal("150.00")
    assert beverages_result["gross_profit"] == Decimal("150.00")


def test_aggregates_multiple_products_in_the_same_category(
    cashier,
    category_products,
    reporting_period,
):
    groceries, _, oil, juice = category_products

    # Put both products in the same category for this test.
    juice.category = groceries
    juice.save(update_fields=["category"])

    completed_at = timezone.make_aware(
        datetime.combine(date(2026, 11, 3), time(12, 0))
    )

    sale = create_sale(
        cashier,
        status=Sale.Status.COMPLETED,
        completed_at=completed_at,
    )

    add_sale_item(
        sale,
        oil,
        quantity=2,
        conversion_factor=1,
        total_amount="500.00",
        total_cost="200.00",
    )

    add_sale_item(
        sale,
        juice,
        quantity=3,
        conversion_factor=1,
        total_amount="300.00",
        total_cost="150.00",
    )

    result = calculate_category_performance(reporting_period)

    assert len(result) == 1
    assert result[0]["category_id"] == groceries.id
    assert result[0]["quantity_sold"] == 5
    assert result[0]["revenue"] == Decimal("800.00")
    assert result[0]["cost_of_goods_sold"] == Decimal("350.00")
    assert result[0]["gross_profit"] == Decimal("450.00")


def test_converts_packaging_quantity_to_base_units(
    cashier,
    category_products,
    reporting_period,
):
    groceries, _, oil, _ = category_products

    completed_at = timezone.make_aware(
        datetime.combine(date(2026, 11, 3), time(12, 0))
    )

    sale = create_sale(
        cashier,
        status=Sale.Status.COMPLETED,
        completed_at=completed_at,
    )

    add_sale_item(
        sale,
        oil,
        quantity=2,
        conversion_factor=12,
        total_amount="6000.00",
        total_cost="2400.00",
    )

    result = calculate_category_performance(reporting_period)

    assert len(result) == 1
    assert result[0]["category_id"] == groceries.id
    assert result[0]["quantity_sold"] == 24
    assert result[0]["revenue"] == Decimal("6000.00")
    assert result[0]["gross_profit"] == Decimal("3600.00")


def test_excludes_draft_and_voided_sales(
    cashier,
    category_products,
    reporting_period,
):
    _, _, oil, _ = category_products

    completed_at = timezone.make_aware(
        datetime.combine(date(2026, 11, 3), time(12, 0))
    )

    for status, amount, cost in [
        (Sale.Status.COMPLETED, "500.00", "200.00"),
        (Sale.Status.DRAFT, "300.00", "100.00"),
        (Sale.Status.VOIDED, "400.00", "150.00"),
    ]:
        sale = create_sale(
            cashier,
            status=status,
            completed_at=completed_at,
        )

        add_sale_item(
            sale,
            oil,
            quantity=1,
            conversion_factor=1,
            total_amount=amount,
            total_cost=cost,
        )

    result = calculate_category_performance(reporting_period)

    assert len(result) == 1
    assert result[0]["revenue"] == Decimal("500.00")
    assert result[0]["cost_of_goods_sold"] == Decimal("200.00")
    assert result[0]["gross_profit"] == Decimal("300.00")


def test_includes_historical_sales_for_inactive_products_and_categories(
    cashier,
    category_products,
    reporting_period,
):
    groceries, _, oil, _ = category_products

    groceries.is_active = False
    groceries.save(update_fields=["is_active"])

    oil.is_active = False
    oil.save(update_fields=["is_active"])

    completed_at = timezone.make_aware(
        datetime.combine(date(2026, 11, 3), time(12, 0))
    )

    sale = create_sale(
        cashier,
        status=Sale.Status.COMPLETED,
        completed_at=completed_at,
    )

    add_sale_item(
        sale,
        oil,
        quantity=1,
        conversion_factor=1,
        total_amount="250.00",
        total_cost="100.00",
    )

    result = calculate_category_performance(reporting_period)

    assert len(result) == 1
    assert result[0]["category_id"] == groceries.id
    assert result[0]["category_name"] == groceries.name
    assert result[0]["gross_profit"] == Decimal("150.00")


def test_returns_empty_list_when_no_completed_sales_exist(
    reporting_period,
):
    result = calculate_category_performance(reporting_period)

    assert result == []
