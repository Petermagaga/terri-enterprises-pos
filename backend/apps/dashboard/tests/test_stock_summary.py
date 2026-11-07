import pytest
from decimal import Decimal

from apps.dashboard.services.stock_summary import get_stock_summary
from apps.inventory.models import InventoryBalance
from apps.products.models import Category, Product, ProductFamily
from apps.products.services.product_creation import create_product


pytestmark = pytest.mark.django_db


@pytest.fixture
def category():
    return Category.objects.create(name="Groceries")


@pytest.fixture
def family():
    return ProductFamily.objects.create(name="Margarine")


def create_test_product(category, family, name, size):
    return create_product(
        name=name,
        product_family=family,
        category=category,
        size_value=size,
        size_unit="G",
        base_unit="tub",
        retail_price=100,
        wholesale_price=90,
    )


def test_stock_summary_counts_products_correctly(category, family):
    # Product with healthy stock.
    healthy = create_test_product(
        category, family, "Margarine 50g", 50
    )
    healthy.reorder_level = 5
    healthy.save()
    InventoryBalance.objects.create(
        product=healthy,
        quantity_on_hand=Decimal("10.000"),
    )

    # Product exactly at reorder level.
    low = create_test_product(
        category, family, "Margarine 100g", 100
    )
    low.reorder_level = 5
    low.save()
    InventoryBalance.objects.create(
        product=low,
        quantity_on_hand=Decimal("5.000"),
    )

    # Product below reorder level but above zero.
    very_low = create_test_product(
        category, family, "Margarine 150g", 150
    )
    very_low.reorder_level = 5
    very_low.save()
    InventoryBalance.objects.create(
        product=very_low,
        quantity_on_hand=Decimal("2.000"),
    )

    # Product with an inventory balance of zero.
    out_of_stock = create_test_product(
        category, family, "Margarine 200g", 200
    )
    InventoryBalance.objects.create(
        product=out_of_stock,
        quantity_on_hand=Decimal("0.000"),
    )

    # Active product without an inventory balance.
    missing_balance = create_test_product(
        category, family, "Margarine 250g", 250
    )

    # Inactive products must not be included.
    inactive = create_test_product(
        category, family, "Margarine 300g", 300
    )
    inactive.is_active = False
    inactive.save()

    summary = get_stock_summary()

    assert summary == {
        "total_products": 5,
        "low_stock_products": 2,
        "out_of_stock_products": 2,
    }