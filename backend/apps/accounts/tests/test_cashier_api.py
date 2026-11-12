
import pytest

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.sales.models import Sale


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner():
    return User.objects.create_superuser(
        username="cashier_api_owner",
        email="owner@test.com",
        password="TestPassword123!",
    )


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="existing_cashier",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def owner_client(api_client, owner):
    token = Token.objects.create(user=owner)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


@pytest.fixture
def cashier_client(cashier):
    client = APIClient()
    token = Token.objects.create(user=cashier)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


def test_owner_can_create_cashier(owner_client):
    response = owner_client.post(
        "/api/cashiers/",
        {
            "username": "new_cashier",
            "first_name": "John",
            "last_name": "Kamau",
            "email": "john@test.com",
            "password": "CashierPass123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    cashier = User.objects.get(username="new_cashier")
    assert cashier.role == User.Role.CASHIER
    assert cashier.check_password("CashierPass123!")
    assert not cashier.is_superuser
    assert not cashier.is_staff
    assert "password" not in response.data


def test_owner_can_list_cashiers(owner_client, cashier):
    response = owner_client.get("/api/cashiers/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["username"] == cashier.username


def test_cashier_cannot_manage_cashier_accounts(cashier_client):
    response = cashier_client.get("/api/cashiers/")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_unauthenticated_user_cannot_manage_cashiers(api_client):
    response = api_client.get("/api/cashiers/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_owner_can_update_cashier_details(owner_client, cashier):
    response = owner_client.patch(
        f"/api/cashiers/{cashier.id}/",
        {
            "first_name": "Updated",
            "last_name": "Name",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    cashier.refresh_from_db()
    assert cashier.first_name == "Updated"
    assert cashier.last_name == "Name"
    assert cashier.role == User.Role.CASHIER


def test_owner_cannot_promote_cashier_to_owner(owner_client, cashier):
    response = owner_client.patch(
        f"/api/cashiers/{cashier.id}/",
        {"role": User.Role.OWNER},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    cashier.refresh_from_db()
    assert cashier.role == User.Role.CASHIER


def test_owner_can_deactivate_and_reactivate_cashier(owner_client, cashier):
    Token.objects.create(user=cashier)

    response = owner_client.patch(
        f"/api/cashiers/{cashier.id}/",
        {"is_active": False},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    cashier.refresh_from_db()
    assert cashier.is_active is False
    assert not Token.objects.filter(user=cashier).exists()

    response = owner_client.patch(
        f"/api/cashiers/{cashier.id}/",
        {"is_active": True},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    cashier.refresh_from_db()
    assert cashier.is_active is True


def test_owner_can_reset_cashier_password(owner_client, cashier):
    old_token = Token.objects.create(user=cashier)

    response = owner_client.post(
        f"/api/cashiers/{cashier.id}/reset-password/",
        {"password": "NewPassword123!"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    cashier.refresh_from_db()
    assert cashier.check_password("NewPassword123!")
    assert not Token.objects.filter(key=old_token.key).exists()


def test_owner_can_deactivate_cashier_without_deleting_sales(
    owner_client,
    cashier,
):
    sale = Sale.objects.create(processed_by=cashier)

    response = owner_client.delete(
        f"/api/cashiers/{cashier.id}/",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    cashier.refresh_from_db()
    sale.refresh_from_db()

    assert cashier.is_active is False
    assert sale.processed_by_id == cashier.id


def test_cashier_cannot_reset_another_cashier_password(
    cashier_client,
    cashier,
):
    response = cashier_client.post(
        f"/api/cashiers/{cashier.id}/reset-password/",
        {"password": "NewPassword123!"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
