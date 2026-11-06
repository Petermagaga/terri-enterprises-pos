import pytest

from decimal import Decimal
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.expenses.models import Expense


pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    return User.objects.create_superuser(
        username="owner_expense",
        email="owner_expense@test.com",
        password="TestPassword123!",
    )


def test_create_cash_expense(owner):
    expense = Expense.objects.create(
        description="Shop rent",
        category=Expense.Category.RENT,
        amount=Decimal("15000.00"),
        payment_method=Expense.PaymentMethod.CASH,
        recorded_by=owner,
    )

    assert expense.amount == Decimal("15000.00")
    assert expense.payment_method == Expense.PaymentMethod.CASH
    assert expense.payment_reference == ""
    assert expense.recorded_by == owner


def test_create_mpesa_expense(owner):
    expense = Expense.objects.create(
        description="Electricity tokens",
        category=Expense.Category.ELECTRICITY,
        amount=Decimal("2500.00"),
        payment_method=Expense.PaymentMethod.MPESA,
        payment_reference="QWE123456",
        recorded_by=owner,
    )

    assert expense.payment_reference == "QWE123456"


def test_create_bank_expense(owner):
    expense = Expense.objects.create(
        description="Internet subscription",
        category=Expense.Category.INTERNET,
        amount=Decimal("3000.00"),
        payment_method=Expense.PaymentMethod.BANK,
        payment_reference="BANK123456",
        recorded_by=owner,
    )

    assert expense.payment_method == Expense.PaymentMethod.BANK


def test_mpesa_expense_requires_reference(owner):
    expense = Expense(
        description="Electricity tokens",
        category=Expense.Category.ELECTRICITY,
        amount=Decimal("2500.00"),
        payment_method=Expense.PaymentMethod.MPESA,
        recorded_by=owner,
    )

    with pytest.raises(ValidationError):
        expense.save()


def test_bank_expense_requires_reference(owner):
    expense = Expense(
        description="Internet subscription",
        category=Expense.Category.INTERNET,
        amount=Decimal("3000.00"),
        payment_method=Expense.PaymentMethod.BANK,
        recorded_by=owner,
    )

    with pytest.raises(ValidationError):
        expense.save()


def test_cash_expense_rejects_reference(owner):
    expense = Expense(
        description="Shop rent",
        category=Expense.Category.RENT,
        amount=Decimal("15000.00"),
        payment_method=Expense.PaymentMethod.CASH,
        payment_reference="CASH123",
        recorded_by=owner,
    )

    with pytest.raises(ValidationError):
        expense.save()


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("0.00"),
        Decimal("-100.00"),
    ],
)
def test_expense_rejects_non_positive_amount(owner, amount):
    expense = Expense(
        description="Invalid expense",
        category=Expense.Category.OTHER,
        amount=amount,
        payment_method=Expense.PaymentMethod.CASH,
        recorded_by=owner,
    )

    with pytest.raises(ValidationError):
        expense.save()