import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner():
    return User.objects.create_user(
        username="dashboard_api_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="dashboard_api_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


def test_unauthenticated_user_cannot_access_owner_dashboard(
    api_client,
):
    response = api_client.get(
        reverse("dashboard-owner")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_cashier_cannot_access_owner_dashboard(
    api_client,
    cashier,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("dashboard-owner")
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_owner_can_access_owner_dashboard(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("dashboard-owner")
    )

    assert response.status_code == status.HTTP_200_OK

    assert "date" in response.data
    assert "financial_summary" in response.data
    assert "payment_summary" in response.data
    assert "sales_summary" in response.data
    assert "stock_summary" in response.data
    assert "top_products" in response.data