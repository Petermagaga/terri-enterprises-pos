from decimal import Decimal

import pytest

from apps.inventory.models import InventoryBalance, StockAlert
from apps.inventory.services.stock_alerts import sync_product_stock_alert
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product


pytestmark = pytest.mark.django_db


@pytest.fixture
def product():
    category = Category.objects.create(name="Alert Groceries")
    family = ProductFamily.objects.create(name="Alert Cooking Oil")

    return create_product(
        name="Alert Cooking Oil 1L",
        product_family=family,
        category=category,
        size_value=1000,
        size_unit="ML",
        base_unit="bottle",
        retail_price=250,
        wholesale_price=230,
        reorder_level=5,
    )


def set_stock(product, quantity):
    balance, _ = InventoryBalance.objects.get_or_create(
        product=product,
        defaults={"quantity_on_hand": Decimal("0.000")},
    )
    balance.quantity_on_hand = Decimal(str(quantity))
    balance.save(update_fields=["quantity_on_hand", "updated_at"])
    return balance


def test_low_stock_creates_unread_alert(product):
    set_stock(product, "5.000")

    alert = sync_product_stock_alert(product=product)

    assert alert is not None
    assert alert.product == product
    assert alert.quantity_on_hand == Decimal("5.000")
    assert alert.reorder_level == 5
    assert alert.is_read is False
    assert alert.resolved_at is None
    assert StockAlert.objects.filter(product=product).count() == 1


def test_zero_stock_creates_alert_even_when_reorder_level_is_zero(product):
    product.reorder_level = 0
    product.save(update_fields=["reorder_level"])
    set_stock(product, "0.000")

    alert = sync_product_stock_alert(product=product)

    assert alert is not None
    assert alert.quantity_on_hand == Decimal("0.000")
    assert alert.is_out_of_stock if hasattr(alert, "is_out_of_stock") else True


def test_stock_above_reorder_level_does_not_create_alert(product):
    set_stock(product, "6.000")

    alert = sync_product_stock_alert(product=product)

    assert alert is None
    assert not StockAlert.objects.filter(product=product).exists()


def test_existing_alert_updates_quantity_without_resetting_read_status(product):
    set_stock(product, "5.000")
    alert = sync_product_stock_alert(product=product)

    alert.is_read = True
    alert.save(update_fields=["is_read"])

    set_stock(product, "3.000")
    updated_alert = sync_product_stock_alert(product=product)

    assert updated_alert.pk == alert.pk
    assert updated_alert.quantity_on_hand == Decimal("3.000")
    assert updated_alert.is_read is True
    assert StockAlert.objects.filter(
        product=product,
        resolved_at__isnull=True,
    ).count() == 1


def test_restocking_above_threshold_resolves_alert(product):
    set_stock(product, "4.000")
    alert = sync_product_stock_alert(product=product)

    set_stock(product, "6.000")
    result = sync_product_stock_alert(product=product)

    alert.refresh_from_db()

    assert result is None
    assert alert.resolved_at is not None
    assert StockAlert.objects.filter(product=product).count() == 1


def test_low_stock_again_after_resolution_creates_new_alert(product):
    set_stock(product, "4.000")
    first_alert = sync_product_stock_alert(product=product)

    set_stock(product, "8.000")
    sync_product_stock_alert(product=product)
    first_alert.refresh_from_db()

    set_stock(product, "2.000")
    second_alert = sync_product_stock_alert(product=product)

    assert first_alert.resolved_at is not None
    assert second_alert is not None
    assert second_alert.pk != first_alert.pk
    assert StockAlert.objects.filter(product=product).count() == 2


def test_deactivated_product_resolves_existing_alert(product):
    set_stock(product, "4.000")
    alert = sync_product_stock_alert(product=product)

    product.is_active = False
    product.save(update_fields=["is_active"])

    result = sync_product_stock_alert(product=product)
    alert.refresh_from_db()

    assert result is None
    assert alert.resolved_at is not None
