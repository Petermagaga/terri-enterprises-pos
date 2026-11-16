from decimal import Decimal

import pytest
from django.utils import timezone

from apps.inventory.models import StockBatch
from apps.inventory.services.inventory_valuation import (
    get_inventory_valuation,
)
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product


pytestmark = pytest.mark.django_db


def make_product(name):
    family = ProductFamily.objects.create(name=f"{name} Family")
    category = Category.objects.create(name=f"{name} Category")

    return create_product(
        name=name,
        product_family=family,
        category=category,
        size_value="500",
        size_unit="ML",
        base_unit="bottle",
        retail_price="100.00",
        wholesale_price="90.00",
        reorder_level=5,
    )


def make_batch(product, received, remaining, unit_cost):
    return StockBatch.objects.create(
        product=product,
        received_quantity=Decimal(received),
        remaining_quantity=Decimal(remaining),
        landed_unit_cost=Decimal(unit_cost),
        received_at=timezone.now(),
    )


def test_valuation_uses_remaining_batch_quantities_and_landed_costs():
    product = make_product("Valuation Water")

    # Two remaining batches with different landed unit costs.
    make_batch(product, "2.000", "2.000", "205.000000")
    make_batch(product, "3.000", "3.000", "210.000000")

    # Fully consumed stock must not contribute to valuation.
    make_batch(product, "5.000", "0.000", "999.000000")

    result = get_inventory_valuation()

    assert result["total_inventory_value"] == Decimal("1040.00")
    assert result["products_with_stock"] == 1

    item = result["products"][0]

    assert item["product_id"] == product.pk
    assert item["product_name"] == product.name
    assert item["product_sku"] == product.sku
    assert item["base_unit"] == "bottle"
    assert item["quantity_on_hand"] == Decimal("5.000")
    assert item["unit_cost"] == Decimal("208.000000")
    assert item["stock_value"] == Decimal("1040.00")


def test_valuation_includes_stock_for_inactive_products():
    product = make_product("Inactive Valuation Water")
    product.is_active = False
    product.save(update_fields=["is_active"])

    make_batch(product, "4.000", "4.000", "50.000000")

    result = get_inventory_valuation()

    assert result["total_inventory_value"] == Decimal("200.00")
    assert result["products_with_stock"] == 1
    assert result["products"][0]["is_active"] is False


def test_valuation_returns_zero_when_no_stock_batches_exist():
    result = get_inventory_valuation()

    assert result == {
        "total_inventory_value": Decimal("0.00"),
        "products_with_stock": 0,
        "products": [],
    }
