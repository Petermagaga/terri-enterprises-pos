import pytest

from django.core.exceptions import PermissionDenied

from apps.accounts.models import User
from apps.expenses.models import Expense
from apps.expenses.services import (
    create_expense,
    update_expense,
    delete_expense,
)


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        username="expense_permission_owner",
        password="test-password-123",
        role=User.Role.OWNER,
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


@pytest.mark.django_db
def test_create_expense_rejects_missing_user():
    with pytest.raises(PermissionDenied):
        create_expense(
            description="Shop rent",
            category=Expense.Category.RENT,
            amount="15000.00",
            payment_method=Expense.PaymentMethod.CASH,
            recorded_by=None,
        )


@pytest.mark.django_db
def test_update_expense_rejects_missing_user(
    sample_expense,
):
    with pytest.raises(PermissionDenied):
        update_expense(
            expense=sample_expense,
            updated_by=None,
            description="Updated electricity bill",
            category=Expense.Category.ELECTRICITY,
            amount="3000.00",
            expense_date=sample_expense.expense_date,
            payment_method=Expense.PaymentMethod.MPESA,
            payment_reference="NEW123456",
        )


@pytest.mark.django_db
def test_delete_expense_rejects_missing_user(
    sample_expense,
):
    with pytest.raises(PermissionDenied):
        delete_expense(
            expense=sample_expense,
            deleted_by=None,
        )

    assert Expense.objects.filter(pk=sample_expense.pk).exists()