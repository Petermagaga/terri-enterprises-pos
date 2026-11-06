from datetime import date, datetime, time
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.expenses.models import Expense
from apps.reporting.services.date_ranges import DateRange
from apps.reporting.services.profit_loss import calculate_profit_loss
from apps.sales.models import Sale


pytestmark = pytest.mark.django_db


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="reporting_cashier",
        email="reporting@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


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
    total_amount,
    total_cost,
    completed_at=None,
):
    return Sale.objects.create(
        processed_by=cashier,
        status=status,
        total_amount=Decimal(total_amount),
        total_cost=Decimal(total_cost),
        completed_at=completed_at,
    )


def create_expense(cashier, *, amount, expense_date):
    return Expense.objects.create(
        description="Reporting test expense",
        category=Expense.Category.OTHER,
        amount=Decimal(amount),
        expense_date=expense_date,
        payment_method=Expense.PaymentMethod.CASH,
        recorded_by=cashier,
    )


def test_calculates_profit_and_loss_for_date_range(
    cashier,
    reporting_period,
):
    first_day = timezone.make_aware(
        datetime.combine(date(2026, 11, 1), time(10, 0))
    )
    last_day = timezone.make_aware(
        datetime.combine(date(2026, 11, 6), time(18, 0))
    )

    create_sale(
        cashier,
        status=Sale.Status.COMPLETED,
        total_amount="1000.00",
        total_cost="600.00",
        completed_at=first_day,
    )

    create_sale(
        cashier,
        status=Sale.Status.COMPLETED,
        total_amount="500.00",
        total_cost="300.00",
        completed_at=last_day,
    )

    create_expense(
        cashier,
        amount="100.00",
        expense_date=date(2026, 11, 3),
    )

    result = calculate_profit_loss(reporting_period)

    assert result["sales_revenue"] == Decimal("1500.00")
    assert result["cost_of_goods_sold"] == Decimal("900.00")
    assert result["gross_profit"] == Decimal("600.00")
    assert result["operating_expenses"] == Decimal("100.00")
    assert result["net_profit"] == Decimal("500.00")


def test_excludes_draft_and_voided_sales(
    cashier,
    reporting_period,
):
    completed_at = timezone.make_aware(
        datetime.combine(date(2026, 11, 3), time(12, 0))
    )

    create_sale(
        cashier,
        status=Sale.Status.COMPLETED,
        total_amount="500.00",
        total_cost="300.00",
        completed_at=completed_at,
    )

    create_sale(
        cashier,
        status=Sale.Status.DRAFT,
        total_amount="200.00",
        total_cost="100.00",
    )

    create_sale(
        cashier,
        status=Sale.Status.VOIDED,
        total_amount="300.00",
        total_cost="150.00",
        completed_at=completed_at,
    )

    result = calculate_profit_loss(reporting_period)

    assert result["sales_revenue"] == Decimal("500.00")
    assert result["cost_of_goods_sold"] == Decimal("300.00")
    assert result["gross_profit"] == Decimal("200.00")


def test_excludes_sales_outside_date_range(
    cashier,
    reporting_period,
):
    before_period = timezone.make_aware(
        datetime.combine(date(2026, 10, 31), time(23, 59))
    )
    after_period = timezone.make_aware(
        datetime.combine(date(2026, 11, 7), time(0, 0))
    )

    create_sale(
        cashier,
        status=Sale.Status.COMPLETED,
        total_amount="1000.00",
        total_cost="500.00",
        completed_at=before_period,
    )

    create_sale(
        cashier,
        status=Sale.Status.COMPLETED,
        total_amount="2000.00",
        total_cost="1000.00",
        completed_at=after_period,
    )

    result = calculate_profit_loss(reporting_period)

    assert result["sales_revenue"] == Decimal("0.00")
    assert result["cost_of_goods_sold"] == Decimal("0.00")


def test_excludes_expenses_outside_date_range(
    cashier,
    reporting_period,
):
    create_expense(
        cashier,
        amount="100.00",
        expense_date=date(2026, 10, 31),
    )

    create_expense(
        cashier,
        amount="200.00",
        expense_date=date(2026, 11, 3),
    )

    create_expense(
        cashier,
        amount="300.00",
        expense_date=date(2026, 11, 7),
    )

    result = calculate_profit_loss(reporting_period)

    assert result["operating_expenses"] == Decimal("200.00")


def test_returns_zero_totals_when_no_records_exist(
    reporting_period,
):
    result = calculate_profit_loss(reporting_period)

    assert result["sales_revenue"] == Decimal("0.00")
    assert result["cost_of_goods_sold"] == Decimal("0.00")
    assert result["gross_profit"] == Decimal("0.00")
    assert result["operating_expenses"] == Decimal("0.00")
    assert result["net_profit"] == Decimal("0.00")