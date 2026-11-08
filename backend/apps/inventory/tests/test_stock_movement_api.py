import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.inventory.models import StockMovement
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        username="movement_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="movement_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def product(db):
    family = ProductFamily.objects.create(
        name="Movement Test Water",
    )
    category = Category.objects.create(
        name="Movement Test Drinks",
    )

    return create_product(
        name="Movement Test Water 500ml",
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
def stock_movement(product, owner):
    return StockMovement.objects.create(
        product=product,
        movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
        direction=StockMovement.Direction.IN,
        quantity="20.000",
        created_by=owner,
        reference="TEST-ADJUSTMENT-001",
        notes="Test stock adjustment",
    )


# AUTHENTICATION TESTS

@pytest.mark.django_db
def test_unauthenticated_user_cannot_view_stock_movements(
    api_client,
    stock_movement,
):
    response = api_client.get(
        reverse("inventory-stock-movement-list")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# OWNER ACCESS TESTS

@pytest.mark.django_db
def test_owner_can_view_stock_movements(
    api_client,
    owner,
    stock_movement,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("inventory-stock-movement-list")
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    movement = response.data['results'][0]

    assert movement["product_name"] == "Movement Test Water 500ml"
    assert movement["product_sku"] == stock_movement.product.sku
    assert movement["movement_type"] == "ADJUSTMENT_IN"
    assert movement["direction"] == "IN"
    assert movement["quantity"] == "20.000"
    assert movement["reference"] == "TEST-ADJUSTMENT-001"
    assert movement["created_by_username"] == owner.username


@pytest.mark.django_db
def test_owner_can_retrieve_stock_movement(
    api_client,
    owner,
    stock_movement,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse(
            "inventory-stock-movement-detail",
            args=[stock_movement.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["quantity"] == "20.000"
    assert response.data["product_name"] == "Movement Test Water 500ml"


# CASHIER ACCESS TESTS

@pytest.mark.django_db
def test_cashier_can_view_stock_movements(
    api_client,
    cashier,
    stock_movement,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("inventory-stock-movement-list")
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1


# DATA PROTECTION TESTS

@pytest.mark.django_db
def test_stock_movements_cannot_be_created_through_api(
    api_client,
    owner,
    product,
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("inventory-stock-movement-list"),
        {
            "product": product.pk,
            "movement_type": "ADJUSTMENT_IN",
            "direction": "IN",
            "quantity": "20.000",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_stock_movements_cannot_be_modified_or_deleted_through_api(
    api_client,
    owner,
    stock_movement,
):
    api_client.force_authenticate(user=owner)

    detail_url = reverse(
        "inventory-stock-movement-detail",
        args=[stock_movement.pk],
    )

    patch_response = api_client.patch(
        detail_url,
        {"notes": "Changed movement"},
        format="json",
    )

    delete_response = api_client.delete(detail_url)

    assert patch_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert delete_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    stock_movement.refresh_from_db()
    assert stock_movement.notes == "Test stock adjustment"