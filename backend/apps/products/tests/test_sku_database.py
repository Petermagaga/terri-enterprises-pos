import pytest

from django.core.exceptions import ValidationError

from apps.products.models import Category, Product, ProductFamily
from apps.products.services.sku import (
    assign_family_prefix,
    generate_product_sku,
)


pytestmark = pytest.mark.django_db


def create_category():
    return Category.objects.create(name="Groceries")


def test_family_receives_a_unique_prefix():
    family = ProductFamily.objects.create(name="Margarine")

    prefix = assign_family_prefix(family)

    assert prefix == "MARG"
    assert ProductFamily.objects.get(pk=family.pk).sku_prefix == "MARG"


def test_colliding_family_names_receive_different_prefixes():
    first_family = ProductFamily.objects.create(name="Margarine")
    second_family = ProductFamily.objects.create(name="Margaret")

    first_prefix = assign_family_prefix(first_family)
    second_prefix = assign_family_prefix(second_family)

    assert first_prefix == "MARG"
    assert second_prefix != first_prefix
    assert len(second_prefix) == 4


def test_short_family_name_receives_a_valid_prefix():
    family = ProductFamily.objects.create(name="OMO")

    prefix = assign_family_prefix(family)

    assert prefix == "OMOA"
    assert len(prefix) == 4


def test_product_sku_is_generated_using_family_and_size():
    family = ProductFamily.objects.create(name="Margarine")

    sku = generate_product_sku(family, 50, "G")

    assert sku == "MARG-050G"


def test_product_sku_remains_unchanged_when_product_details_change():
    family = ProductFamily.objects.create(name="Margarine")
    category = create_category()

    product = Product.objects.create(
        name="Margarine 50g",
        product_family=family,
        category=category,
        sku=generate_product_sku(family, 50, "G"),
        size_value=50,
        size_unit="G",
        base_unit="piece",
        retail_price=60,
        wholesale_price=55,
    )

    original_sku = product.sku

    product.name = "Premium Margarine 50g"
    product.retail_price = 65
    product.save()

    product.refresh_from_db()

    assert product.sku == original_sku
    assert product.name == "Premium Margarine 50g"
    assert product.retail_price == 65


def test_product_sku_cannot_be_changed_through_model_save():
    family = ProductFamily.objects.create(name="Margarine")
    category = create_category()

    product = Product.objects.create(
        name="Margarine 50g",
        product_family=family,
        category=category,
        sku=generate_product_sku(family, 50, "G"),
        size_value=50,
        size_unit="G",
        base_unit="piece",
        retail_price=60,
        wholesale_price=55,
    )

    product.sku = "TEST-050G"

    with pytest.raises(ValidationError, match="SKU cannot be changed"):
        product.save()