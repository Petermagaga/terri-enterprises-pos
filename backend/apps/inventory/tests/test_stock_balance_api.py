import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.inventory.models import InventoryBalance
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        username="stock_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="stock_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def product(db):
    family = ProductFamily.objects.create(name="Stock Test Water")
    category = Category.objects.create(name="Stock Test Drinks")

    return create_product(
        name="Stock Test Water 500ml",
        product_family=family,
        category=category,
        size_value="500",
        size_unit="ML",
        base_unit="bottle",
        retail_price="50.00",
        wholesale_price="45.00",
        reorder_level=10,
    )


@pytest.fixture
def inventory_balance(product):
    return InventoryBalance.objects.create(
        product=product,
        quantity_on_hand="8.000",
    )


# AUTHENTICATION TESTS

@pytest.mark.django_db
def test_unauthenticated_user_cannot_view_stock_balances(
    api_client,
    inventory_balance,
):
    response = api_client.get(
        reverse("inventory-stock-balance-list")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# OWNER ACCESS TESTS

@pytest.mark.django_db
def test_owner_can_view_stock_balances(
    api_client,
    owner,
    inventory_balance,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("inventory-stock-balance-list")
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    stock = response.data["results"][0]

    assert stock["product_name"] == "Stock Test Water 500ml"
    assert stock["base_unit"] == "bottle"
    assert stock["quantity_on_hand"] == "8.000"
    assert stock["reorder_level"] == 10
    assert stock["is_low_stock"] is True


@pytest.mark.django_db
def test_owner_can_retrieve_stock_balance(
    api_client,
    owner,
    inventory_balance,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse(
            "inventory-stock-balance-detail",
            args=[inventory_balance.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["quantity_on_hand"] == "8.000"


# CASHIER ACCESS TESTS

@pytest.mark.django_db
def test_cashier_can_view_stock_balances(
    api_client,
    cashier,
    inventory_balance,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("inventory-stock-balance-list")
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1


# LOW STOCK CALCULATION TESTS

@pytest.mark.django_db
def test_stock_above_reorder_level_is_not_low_stock(
    api_client,
    owner,
    inventory_balance,
):
    inventory_balance.quantity_on_hand = "15.000"
    inventory_balance.save()

    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse(
            "inventory-stock-balance-detail",
            args=[inventory_balance.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["is_low_stock"] is False


# DATA PROTECTION TESTS

@pytest.mark.django_db
def test_stock_balance_cannot_be_modified_through_api(
    api_client,
    owner,
    inventory_balance,
):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse(
            "inventory-stock-balance-detail",
            args=[inventory_balance.pk],
        ),
        {"quantity_on_hand": "100.000"},
        format="json",
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    inventory_balance.refresh_from_db()
    assert inventory_balance.quantity_on_hand == Decimal("8.000")