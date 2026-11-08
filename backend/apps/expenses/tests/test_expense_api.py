import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.expenses.models import Expense
from apps.expenses.services import create_expense


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        username="expense_api_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="expense_api_cashier",
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


# AUTHENTICATION TESTS

@pytest.mark.django_db
def test_unauthenticated_user_cannot_view_expenses(api_client):
    response = api_client.get(reverse("expense-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_expense(api_client):
    response = api_client.post(
        reverse("expense-list"),
        {
            "description": "Shop rent",
            "category": "RENT",
            "amount": "15000.00",
            "payment_method": "CASH",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Expense.objects.count() == 0


# CASHIER ACCESS RESTRICTION TESTS

@pytest.mark.django_db
def test_cashier_cannot_view_expenses(api_client, cashier):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(reverse("expense-list"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_cashier_cannot_create_expenses(api_client, cashier):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("expense-list"),
        {
            "description": "Shop rent",
            "category": "RENT",
            "amount": "15000.00",
            "payment_method": "CASH",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Expense.objects.count() == 0



# OWNER ACCESS AND CREATION TESTS

@pytest.mark.django_db
def test_owner_can_create_expense(api_client, owner):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("expense-list"),
        {
            "description": "Monthly shop rent",
            "category": "RENT",
            "amount": "15000.00",
            "payment_method": "CASH",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["description"] == "Monthly shop rent"
    assert response.data["recorded_by"] == owner.pk

    expense = Expense.objects.get(pk=response.data["id"])
    assert expense.recorded_by == owner


@pytest.mark.django_db
def test_owner_can_view_expense_list(
    api_client,
    owner,
    sample_expense,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(reverse("expense-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == sample_expense.pk

@pytest.mark.django_db
def test_owner_can_retrieve_expense(
    api_client,
    owner,
    sample_expense,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("expense-detail", args=[sample_expense.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["description"] == "Shop electricity bill"
    assert response.data["amount"] == "2500.00"
    assert response.data["recorded_by"] == owner.pk


@pytest.mark.django_db
def test_client_cannot_override_recorded_by(
    api_client,
    owner,
    cashier,
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("expense-list"),
        {
            "description": "Shop rent",
            "category": "RENT",
            "amount": "15000.00",
            "payment_method": "CASH",
            "recorded_by": cashier.pk,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["recorded_by"] == owner.pk

    expense = Expense.objects.get(pk=response.data["id"])
    assert expense.recorded_by == owner

# EXPENSE UPDATE TESTS

@pytest.mark.django_db
def test_owner_can_update_expense(
    api_client,
    owner,
    sample_expense,
):
    api_client.force_authenticate(user=owner)

    response = api_client.put(
        reverse("expense-detail", args=[sample_expense.pk]),
        {
            "description": "Updated electricity bill",
            "category": "ELECTRICITY",
            "amount": "3000.00",
            "expense_date": str(sample_expense.expense_date),
            "payment_method": "MPESA",
            "payment_reference": "NEW123456",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["description"] == "Updated electricity bill"
    assert response.data["amount"] == "3000.00"

    sample_expense.refresh_from_db()
    assert sample_expense.recorded_by == owner
    assert sample_expense.amount == 3000


@pytest.mark.django_db
def test_owner_can_partially_update_expense(
    api_client,
    owner,
    sample_expense,
):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse("expense-detail", args=[sample_expense.pk]),
        {
            "description": "Corrected electricity bill",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["description"] == "Corrected electricity bill"
    assert response.data["amount"] == "2500.00"
    assert response.data["payment_reference"] == "QWE123456"

    sample_expense.refresh_from_db()
    assert sample_expense.amount == 2500

# EXPENSE DELETION TESTS

@pytest.mark.django_db
def test_owner_can_delete_expense(
    api_client,
    owner,
    sample_expense,
):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(
        reverse("expense-detail", args=[sample_expense.pk])
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Expense.objects.filter(pk=sample_expense.pk).exists()


# CASHIER CANNOT MODIFY OR DELETE EXPENSES

@pytest.mark.django_db
def test_cashier_cannot_retrieve_expense(
    api_client,
    cashier,
    sample_expense,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("expense-detail", args=[sample_expense.pk])
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_cashier_cannot_update_expense(
    api_client,
    cashier,
    sample_expense,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.patch(
        reverse("expense-detail", args=[sample_expense.pk]),
        {"description": "Unauthorized change"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    sample_expense.refresh_from_db()
    assert sample_expense.description == "Shop electricity bill"


@pytest.mark.django_db
def test_cashier_cannot_delete_expense(
    api_client,
    cashier,
    sample_expense,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.delete(
        reverse("expense-detail", args=[sample_expense.pk])
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Expense.objects.filter(pk=sample_expense.pk).exists()


# EXPENSE VALIDATION TESTS

@pytest.mark.django_db
def test_owner_cannot_create_expense_with_zero_amount(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("expense-list"),
        {
            "description": "Invalid rent expense",
            "category": "RENT",
            "amount": "0.00",
            "payment_method": "CASH",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Expense.objects.count() == 0


@pytest.mark.django_db
def test_owner_cannot_create_mpesa_expense_without_reference(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("expense-list"),
        {
            "description": "Electricity bill",
            "category": "ELECTRICITY",
            "amount": "2500.00",
            "payment_method": "MPESA",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Expense.objects.count() == 0


@pytest.mark.django_db
def test_owner_cannot_create_bank_expense_without_reference(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("expense-list"),
        {
            "description": "Supplier transport payment",
            "category": "TRANSPORT",
            "amount": "3000.00",
            "payment_method": "BANK",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Expense.objects.count() == 0


@pytest.mark.django_db
def test_owner_cannot_create_cash_expense_with_reference(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("expense-list"),
        {
            "description": "Shop cleaning",
            "category": "OTHER",
            "amount": "500.00",
            "payment_method": "CASH",
            "payment_reference": "CASH123",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Expense.objects.count() == 0