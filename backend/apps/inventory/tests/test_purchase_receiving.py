
from decimal import Decimal

import pytest

from django.core.exceptions import ValidationError

from apps.inventory.models import (
    ProductPackaging,
    Purchase,
    PurchaseItem,
    StockBatch,
)
from apps.inventory.services.purchase_creation import (
    add_purchase_item,
    create_purchase,
)
from apps.inventory.services.purchase_receiving import receive_purchase
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.suppliers.models import Supplier
from django.contrib.auth import get_user_model


pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    User = get_user_model()
    return User.objects.create_user(
        username="receiving_owner",
        password="test-password",
    )


@pytest.fixture
def supplier():
    return Supplier.objects.create(
        name="Receiving Distributors",
        phone="0712345678",
    )


@pytest.fixture
def product_and_packaging():
    category = Category.objects.create(name="Receiving Groceries")
    family = ProductFamily.objects.create(name="Receiving Oil")

    product = create_product(
        name="Cooking Oil 1L",
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
        name="Carton",
        conversion_factor=12,
    )

    return product, packaging


@pytest.fixture
def purchase(supplier, owner):
    return create_purchase(
        supplier=supplier,
        created_by=owner,
        transport_cost=Decimal("120.00"),
    )


def test_receiving_purchase_creates_stock_batch(
    purchase, product_and_packaging
):
    product, packaging = product_and_packaging

    item = add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=2,
        purchase_unit_cost=Decimal("2400.00"),
    )

    batches = receive_purchase(purchase=purchase)

    assert len(batches) == 1

    batch = batches[0]

    assert batch.product == product
    assert batch.purchase_item == item
    assert batch.received_quantity == Decimal("24.000")
    assert batch.remaining_quantity == Decimal("24.000")


def test_receiving_calculates_landed_unit_cost(
    purchase, product_and_packaging
):
    product, packaging = product_and_packaging

    item = add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=2,
        purchase_unit_cost=Decimal("2400.00"),
    )

    batches = receive_purchase(purchase=purchase)

    batch = batches[0]

    # Purchase subtotal: 2 x 2,400 = 4,800.
    # Transport cost: 120.
    # Landed total: 4,920.
    # Base quantity: 24 bottles.
    assert batch.landed_unit_cost == Decimal("205.000000")


def test_receiving_marks_purchase_as_received(
    purchase, product_and_packaging
):
    product, packaging = product_and_packaging

    add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=1,
        purchase_unit_cost=Decimal("2400.00"),
    )

    receive_purchase(purchase=purchase)

    purchase.refresh_from_db()

    assert purchase.status == Purchase.Status.RECEIVED
    assert purchase.received_at is not None


def test_receiving_purchase_without_items_is_rejected(purchase):
    with pytest.raises(ValidationError):
        receive_purchase(purchase=purchase)

    purchase.refresh_from_db()

    assert purchase.status == Purchase.Status.DRAFT
    assert StockBatch.objects.count() == 0


def test_received_purchase_cannot_be_received_twice(
    purchase, product_and_packaging
):
    product, packaging = product_and_packaging

    add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=1,
        purchase_unit_cost=Decimal("2400.00"),
    )

    receive_purchase(purchase=purchase)

    with pytest.raises(ValidationError):
        receive_purchase(purchase=purchase)

    assert StockBatch.objects.count() == 1


def test_receiving_creates_one_batch_per_purchase_item(
    purchase, product_and_packaging
):
    product, packaging = product_and_packaging

    first_item = add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=1,
        purchase_unit_cost=Decimal("2400.00"),
    )

    second_item = add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=2,
        purchase_unit_cost=Decimal("2300.00"),
    )

    batches = receive_purchase(purchase=purchase)

    assert len(batches) == 2
    assert StockBatch.objects.count() == 2
    assert {batch.purchase_item_id for batch in batches} == {
        first_item.pk,
        second_item.pk,
    }


def test_receiving_preserves_zero_transport_cost(
    purchase, product_and_packaging
):
    product, packaging = product_and_packaging

    purchase.transport_cost = Decimal("0.00")
    purchase.save()

    add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=1,
        purchase_unit_cost=Decimal("1200.00"),
    )

    batches = receive_purchase(purchase=purchase)

    assert batches[0].landed_unit_cost == Decimal("100.000000")
