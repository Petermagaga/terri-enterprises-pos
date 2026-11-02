
import pytest

from decimal import Decimal
from django.core.exceptions import ValidationError

from apps.products.models import Category, Product, ProductFamily
from apps.products.services.product_creation import create_product


pytestmark = pytest.mark.django_db


@pytest.fixture
def category():
    return Category.objects.create(name="Groceries")


@pytest.fixture
def family():
    return ProductFamily.objects.create(name="Margarine")


def test_product_is_created_with_automatically_generated_sku(
    category, family
):
    product = create_product(
        name="Margarine 50g",
        product_family=family,
        category=category,
        size_value=50,
        size_unit="G",
        base_unit="tub",
        retail_price=60,
        wholesale_price=55,
    )

    assert product.pk is not None
    assert product.sku == "MARG-050G"
    assert Product.objects.filter(pk=product.pk).exists()


def test_product_creation_does_not_require_a_manual_sku(
    category, family
):
    product = create_product(
        name="Margarine 500g",
        product_family=family,
        category=category,
        size_value=500,
        size_unit="G",
        base_unit="tub",
        retail_price=250,
        wholesale_price=230,
    )

    assert product.sku == "MARG-500G"


def test_invalid_product_data_is_rejected(category, family):
    with pytest.raises(ValidationError):
        create_product(
            name="Invalid Margarine",
            product_family=family,
            category=category,
            size_value=0,
            size_unit="G",
            base_unit="tub",
            retail_price=60,
            wholesale_price=55,
        )

    assert Product.objects.count() == 0


def test_product_creation_rolls_back_family_prefix_on_failure(
    category, family
):
    with pytest.raises(ValidationError):
        create_product(
            name="Invalid Margarine",
            product_family=family,
            category=category,
            size_value=50,
            size_unit="INVALID",
            base_unit="tub",
            retail_price=60,
            wholesale_price=55,
        )

    family.refresh_from_db()

    assert family.sku_prefix is None
    assert Product.objects.count() == 0
