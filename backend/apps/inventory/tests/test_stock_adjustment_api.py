
from datetime import timedelta
from decimal import Decimal

import pytest

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from apps.inventory.models import (
    InventoryBalance,
    ProductPackaging,
    StockBatch,
    StockMovement,
)
from apps.inventory.services.purchase_creation import (
    add_purchase_item,
    create_purchase,
)
from apps.inventory.services.purchase_receiving import receive_purchase
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.suppliers.models import Supplier


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner():
    User = get_user_model()
    return User.objects.create_user(
        username="adjustment_api_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier():
    User = get_user_model()
    return User.objects.create_user(
        username="adjustment_api_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def supplier():
    return Supplier.objects.create(
        name="Adjustment API Distributors",
        phone="0712345678",
    )


@pytest.fixture
def product_and_packaging():
    category = Category.objects.create(name="Adjustment API Groceries")
    family = ProductFamily.objects.create(
        name="Adjustment API Cooking Oil"
    )

    product = create_product(
        name="Adjustment API Cooking Oil 1L",
        product_family=family,
        category=category,
        size_value=1000,
        size_unit="ML",
        base_unit="bottle",
        retail_price=250,
        wholesale_price=230,
    )

    packaging = ProductPackaging.objects.create(
        product=product,
        name="Bottle",
        conversion_factor=1,
    )

    return product, packaging


def create_received_batch(
    *,
    supplier,
    owner,
    product,
    packaging,
    quantity,
    unit_cost,
    received_at,
):
    purchase = create_purchase(
        supplier=supplier,
        created_by=owner,
        transport_cost=Decimal("0.00"),
    )

    add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=Decimal(str(quantity)),
        purchase_unit_cost=Decimal(str(unit_cost)),
    )

    batches = receive_purchase(
        purchase=purchase,
        received_at=received_at,
    )

    return batches[0]


def adjustment_url():
    return reverse("inventory-stock-adjustment")


# AUTHENTICATION AND PERMISSION TESTS


def test_unauthenticated_user_cannot_adjust_stock(
    api_client,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    response = api_client.post(
        adjustment_url(),
        {
            "product": product.pk,
            "quantity": "5.000",
            "movement_type": StockMovement.MovementType.ADJUSTMENT_IN,
            "reason": "Physical stock correction",
            "unit_cost": "100.000000",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_cashier_cannot_adjust_stock(
    api_client,
    cashier,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        adjustment_url(),
        {
            "product": product.pk,
            "quantity": "5.000",
            "movement_type": StockMovement.MovementType.ADJUSTMENT_IN,
            "reason": "Physical stock correction",
            "unit_cost": "100.000000",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    assert not StockBatch.objects.filter(product=product).exists()
    assert not StockMovement.objects.filter(product=product).exists()


# STOCK INCREASE TESTS


def test_owner_can_increase_stock(
    api_client,
    owner,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        adjustment_url(),
        {
            "product": product.pk,
            "quantity": "10.000",
            "movement_type": StockMovement.MovementType.ADJUSTMENT_IN,
            "reason": "Physical stock count correction",
            "unit_cost": "120.000000",
            "reference": "COUNT-API-001",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    balance = InventoryBalance.objects.get(product=product)

    assert balance.quantity_on_hand == Decimal("10.000")

    assert response.data["movement_type"] == (
        StockMovement.MovementType.ADJUSTMENT_IN
    )

    assert len(response.data["movements"]) == 1

    movement = response.data["movements"][0]

    assert movement["movement_type"] == (
        StockMovement.MovementType.ADJUSTMENT_IN
    )
    assert movement["quantity"] == "10.000"
    assert movement["unit_cost"] == "120.000000"
    assert movement["reference"] == "COUNT-API-001"
    assert movement["created_by_username"] == owner.username


# STOCK REDUCTION AND FIFO TESTS


def test_owner_can_reduce_stock_using_fifo(
    api_client,
    owner,
    supplier,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=10,
        unit_cost=100,
        received_at=timezone.now() - timedelta(days=2),
    )

    create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=10,
        unit_cost=150,
        received_at=timezone.now() - timedelta(days=1),
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        adjustment_url(),
        {
            "product": product.pk,
            "quantity": "12.000",
            "movement_type": StockMovement.MovementType.ADJUSTMENT_OUT,
            "reason": "Physical stock count correction",
            "reference": "COUNT-API-002",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    balance = InventoryBalance.objects.get(product=product)

    assert balance.quantity_on_hand == Decimal("8.000")

    movements = response.data["movements"]

    assert len(movements) == 2
    assert movements[0]["quantity"] == "10.000"
    assert movements[0]["unit_cost"] == "100.000000"
    assert movements[1]["quantity"] == "2.000"
    assert movements[1]["unit_cost"] == "150.000000"


def test_owner_can_write_off_damaged_stock(
    api_client,
    owner,
    supplier,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    batch = create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=10,
        unit_cost=100,
        received_at=timezone.now(),
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        adjustment_url(),
        {
            "product": product.pk,
            "quantity": "3.000",
            "movement_type": StockMovement.MovementType.DAMAGE,
            "reason": "Three bottles were damaged",
            "reference": "DAMAGE-API-001",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    batch.refresh_from_db()

    balance = InventoryBalance.objects.get(product=product)

    assert batch.remaining_quantity == Decimal("7.000")
    assert balance.quantity_on_hand == Decimal("7.000")

    movement = response.data["movements"][0]

    assert movement["movement_type"] == StockMovement.MovementType.DAMAGE
    assert movement["direction"] == StockMovement.Direction.OUT
    assert movement["quantity"] == "3.000"
    assert movement["reference"] == "DAMAGE-API-001"


# VALIDATION AND ROLLBACK TESTS


def test_stock_increase_requires_unit_cost(
    api_client,
    owner,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        adjustment_url(),
        {
            "product": product.pk,
            "quantity": "5.000",
            "movement_type": StockMovement.MovementType.ADJUSTMENT_IN,
            "reason": "Opening stock correction",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "unit_cost" in response.data

    assert not StockBatch.objects.filter(product=product).exists()


def test_adjustment_requires_a_reason(
    api_client,
    owner,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        adjustment_url(),
        {
            "product": product.pk,
            "quantity": "5.000",
            "movement_type": StockMovement.MovementType.ADJUSTMENT_IN,
            "reason": "   ",
            "unit_cost": "100.000000",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "reason" in response.data

    assert not StockBatch.objects.filter(product=product).exists()


def test_owner_cannot_reduce_more_stock_than_available(
    api_client,
    owner,
    supplier,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    batch = create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=5,
        unit_cost=100,
        received_at=timezone.now(),
    )

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        adjustment_url(),
        {
            "product": product.pk,
            "quantity": "8.000",
            "movement_type": StockMovement.MovementType.ADJUSTMENT_OUT,
            "reason": "Physical stock count correction",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    batch.refresh_from_db()

    balance = InventoryBalance.objects.get(product=product)

    assert batch.remaining_quantity == Decimal("5.000")
    assert balance.quantity_on_hand == Decimal("5.000")

    assert not StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.ADJUSTMENT_OUT,
    ).exists()
