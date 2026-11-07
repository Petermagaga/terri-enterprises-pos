
import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from datetime import date


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner():
    return User.objects.create_user(
        username="reporting_api_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="reporting_api_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


REPORT_ENDPOINTS = [
    "report-profit-loss",
    "report-product-profitability",
    "report-payment-summary",
    "report-sales-summary",
]


@pytest.mark.parametrize("endpoint", REPORT_ENDPOINTS)
def test_unauthenticated_user_cannot_access_reports(
    api_client,
    endpoint,
):
    response = api_client.get(reverse(endpoint))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("endpoint", REPORT_ENDPOINTS)
def test_cashier_cannot_access_reports(
    api_client,
    cashier,
    endpoint,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(reverse(endpoint))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize("endpoint", REPORT_ENDPOINTS)
def test_owner_can_access_reports(
    api_client,
    owner,
    endpoint,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(reverse(endpoint))

    assert response.status_code == status.HTTP_200_OK
    assert "date_range" in response.data
    assert "data" in response.data
    payload = response.json()

    assert "date_range" in payload
    assert "data" in payload

def test_owner_can_request_custom_date_range(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("report-profit-loss"),
        {
            "preset": "custom",
            "start_date": "2026-11-01",
            "end_date": "2026-11-06",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["date_range"]["start_date"] == date(2026, 11, 1)
    assert response.data["date_range"]["end_date"] == date(2026, 11, 6)

def test_custom_date_range_requires_both_dates(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("report-profit-loss"),
        {
            "preset": "custom",
            "start_date": "2026-11-01",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_custom_date_range_rejects_start_date_after_end_date(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("report-profit-loss"),
        {
            "preset": "custom",
            "start_date": "2026-11-06",
            "end_date": "2026-11-01",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_sales_summary_accepts_grouping_parameter(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("report-sales-summary"),
        {
            "preset": "this_month",
            "group_by": "monthly",
        },
    )

    assert response.status_code == status.HTTP_200_OK


def test_sales_summary_rejects_unsupported_grouping(
    api_client,
    owner,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("report-sales-summary"),
        {
            "preset": "today",
            "group_by": "hourly",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
