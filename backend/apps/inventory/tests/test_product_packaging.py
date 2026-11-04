import pytest

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.inventory.models import ProductPackaging
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product


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


def test_product_packaging_is_created_successfully(product):
    packaging = ProductPackaging.objects.create(
        product=product,
        name="Carton",
        conversion_factor=12,
        purchase_enabled=True,
        sales_enabled=True,
    )

    assert packaging.pk is not None
    assert packaging.conversion_factor == 12
    assert packaging.product == product


def test_product_packaging_rejects_zero_conversion_factor(product):
    with pytest.raises(ValidationError):
        ProductPackaging.objects.create(
            product=product,
            name="Invalid Pack",
            conversion_factor=0,
        )

    assert ProductPackaging.objects.count() == 0


def test_product_packaging_rejects_empty_name(product):
    with pytest.raises(ValidationError):
        ProductPackaging.objects.create(
            product=product,
            name="   ",
            conversion_factor=6,
        )

    assert ProductPackaging.objects.count() == 0


def test_product_packaging_requires_purchase_or_sales_enabled(product):
    with pytest.raises(ValidationError):
        ProductPackaging.objects.create(
            product=product,
            name="Disabled Pack",
            conversion_factor=6,
            purchase_enabled=False,
            sales_enabled=False,
        )

    assert ProductPackaging.objects.count() == 0


def test_product_packaging_rejects_duplicate_name_for_same_product(product):
    ProductPackaging.objects.create(
        product=product,
        name="Carton",
        conversion_factor=12,
    )

    with pytest.raises(ValidationError):
        ProductPackaging.objects.create(
            product=product,
            name="Carton",
            conversion_factor=24,
        )

def test_same_packaging_name_is_allowed_for_different_products(product):
    category = Category.objects.create(name="Beverages")
    family = ProductFamily.objects.create(name="Juice")

    second_product = create_product(
        name="Orange Juice 500ml",
        product_family=family,
        category=category,
        size_value=500,
        size_unit="ML",
        base_unit="bottle",
        retail_price=100,
        wholesale_price=90,
    )

    first_packaging = ProductPackaging.objects.create(
        product=product,
        name="Carton",
        conversion_factor=12,
    )

    second_packaging = ProductPackaging.objects.create(
        product=second_product,
        name="Carton",
        conversion_factor=24,
    )

    assert first_packaging.name == second_packaging.name
    assert first_packaging.product != second_packaging.product