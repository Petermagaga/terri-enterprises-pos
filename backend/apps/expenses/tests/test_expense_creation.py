import pytest

from decimal import Decimal
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from apps.accounts.models import User
from apps.expenses.models import Expense
from apps.expenses.services.expense_creation import create_expense


pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    return User.objects.create_superuser(
        username="owner_creation",
        email="owner_creation@test.com",
        password="TestPassword123!",
    )


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="cashier_creation",
        email="cashier_creation@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


def test_owner_can_create_expense(owner):
    expense = create_expense(
        description="Shop rent",
        category=Expense.Category.RENT,
        amount=Decimal("15000.00"),
        payment_method=Expense.PaymentMethod.CASH,
        recorded_by=owner,
    )

    assert expense.recorded_by == owner
    assert expense.amount == Decimal("15000.00")
    assert expense.expense_date == timezone.localdate()


def test_cashier_cannot_create_expense(cashier):
    with pytest.raises(PermissionDenied):
        create_expense(
            description="Shop rent",
            category=Expense.Category.RENT,
            amount=Decimal("15000.00"),
            payment_method=Expense.PaymentMethod.CASH,
            recorded_by=cashier,
        )


def test_inactive_owner_cannot_create_expense(owner):
    owner.is_active = False
    owner.save()

    with pytest.raises(PermissionDenied):
        create_expense(
            description="Shop rent",
            category=Expense.Category.RENT,
            amount=Decimal("15000.00"),
            payment_method=Expense.PaymentMethod.CASH,
            recorded_by=owner,
        )