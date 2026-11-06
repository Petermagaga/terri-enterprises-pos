from datetime import date, datetime, time
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.models import User
from apps.reporting.services.date_ranges import DateRange
from apps.reporting.services.sales_summary import (
    calculate_sales_summary,
)
from apps.sales.models import Sale


pytestmark = pytest.mark.django_db


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="sales_summary_cashier",
        email="salessummary@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def reporting_period():
    return DateRange(
        start_date=date(2025, 12, 31),
        end_date=date(2026, 4, 2),
    )


def create_sale(
    cashier,
    *,
    sale_date,
    status=Sale.Status.COMPLETED,
    revenue="500.00",
    cost="300.00",
):
    completed_at = timezone.make_aware(
        datetime.combine(sale_date, time(12, 0))
    )

    return Sale.objects.create(
        processed_by=cashier,
        status=status,
        completed_at=completed_at,
        total_amount=Decimal(revenue),
        total_cost=Decimal(cost),
    )


@pytest.mark.parametrize(
    "group_by, expected_periods",
    [
        (
            "daily",
            [
                date(2025, 12, 31),
                date(2026, 1, 1),
                date(2026, 4, 1),
                date(2026, 4, 2),
            ],
        ),
        (
            "weekly",
            [
                date(2025, 12, 29),
                date(2026, 3, 30),
            ],
        ),
        (
            "monthly",
            [
                date(2025, 12, 1),
                date(2026, 1, 1),
                date(2026, 4, 1),
            ],
        ),
        (
            "quarterly",
            [
                date(2025, 10, 1),
                date(2026, 1, 1),
                date(2026, 4, 1),
            ],
        ),
        (
            "yearly",
            [
                date(2025, 1, 1),
                date(2026, 1, 1),
            ],
        ),
    ],
)
def test_groups_sales_by_requested_period(
    cashier,
    reporting_period,
    group_by,
    expected_periods,
):
    sale_dates = [
        date(2025, 12, 31),
        date(2026, 1, 1),
        date(2026, 4, 1),
        date(2026, 4, 2),
    ]

    for sale_date in sale_dates:
        create_sale(cashier, sale_date=sale_date)

    result = calculate_sales_summary(
        reporting_period,
        group_by=group_by,
    )

    actual_periods = [
        item["period"].date()
        for item in result
    ]

    assert actual_periods == expected_periods

    assert sum(item["sale_count"] for item in result) == 4
    assert sum(
        (item["revenue"] for item in result),
        Decimal("0.00"),
    ) == Decimal("2000.00")

    assert sum(
        (item["cost_of_goods_sold"] for item in result),
        Decimal("0.00"),
    ) == Decimal("1200.00")

    assert sum(
        (item["gross_profit"] for item in result),
        Decimal("0.00"),
    ) == Decimal("800.00")


def test_excludes_draft_and_voided_sales(
    cashier,
    reporting_period,
):
    sale_date = date(2026, 1, 15)

    create_sale(
        cashier,
        sale_date=sale_date,
        status=Sale.Status.COMPLETED,
    )

    create_sale(
        cashier,
        sale_date=sale_date,
        status=Sale.Status.DRAFT,
        revenue="1000.00",
        cost="500.00",
    )

    create_sale(
        cashier,
        sale_date=sale_date,
        status=Sale.Status.VOIDED,
        revenue="2000.00",
        cost="1000.00",
    )

    result = calculate_sales_summary(
        reporting_period,
        group_by="monthly",
    )

    assert len(result) == 1
    assert result[0]["sale_count"] == 1
    assert result[0]["revenue"] == Decimal("500.00")
    assert result[0]["cost_of_goods_sold"] == Decimal("300.00")
    assert result[0]["gross_profit"] == Decimal("200.00")


def test_returns_empty_list_when_no_completed_sales_exist(
    reporting_period,
):
    result = calculate_sales_summary(reporting_period)

    assert result == []


def test_rejects_unsupported_grouping(reporting_period):
    with pytest.raises(ValidationError):
        calculate_sales_summary(
            reporting_period,
            group_by="hourly",
        )