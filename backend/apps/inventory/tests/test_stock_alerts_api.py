from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.inventory.models import InventoryBalance, StockAlert
from apps.inventory.services.stock_alerts import sync_product_stock_alert
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner():
    return User.objects.create_user(
        username="alert_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="alert_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def product():
    category = Category.objects.create(name="Alert API Groceries")
    family = ProductFamily.objects.create(name="Alert API Drinks")

    return create_product(
        name="Alert API Water 500ml",
        product_family=family,
        category=category,
        size_value=500,
        size_unit="ML",
        base_unit="bottle",
        retail_price="50.00",
        wholesale_price="45.00",
        reorder_level=10,
    )


@pytest.fixture
def active_alert(product):
    InventoryBalance.objects.create(
        product=product,
        quantity_on_hand=Decimal("8.000"),
    )
    return sync_product_stock_alert(product=product)


def test_unauthenticated_user_cannot_view_stock_alerts(
    api_client,
    active_alert,
):
    response = api_client.get(
        reverse("inventory-stock-alerts")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_owner_can_view_active_stock_alerts(
    api_client,
    owner,
    active_alert,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("inventory-stock-alerts")
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["unread_count"] == 1
    assert len(response.data["alerts"]) == 1

    alert = response.data["alerts"][0]

    assert alert["product_name"] == "Alert API Water 500ml"
    assert alert["quantity_on_hand"] == "8.000"
    assert alert["reorder_level"] == 10
    assert alert["is_out_of_stock"] is False
    assert alert["is_read"] is False


def test_cashier_can_view_active_stock_alerts(
    api_client,
    cashier,
    active_alert,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("inventory-stock-alerts")
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["unread_count"] == 1
    assert len(response.data["alerts"]) == 1


def test_mark_all_read_does_not_delete_or_resolve_alerts(
    api_client,
    owner,
    active_alert,
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("inventory-stock-alerts-mark-all-read")
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["marked_read"] == 1
    assert response.data["unread_count"] == 0

    active_alert.refresh_from_db()

    assert active_alert.is_read is True
    assert active_alert.resolved_at is None
    assert StockAlert.objects.filter(pk=active_alert.pk).exists()

    list_response = api_client.get(
        reverse("inventory-stock-alerts")
    )

    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data["alerts"]) == 1
    assert list_response.data["unread_count"] == 0


def test_mark_all_read_is_available_to_cashier(
    api_client,
    cashier,
    active_alert,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("inventory-stock-alerts-mark-all-read")
    )

    assert response.status_code == status.HTTP_200_OK

    active_alert.refresh_from_db()
    assert active_alert.is_read is True
    assert active_alert.resolved_at is None


def test_mark_all_read_requires_authentication(
    api_client,
):
    response = api_client.post(
        reverse("inventory-stock-alerts-mark-all-read")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_resolved_alert_is_not_returned(
    api_client,
    owner,
    active_alert,
):
    active_alert.resolved_at = active_alert.created_at
    active_alert.save(update_fields=["resolved_at"])

    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("inventory-stock-alerts")
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["alerts"] == []
    assert response.data["unread_count"] == 0
