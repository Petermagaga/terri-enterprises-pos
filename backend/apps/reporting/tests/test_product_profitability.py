from datetime import date, datetime, time
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.reporting.services.date_ranges import DateRange
from apps.reporting.services.product_profitability import (
    calculate_product_profitability,
)
from apps.sales.models import Sale, SaleItem


pytestmark = pytest.mark.django_db


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="profitability_cashier",
        email="profitability@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def products():
    category = Category.objects.create(
        name="Profitability Groceries"
    )

    cooking_oil_family = ProductFamily.objects.create(
        name="Profitability Cooking Oil"
    )

    juice_family = ProductFamily.objects.create(
        name="Profitability Juice"
    )

    cooking_oil = create_product(
        name="Cooking Oil 1L",
        product_family=cooking_oil_family,
        category=category,
        size_value=1000,
        size_unit="ML",
        base_unit="bottle",
        retail_price=250,
        wholesale_price=230,
    )

    juice = create_product(
        name="Orange Juice 500ml",
        product_family=juice_family,
        category=category,
        size_value=500,
        size_unit="ML",
        base_unit="bottle",
        retail_price=100,
        wholesale_price=90,
    )

    return cooking_oil, juice


@pytest.fixture
def reporting_period():
    return DateRange(
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 6),
    )


def create_sale(
    cashier,
    *,
    status,
    completed_at=None,
):
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


def test_calculates_profitability_for_multiple_products(
    cashier,
    products,
    reporting_period,
):
    cooking_oil, juice = products

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
        cooking_oil,
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

    result = calculate_product_profitability(reporting_period)

    assert len(result) == 2

    oil_result = next(
        item for item in result
        if item["product_id"] == cooking_oil.id
    )

    juice_result = next(
        item for item in result
        if item["product_id"] == juice.id
    )

    assert oil_result["product_name"] == cooking_oil.name
    assert oil_result["product_sku"] == cooking_oil.sku
    assert oil_result["quantity_sold"] == 2
    assert oil_result["revenue"] == Decimal("500.00")
    assert oil_result["cost_of_goods_sold"] == Decimal("200.00")
    assert oil_result["gross_profit"] == Decimal("300.00")

    assert juice_result["quantity_sold"] == 3
    assert juice_result["revenue"] == Decimal("300.00")
    assert juice_result["cost_of_goods_sold"] == Decimal("150.00")
    assert juice_result["gross_profit"] == Decimal("150.00")


def test_converts_packaging_quantity_to_base_units(
    cashier,
    products,
    reporting_period,
):
    cooking_oil, _ = products

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
        cooking_oil,
        quantity=2,
        conversion_factor=12,
        total_amount="6000.00",
        total_cost="2400.00",
    )

    result = calculate_product_profitability(reporting_period)

    assert result[0]["quantity_sold"] == 24
    assert result[0]["revenue"] == Decimal("6000.00")
    assert result[0]["gross_profit"] == Decimal("3600.00")


def test_excludes_draft_and_voided_sales(
    cashier,
    products,
    reporting_period,
):
    cooking_oil, _ = products

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
            cooking_oil,
            quantity=1,
            conversion_factor=1,
            total_amount=amount,
            total_cost=cost,
        )

    result = calculate_product_profitability(reporting_period)

    assert len(result) == 1
    assert result[0]["revenue"] == Decimal("500.00")
    assert result[0]["cost_of_goods_sold"] == Decimal("200.00")
    assert result[0]["gross_profit"] == Decimal("300.00")


def test_returns_empty_list_when_no_completed_sales_exist(
    reporting_period,
):
    result = calculate_product_profitability(reporting_period)

    assert result == []

   

