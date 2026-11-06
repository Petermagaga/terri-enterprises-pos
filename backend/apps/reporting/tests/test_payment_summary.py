from datetime import date, datetime, time
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.reporting.services.date_ranges import DateRange
from apps.reporting.services.payment_summary import (
    calculate_payment_summary,
)
from apps.sales.models import Sale, SalePayment


pytestmark = pytest.mark.django_db


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="payment_report_cashier",
        email="paymentreport@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


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


def add_payment(
    sale,
    cashier,
    *,
    method,
    amount,
    reference="",
):
    return SalePayment.objects.create(
        sale=sale,
        payment_method=method,
        amount=Decimal(amount),
        reference=reference,
        received_by=cashier,
    )


def test_summarizes_cash_and_mpesa_collections(
    cashier,
    reporting_period,
):
    completed_at = timezone.make_aware(
        datetime.combine(date(2026, 11, 3), time(12, 0))
    )

    sale = create_sale(
        cashier,
        status=Sale.Status.COMPLETED,
        completed_at=completed_at,
    )

    add_payment(
        sale,
        cashier,
        method=SalePayment.PaymentMethod.CASH,
        amount="300.00",
    )

    add_payment(
        sale,
        cashier,
        method=SalePayment.PaymentMethod.MPESA,
        amount="700.00",
        reference="MPESA123456",
    )

    result = calculate_payment_summary(reporting_period)

    assert result["cash"]["total_amount"] == Decimal("300.00")
    assert result["cash"]["transaction_count"] == 1

    assert result["mpesa"]["total_amount"] == Decimal("700.00")
    assert result["mpesa"]["transaction_count"] == 1

    assert result["total_collections"] == Decimal("1000.00")
    assert result["total_transactions"] == 2


def test_summarizes_multiple_payments_of_same_method(
    cashier,
    reporting_period,
):
    completed_at = timezone.make_aware(
        datetime.combine(date(2026, 11, 3), time(12, 0))
    )

    sale = create_sale(
        cashier,
        status=Sale.Status.COMPLETED,
        completed_at=completed_at,
    )

    add_payment(
        sale,
        cashier,
        method=SalePayment.PaymentMethod.CASH,
        amount="200.00",
    )

    add_payment(
        sale,
        cashier,
        method=SalePayment.PaymentMethod.CASH,
        amount="150.00",
    )

    result = calculate_payment_summary(reporting_period)

    assert result["cash"]["total_amount"] == Decimal("350.00")
    assert result["cash"]["transaction_count"] == 2


def test_excludes_draft_and_voided_sales(
    cashier,
    reporting_period,
):
    completed_at = timezone.make_aware(
        datetime.combine(date(2026, 11, 3), time(12, 0))
    )

    for status, amount, reference in [
        (Sale.Status.COMPLETED, "500.00", ""),
        (Sale.Status.DRAFT, "300.00", ""),
        (Sale.Status.VOIDED, "200.00", ""),
    ]:
        sale = create_sale(
            cashier,
            status=status,
            completed_at=completed_at,
        )

        add_payment(
            sale,
            cashier,
            method=SalePayment.PaymentMethod.CASH,
            amount=amount,
        )

    result = calculate_payment_summary(reporting_period)

    assert result["cash"]["total_amount"] == Decimal("500.00")
    assert result["cash"]["transaction_count"] == 1
    assert result["total_collections"] == Decimal("500.00")


def test_returns_zero_totals_when_no_payments_exist(
    reporting_period,
):
    result = calculate_payment_summary(reporting_period)

    assert result["cash"]["total_amount"] == 0
    assert result["cash"]["transaction_count"] == 0

    assert result["mpesa"]["total_amount"] == 0
    assert result["mpesa"]["transaction_count"] == 0

    assert result["total_collections"] == 0
    assert result["total_transactions"] == 0