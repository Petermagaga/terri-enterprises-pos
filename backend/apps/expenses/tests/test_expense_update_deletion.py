import pytest

from django.core.exceptions import PermissionDenied

from apps.accounts.models import User
from apps.expenses.models import Expense
from apps.expenses.services import (
    create_expense,
    update_expense,
    delete_expense,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    return User.objects.create_user(
        username="expense_update_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="expense_update_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def sample_expense(owner):
    return create_expense(
        description="Shop electricity bill",
        category=Expense.Category.ELECTRICITY,
        amount="2500.00",
        payment_method=Expense.PaymentMethod.MPESA,
        payment_reference="QWE123456",
        recorded_by=owner,
    )


# UPDATE PERMISSION TESTS

def test_cashier_cannot_update_expense(
    cashier,
    sample_expense,
):
    with pytest.raises(PermissionDenied):
        update_expense(
            expense=sample_expense,
            updated_by=cashier,
            description="Unauthorized change",
            category=Expense.Category.ELECTRICITY,
            amount="3000.00",
            expense_date=sample_expense.expense_date,
            payment_method=Expense.PaymentMethod.MPESA,
            payment_reference="NEW123456",
        )

    sample_expense.refresh_from_db()
    assert sample_expense.amount == 2500


def test_inactive_owner_cannot_update_expense(
    owner,
    sample_expense,
):
    owner.is_active = False
    owner.save()

    with pytest.raises(PermissionDenied):
        update_expense(
            expense=sample_expense,
            updated_by=owner,
            description="Unauthorized change",
            category=Expense.Category.ELECTRICITY,
            amount="3000.00",
            expense_date=sample_expense.expense_date,
            payment_method=Expense.PaymentMethod.MPESA,
            payment_reference="NEW123456",
        )

    sample_expense.refresh_from_db()
    assert sample_expense.amount == 2500


# DELETION PERMISSION TESTS

def test_cashier_cannot_delete_expense(
    cashier,
    sample_expense,
):
    with pytest.raises(PermissionDenied):
        delete_expense(
            expense=sample_expense,
            deleted_by=cashier,
        )

    assert Expense.objects.filter(pk=sample_expense.pk).exists()


def test_inactive_owner_cannot_delete_expense(
    owner,
    sample_expense,
):
    owner.is_active = False
    owner.save()

    with pytest.raises(PermissionDenied):
        delete_expense(
            expense=sample_expense,
            deleted_by=owner,
        )

    assert Expense.objects.filter(pk=sample_expense.pk).exists()