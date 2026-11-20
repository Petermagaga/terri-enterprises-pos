
import pytest

from datetime import date
from unittest.mock import patch

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
    response = api_client.get(reverse("dashboard-owner"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_cashier_cannot_access_owner_dashboard(
    api_client,
    cashier,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(reverse("dashboard-owner"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch(
    "apps.dashboard.api.views.owner_dashboard.get_owner_dashboard_summary"
)
def test_owner_can_access_owner_dashboard_with_default_weekly_period(
    mock_get_summary,
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)
    mock_get_summary.return_value = {
        "date": date(2026, 11, 19),
        "date_range": {
            "start_date": date(2026, 11, 16),
            "end_date": date(2026, 11, 19),
        },
        "financial_summary": {},
        "payment_summary": {},
        "sales_summary": {},
        "sales_trend": [],
        "stock_summary": {},
        "inventory_valuation": {},
        "top_products": [],
        "category_performance": [],
    }

    response = api_client.get(reverse("dashboard-owner"))

    assert response.status_code == status.HTTP_200_OK

    mock_get_summary.assert_called_once_with(
        period="this_week",
        start_date=None,
        end_date=None,
    )

    assert "date" in response.data
    assert "date_range" in response.data
    assert "financial_summary" in response.data
    assert "payment_summary" in response.data
    assert "sales_summary" in response.data
    assert "sales_trend" in response.data
    assert "stock_summary" in response.data
    assert "inventory_valuation" in response.data
    assert "top_products" in response.data

@patch(
    "apps.dashboard.api.views.owner_dashboard.get_owner_dashboard_summary"
)
def test_owner_can_select_monthly_period(
    mock_get_summary,
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)
    mock_get_summary.return_value = {
        "date": date(2026, 11, 19),
        "date_range": {
            "start_date": date(2026, 11, 1),
            "end_date": date(2026, 11, 19),
        },
        "financial_summary": {},
        "payment_summary": {},
        "sales_summary": {},
        "sales_trend": [],
        "stock_summary": {},
        "inventory_valuation": {},
        "top_products": [],
        "category_performance": [],
    }

    response = api_client.get(
        reverse("dashboard-owner"),
        {"period": "this_month"},
    )

    assert response.status_code == status.HTTP_200_OK

    mock_get_summary.assert_called_once_with(
        period="this_month",
        start_date=None,
        end_date=None,
    )


@patch(
    "apps.dashboard.api.views.owner_dashboard.get_owner_dashboard_summary"
)
def test_owner_can_select_custom_date_range(
    mock_get_summary,
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)
    mock_get_summary.return_value = {
        "date": date(2026, 11, 6),
        "date_range": {
            "start_date": date(2026, 11, 1),
            "end_date": date(2026, 11, 6),
        },
        "financial_summary": {},
        "payment_summary": {},
        "sales_summary": {},
        "sales_trend": [],
        "stock_summary": {},
        "inventory_valuation": {},
        "top_products": [],
        "category_performance": [],
    }

    response = api_client.get(
        reverse("dashboard-owner"),
        {
            "period": "custom",
            "start_date": "2026-11-01",
            "end_date": "2026-11-06",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    mock_get_summary.assert_called_once_with(
        period="custom",
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 6),
    )


def test_custom_period_requires_both_dates(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("dashboard-owner"),
        {
            "period": "custom",
            "start_date": "2026-11-01",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_custom_period_rejects_start_date_after_end_date(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("dashboard-owner"),
        {
            "period": "custom",
            "start_date": "2026-11-06",
            "end_date": "2026-11-01",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_dashboard_rejects_unsupported_period(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("dashboard-owner"),
        {"period": "last_decade"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
