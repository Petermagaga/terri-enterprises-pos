from decimal import Decimal

import pytest

from django.core.exceptions import ValidationError

from apps.inventory.models import ProductPackaging, Purchase, PurchaseItem
from apps.inventory.services.purchase_creation import (
    add_purchase_item,
    create_purchase,
)
from apps.inventory.services.transport_allocation import (
    allocate_transport_cost,
)
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.suppliers.models import Supplier
from django.contrib.auth import get_user_model


pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    User = get_user_model()
    return User.objects.create_user(
        username="transport_owner",
        password="test-password",
    )


@pytest.fixture
def supplier():
    return Supplier.objects.create(
        name="ABC Distributors",
        phone="0712345678",
    )


@pytest.fixture
def purchase(supplier, owner):
    return create_purchase(
        supplier=supplier,
        created_by=owner,
        transport_cost=Decimal("500.00"),
    )


@pytest.fixture
def products_and_packaging():
    category = Category.objects.create(name="Groceries")
    family = ProductFamily.objects.create(name="Cooking Oil")

    first_product = create_product(
        name="Cooking Oil 1L",
        product_family=family,
        category=category,
        size_value=1000,
        size_unit="ML",
        base_unit="bottle",
        retail_price=250,
        wholesale_price=230,
    )

    second_product = create_product(
        name="Cooking Oil 2L",
        product_family=family,
        category=category,
        size_value=2000,
        size_unit="ML",
        base_unit="bottle",
        retail_price=450,
        wholesale_price=420,
    )

    first_packaging = ProductPackaging.objects.create(
        product=first_product,
        name="Carton",
        conversion_factor=12,
    )

    second_packaging = ProductPackaging.objects.create(
        product=second_product,
        name="Carton",
        conversion_factor=6,
    )

    return (
        first_product,
        second_product,
        first_packaging,
        second_packaging,
    )


def test_transport_cost_is_allocated_proportionally(
    purchase, products_and_packaging
):
    first, second, first_pack, second_pack = products_and_packaging

    first_item = add_purchase_item(
        purchase=purchase,
        product=first,
        packaging=first_pack,
        package_quantity=1,
        purchase_unit_cost=Decimal("2400.00"),
    )

    second_item = add_purchase_item(
        purchase=purchase,
        product=second,
        packaging=second_pack,
        package_quantity=1,
        purchase_unit_cost=Decimal("1600.00"),
    )

    allocate_transport_cost(purchase=purchase)

    first_item.refresh_from_db()
    second_item.refresh_from_db()

    assert first_item.allocated_transport_cost == Decimal("300.00")
    assert second_item.allocated_transport_cost == Decimal("200.00")


def test_transport_allocations_equal_total_transport_cost(
    purchase, products_and_packaging
):
    first, second, first_pack, second_pack = products_and_packaging

    add_purchase_item(
        purchase=purchase,
        product=first,
        packaging=first_pack,
        package_quantity=1,
        purchase_unit_cost=Decimal("100.00"),
    )

    add_purchase_item(
        purchase=purchase,
        product=second,
        packaging=second_pack,
        package_quantity=1,
        purchase_unit_cost=Decimal("200.00"),
    )

    items = allocate_transport_cost(purchase=purchase)

    allocated_total = sum(
        (item.allocated_transport_cost for item in items),
        Decimal("0.00"),
    )

    assert allocated_total == purchase.transport_cost


def test_transport_allocation_handles_rounding_remainders(
    purchase, products_and_packaging
):
    first, second, first_pack, second_pack = products_and_packaging

    purchase.transport_cost = Decimal("0.05")
    purchase.save()

    add_purchase_item(
        purchase=purchase,
        product=first,
        packaging=first_pack,
        package_quantity=1,
        purchase_unit_cost=Decimal("1.00"),
    )

    add_purchase_item(
        purchase=purchase,
        product=second,
        packaging=second_pack,
        package_quantity=1,
        purchase_unit_cost=Decimal("1.00"),
    )

    items = allocate_transport_cost(purchase=purchase)

    allocated_total = sum(
        (item.allocated_transport_cost for item in items),
        Decimal("0.00"),
    )

    assert allocated_total == Decimal("0.05")
    assert all(
        item.allocated_transport_cost >= Decimal("0.00")
        for item in items
    )


def test_transport_allocation_rejects_zero_purchase_value(
    purchase, products_and_packaging
):
    first, _, first_pack, _ = products_and_packaging

    add_purchase_item(
        purchase=purchase,
        product=first,
        packaging=first_pack,
        package_quantity=1,
        purchase_unit_cost=Decimal("0.00"),
    )

    with pytest.raises(ValidationError):
        allocate_transport_cost(purchase=purchase)


def test_transport_allocation_rejects_purchase_without_items(purchase):
    with pytest.raises(ValidationError):
        allocate_transport_cost(purchase=purchase)


def test_transport_allocation_rejects_received_purchase(
    purchase, products_and_packaging
):
    first, _, first_pack, _ = products_and_packaging

    add_purchase_item(
        purchase=purchase,
        product=first,
        packaging=first_pack,
        package_quantity=1,
        purchase_unit_cost=Decimal("100.00"),
    )

    purchase.status = Purchase.Status.RECEIVED
    purchase.save()

    with pytest.raises(ValidationError):
        allocate_transport_cost(purchase=purchase)


def test_zero_transport_cost_resets_existing_allocations(
    purchase, products_and_packaging
):
    first, _, first_pack, _ = products_and_packaging

    item = add_purchase_item(
        purchase=purchase,
        product=first,
        packaging=first_pack,
        package_quantity=1,
        purchase_unit_cost=Decimal("100.00"),
    )

    item.allocated_transport_cost = Decimal("50.00")
    item.save()

    purchase.transport_cost = Decimal("0.00")
    purchase.save()

    allocate_transport_cost(purchase=purchase)

    item.refresh_from_db()

    assert item.allocated_transport_cost == Decimal("0.00")