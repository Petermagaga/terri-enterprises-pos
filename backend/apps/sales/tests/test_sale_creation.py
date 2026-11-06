
import pytest

from decimal import Decimal
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.inventory.models import ProductPackaging
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.sales.models import Sale
from apps.sales.services.sale_creation import create_sale, add_sale_item


pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    return User.objects.create_superuser(
        username="owner_test",
        email="owner@test.com",
        password="TestPassword123!",
    )


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="cashier_test",
        email="cashier@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def product():
    category = Category.objects.create(name="Groceries")
    family = ProductFamily.objects.create(name="Margarine")

    return create_product(
        name="Margarine 500g",
        product_family=family,
        category=category,
        size_value=500,
        size_unit="G",
        base_unit="tub",
        retail_price=250,
        wholesale_price=230,
    )


@pytest.fixture
def carton(product):
    return ProductPackaging.objects.create(
        product=product,
        name="Carton",
        conversion_factor=12,
        purchase_enabled=True,
        sales_enabled=True,
    )


def test_owner_can_create_draft_sale(owner):
    sale = create_sale(processed_by=owner)

    assert sale.status == Sale.Status.DRAFT
    assert sale.processed_by == owner
    assert sale.total_amount == Decimal("0.00")


def test_cashier_can_create_draft_sale(cashier):
    sale = create_sale(processed_by=cashier)

    assert sale.status == Sale.Status.DRAFT
    assert sale.processed_by == cashier


def test_create_sale_rejects_inactive_user(cashier):
    cashier.is_active = False
    cashier.save()

    with pytest.raises(ValidationError):
        create_sale(processed_by=cashier)


def test_create_sale_rejects_invalid_user():
    with pytest.raises(ValidationError):
        create_sale(processed_by="cashier")


def test_add_retail_sale_item(product, cashier):
    sale = create_sale(processed_by=cashier)

    item = add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=2,
    )

    sale.refresh_from_db()

    assert item.total_amount == Decimal("500.00")
    assert item.selling_price_per_package == Decimal("250.00")
    assert item.quantity == 2
    assert item.conversion_factor_snapshot == 1
    assert item.packaging_name_snapshot == "tub"
    assert sale.total_amount == Decimal("500.00")


def test_add_wholesale_carton_sale_item(product, carton, cashier):
    sale = create_sale(processed_by=cashier)

    item = add_sale_item(
        sale=sale,
        product=product,
        pricing_type="WHOLESALE",
        quantity=2,
        packaging=carton,
    )

    sale.refresh_from_db()

    assert item.selling_price_per_package == Decimal("2760.00")
    assert item.total_amount == Decimal("5520.00")
    assert item.base_quantity == 24
    assert item.packaging_name_snapshot == "Carton"
    assert item.conversion_factor_snapshot == 12
    assert sale.total_amount == Decimal("5520.00")


def test_sale_total_accumulates_multiple_items(product, carton, cashier):
    sale = create_sale(processed_by=cashier)

    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=2,
    )

    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="WHOLESALE",
        quantity=1,
        packaging=carton,
    )

    sale.refresh_from_db()

    assert sale.items.count() == 2
    assert sale.total_amount == Decimal("3260.00")


def test_sale_item_preserves_product_snapshots(product, cashier):
    sale = create_sale(processed_by=cashier)

    item = add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=1,
    )

    assert item.product_name_snapshot == "Margarine 500g"
    assert item.product_sku_snapshot == product.sku
    assert item.base_unit_snapshot == "tub"


def test_add_sale_item_rejects_completed_sale(product, cashier):
    sale = create_sale(processed_by=cashier)
    sale.status = Sale.Status.COMPLETED
    sale.save()

    with pytest.raises(ValidationError):
        add_sale_item(
            sale=sale,
            product=product,
            pricing_type="RETAIL",
            quantity=1,
        )


def test_add_sale_item_rejects_inactive_product(product, cashier):
    sale = create_sale(processed_by=cashier)

    product.is_active = False
    product.save()

    with pytest.raises(ValidationError):
        add_sale_item(
            sale=sale,
            product=product,
            pricing_type="RETAIL",
            quantity=1,
        )


def test_add_sale_item_rejects_packaging_from_another_product(
    product,
    cashier,
):
    sale = create_sale(processed_by=cashier)

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

    wrong_packaging = ProductPackaging.objects.create(
        product=another_product,
        name="Carton",
        conversion_factor=24,
        sales_enabled=True,
    )

    with pytest.raises(ValidationError):
        add_sale_item(
            sale=sale,
            product=product,
            pricing_type="RETAIL",
            quantity=1,
            packaging=wrong_packaging,
        )


def test_adding_sale_item_does_not_deduct_stock(product, cashier):
    sale = create_sale(processed_by=cashier)

    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=2,
    )

    # Stock is deducted only when the sale is completed.
    from apps.inventory.models import InventoryBalance

    assert not InventoryBalance.objects.filter(product=product).exists()

def test_add_sale_item_rejects_invalid_pricing_type(product, cashier):
    sale = create_sale(processed_by=cashier)

    with pytest.raises(ValidationError):
        add_sale_item(
            sale=sale,
            product=product,
            pricing_type="INVALID",
            quantity=1,
        )

    sale.refresh_from_db()

    assert sale.total_amount == Decimal("0.00")
    assert sale.items.count() == 0