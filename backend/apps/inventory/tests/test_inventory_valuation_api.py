from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.inventory.models import StockBatch
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner():
    return User.objects.create_user(
        username="valuation_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="valuation_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def product():
    family = ProductFamily.objects.create(name="Valuation API Family")
    category = Category.objects.create(name="Valuation API Category")

    return create_product(
        name="Valuation API Water",
        product_family=family,
        category=category,
        size_value="500",
        size_unit="ML",
        base_unit="bottle",
        retail_price="100.00",
        wholesale_price="90.00",
        reorder_level=5,
    )


@pytest.fixture
def stock_batch(product):
    from django.utils import timezone

    return StockBatch.objects.create(
        product=product,
        received_quantity=Decimal("10.000"),
        remaining_quantity=Decimal("6.000"),
        landed_unit_cost=Decimal("205.000000"),
        received_at=timezone.now(),
    )

def test_unauthenticated_user_cannot_view_inventory_valuation(
    api_client,
    stock_batch,
):
    response = api_client.get(
        reverse("inventory-valuation")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_cashier_cannot_view_inventory_valuation(
    api_client,
    cashier,
    stock_batch,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("inventory-valuation")
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_owner_can_view_inventory_valuation(
    api_client,
    owner,
    product,
    stock_batch,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("inventory-valuation")
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_inventory_value"] == "1230.00"
    assert response.data["products_with_stock"] == 1
    assert len(response.data["products"]) == 1

    item = response.data["products"][0]

    assert item["product_id"] == product.pk
    assert item["product_name"] == product.name
    assert item["product_sku"] == product.sku
    assert item["base_unit"] == "bottle"
    assert item["quantity_on_hand"] == "6.000"
    assert item["unit_cost"] == "205.000000"
    assert item["stock_value"] == "1230.00"
