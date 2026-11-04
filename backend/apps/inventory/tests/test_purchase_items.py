from decimal import Decimal

import pytest

from django.core.exceptions import ValidationError

from apps.inventory.models import (
    ProductPackaging,
    Purchase,
    PurchaseItem,
)
from apps.inventory.services.purchase_creation import (
    add_purchase_item,
    create_purchase,
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
        username="inventory_owner",
        password="test-password",
    )


@pytest.fixture
def supplier():
    return Supplier.objects.create(
        name="ABC Distributors",
        phone="0712345678",
    )


@pytest.fixture
def product():
    category = Category.objects.create(name="Groceries")
    family = ProductFamily.objects.create(name="Cooking Oil")

    return create_product(
        name="Cooking Oil 1L",
        product_family=family,
        category=category,
        size_value=1000,
        size_unit="ML",
        base_unit="bottle",
        retail_price=250,
        wholesale_price=230,
    )


@pytest.fixture
def packaging(product):
    return ProductPackaging.objects.create(
        product=product,
        name="Carton",
        conversion_factor=12,
        purchase_enabled=True,
        sales_enabled=True,
    )


@pytest.fixture
def purchase(supplier, owner):
    return create_purchase(
        supplier=supplier,
        created_by=owner,
        supplier_reference="INV-001",
    )


def test_purchase_item_is_created_successfully(
    purchase, product, packaging
):
    item = add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=2,
        purchase_unit_cost=Decimal("2400.00"),
    )

    assert item.pk is not None
    assert item.purchase == purchase
    assert item.product == product
    assert item.packaging == packaging


def test_purchase_item_calculates_base_quantity(
    purchase, product, packaging
):
    item = add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=2,
        purchase_unit_cost=Decimal("2400.00"),
    )

    assert item.base_quantity == Decimal("24")


def test_purchase_item_preserves_packaging_snapshots(
    purchase, product, packaging
):
    item = add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=2,
        purchase_unit_cost=Decimal("2400.00"),
    )

    assert item.packaging_name_snapshot == "Carton"
    assert item.conversion_factor_snapshot == 12


def test_purchase_item_rejects_packaging_from_another_product(
    purchase, product
):
    category = Category.objects.create(name="Beverages")
    family = ProductFamily.objects.create(name="Juice")

    another_product = create_product(
        name="Orange Juice 500ml",
        product_family=family,
        category=category,
        size_value=500,
        size_unit="ML",
        base_unit="bottle",
        retail_price=100,
        wholesale_price=90,
    )

    another_packaging = ProductPackaging.objects.create(
        product=another_product,
        name="Carton",
        conversion_factor=24,
    )

    with pytest.raises(ValidationError):
        add_purchase_item(
            purchase=purchase,
            product=product,
            packaging=another_packaging,
            package_quantity=1,
            purchase_unit_cost=Decimal("1000.00"),
        )

    assert PurchaseItem.objects.count() == 0


def test_purchase_item_rejects_inactive_packaging(
    purchase, product
):
    inactive_packaging = ProductPackaging.objects.create(
        product=product,
        name="Old Carton",
        conversion_factor=12,
        is_active=False,
    )

    with pytest.raises(ValidationError):
        add_purchase_item(
            purchase=purchase,
            product=product,
            packaging=inactive_packaging,
            package_quantity=1,
            purchase_unit_cost=Decimal("1000.00"),
        )

    assert PurchaseItem.objects.count() == 0


def test_purchase_item_rejects_inactive_product(
    purchase, packaging, product
):
    product.is_active = False
    product.save()

    with pytest.raises(ValidationError):
        add_purchase_item(
            purchase=purchase,
            product=product,
            packaging=packaging,
            package_quantity=1,
            purchase_unit_cost=Decimal("1000.00"),
        )

    assert PurchaseItem.objects.count() == 0


def test_purchase_item_cannot_be_added_to_received_purchase(
    purchase, product, packaging
):
    purchase.status = Purchase.Status.RECEIVED
    purchase.save()

    with pytest.raises(ValidationError):
        add_purchase_item(
            purchase=purchase,
            product=product,
            packaging=packaging,
            package_quantity=1,
            purchase_unit_cost=Decimal("1000.00"),
        )

    assert PurchaseItem.objects.count() == 0