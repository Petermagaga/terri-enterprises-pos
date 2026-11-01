
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.products.models import Category, Product, ProductFamily
from apps.products.services.sku import generate_product_sku


@transaction.atomic
def create_product(
    *,
    name,
    product_family,
    category,
    size_value,
    size_unit,
    base_unit,
    retail_price,
    wholesale_price,
    brand="",
    reorder_level=0,
    is_active=True,
):
    """
    Create a product with an automatically generated, permanent SKU.

    SKU generation and product creation happen within one transaction.
    If product validation or saving fails, the transaction is rolled back.
    """

    # Ensure the family and category are valid saved model instances.
    if not isinstance(product_family, ProductFamily):
        raise ValidationError("A valid product family is required.")

    if not isinstance(category, Category):
        raise ValidationError("A valid product category is required.")

    if product_family.pk is None:
        raise ValidationError("Save the product family before creating a product.")

    if category.pk is None:
        raise ValidationError("Save the category before creating a product.")

    # Generate the SKU internally. The caller cannot supply one.
    sku = generate_product_sku(
        family=product_family,
        size_value=size_value,
        size_unit=size_unit,
    )

    product = Product(
        name=name,
        product_family=product_family,
        category=category,
        sku=sku,
        size_value=size_value,
        size_unit=size_unit,
        base_unit=base_unit,
        retail_price=retail_price,
        wholesale_price=wholesale_price,
        brand=brand,
        reorder_level=reorder_level,
        is_active=is_active,
    )

    # Run field, choice, and uniqueness validation before saving.
    product.full_clean()

    product.save()

    return product
