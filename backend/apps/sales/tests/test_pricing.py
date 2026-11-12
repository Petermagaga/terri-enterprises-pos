import pytest

from django.core.exceptions import ValidationError

from apps.inventory.models import ProductPackaging
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.sales.services.pricing import calculate_sale_item_pricing


pytestmark = pytest.mark.django_db


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


def test_retail_price_for_one_base_unit(product):
    result = calculate_sale_item_pricing(
        product=product,
        pricing_type="RETAIL",
        quantity=1,
    )

    assert result["selling_price_per_package"] == 250
    assert result["total_amount"] == 250
    assert result["base_quantity"] == 1
    assert result["packaging_name_snapshot"] == "tub"


def test_wholesale_price_for_one_base_unit(product):
    result = calculate_sale_item_pricing(
        product=product,
        pricing_type="WHOLESALE",
        quantity=1,
    )

    assert result["selling_price_per_package"] == 230
    assert result["total_amount"] == 230


def test_retail_price_for_one_carton(product, carton):
    result = calculate_sale_item_pricing(
        product=product,
        pricing_type="RETAIL",
        quantity=1,
        packaging=carton,
    )

    assert result["selling_price_per_package"] == 3000
    assert result["total_amount"] == 3000
    assert result["base_quantity"] == 12
    assert result["packaging_name_snapshot"] == "Carton"


def test_wholesale_price_for_one_carton(product, carton):
    result = calculate_sale_item_pricing(
        product=product,
        pricing_type="WHOLESALE",
        quantity=1,
        packaging=carton,
    )

    assert result["selling_price_per_package"] == 2760
    assert result["total_amount"] == 2760


def test_multiple_cartons_calculate_correct_total(product, carton):
    result = calculate_sale_item_pricing(
        product=product,
        pricing_type="WHOLESALE",
        quantity=2,
        packaging=carton,
    )

    assert result["total_amount"] == 5520
    assert result["base_quantity"] == 24


def test_pricing_returns_historical_product_snapshots(product):
    result = calculate_sale_item_pricing(
        product=product,
        pricing_type="RETAIL",
        quantity=1,
    )

    assert result["product_name_snapshot"] == "Margarine 500g"
    assert result["product_sku_snapshot"] == product.sku
    assert result["base_unit_snapshot"] == "tub"
    assert result["conversion_factor_snapshot"] == 1


def test_pricing_rejects_inactive_product(product):
    product.is_active = False

    with pytest.raises(ValidationError):
        calculate_sale_item_pricing(
            product=product,
            pricing_type="RETAIL",
            quantity=1,
        )


@pytest.mark.parametrize("pricing_type", ["INVALID", "", None])
def test_pricing_rejects_invalid_pricing_type(product, pricing_type):
    with pytest.raises(ValidationError):
        calculate_sale_item_pricing(
            product=product,
            pricing_type=pricing_type,
            quantity=1,
        )


@pytest.mark.parametrize("quantity", [0, -1, 1.5, "2", True, None])
def test_pricing_rejects_invalid_quantity(product, quantity):
    with pytest.raises(ValidationError):
        calculate_sale_item_pricing(
            product=product,
            pricing_type="RETAIL",
            quantity=quantity,
        )


def test_pricing_rejects_packaging_from_another_product(product):
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

    packaging = ProductPackaging.objects.create(
        product=another_product,
        name="Carton",
        conversion_factor=24,
    )

    with pytest.raises(ValidationError):
        calculate_sale_item_pricing(
            product=product,
            pricing_type="RETAIL",
            quantity=1,
            packaging=packaging,
        )


def test_pricing_rejects_inactive_packaging(product, carton):
    carton.is_active = False
    carton.save()

    with pytest.raises(ValidationError):
        calculate_sale_item_pricing(
            product=product,
            pricing_type="RETAIL",
            quantity=1,
            packaging=carton,
        )


def test_pricing_rejects_packaging_disabled_for_sales(product, carton):
    carton.sales_enabled = False
    carton.save()

    with pytest.raises(ValidationError):
        calculate_sale_item_pricing(
            product=product,
            pricing_type="RETAIL",
            quantity=1,
            packaging=carton,
        )


def test_wholesale_rejects_quantity_below_minimum(product):
    product.wholesale_min_quantity = 12
    product.save()

    with pytest.raises(
        ValidationError,
        match="Wholesale pricing requires at least 12",
    ):
        calculate_sale_item_pricing(
            product=product,
            pricing_type="WHOLESALE",
            quantity=11,
        )


def test_wholesale_accepts_quantity_equal_to_minimum(product):
    product.wholesale_min_quantity = 12
    product.save()

    result = calculate_sale_item_pricing(
        product=product,
        pricing_type="WHOLESALE",
        quantity=12,
    )

    assert result["base_quantity"] == 12
    assert result["total_amount"] == 2760


def test_wholesale_accepts_one_carton_when_minimum_is_12(
    product, carton
):
    product.wholesale_min_quantity = 12
    product.save()

    result = calculate_sale_item_pricing(
        product=product,
        pricing_type="WHOLESALE",
        quantity=1,
        packaging=carton,
    )

    assert result["base_quantity"] == 12
    assert result["total_amount"] == 2760


def test_wholesale_rejects_carton_below_minimum(product):
    product.wholesale_min_quantity = 12
    product.save()

    small_packaging = ProductPackaging.objects.create(
        product=product,
        name="Pack of 6",
        conversion_factor=6,
        purchase_enabled=True,
        sales_enabled=True,
    )

    with pytest.raises(ValidationError):
        calculate_sale_item_pricing(
            product=product,
            pricing_type="WHOLESALE",
            quantity=1,
            packaging=small_packaging,
        )


def test_retail_remains_available_below_wholesale_minimum(product):
    product.wholesale_min_quantity = 12
    product.save()

    result = calculate_sale_item_pricing(
        product=product,
        pricing_type="RETAIL",
        quantity=1,
    )

    assert result["selling_price_per_package"] == 250
    assert result["total_amount"] == 250