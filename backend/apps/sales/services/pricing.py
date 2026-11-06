from decimal import Decimal

from django.core.exceptions import ValidationError

from apps.inventory.models import ProductPackaging
from apps.products.models import Product


def calculate_sale_item_pricing(
    *,
    product,
    pricing_type,
    quantity,
    packaging=None,
):
    """
    Calculate a sale item's package price and total amount.

    The product's stored retail or wholesale price is the
    price of one individual base unit.
    """

    if not isinstance(product, Product):
        raise ValidationError("A valid product is required.")

    if not product.is_active:
        raise ValidationError("Cannot sell an inactive product.")

    if pricing_type not in {"RETAIL", "WHOLESALE"}:
        raise ValidationError("Invalid pricing type.")

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValidationError("Quantity must be a whole number.")

    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")

    if packaging is None:
        packaging_name = product.base_unit
        conversion_factor = 1

    else:
        if not isinstance(packaging, ProductPackaging):
            raise ValidationError("Invalid packaging selection.")

        if packaging.product_id != product.pk:
            raise ValidationError(
                "The selected packaging does not belong to this product."
            )

        if not packaging.is_active or not packaging.sales_enabled:
            raise ValidationError(
                "The selected packaging is not available for sale."
            )

        packaging_name = packaging.name
        conversion_factor = packaging.conversion_factor

    if pricing_type == "RETAIL":
        base_unit_price = product.retail_price
    else:
        base_unit_price = product.wholesale_price

    selling_price_per_package = (
        Decimal(str(base_unit_price)) * conversion_factor
    )

    total_amount = selling_price_per_package * quantity

    return {
        "product_name_snapshot": product.name,
        "product_sku_snapshot": product.sku,
        "base_unit_snapshot": product.base_unit,
        "packaging_name_snapshot": packaging_name,
        "conversion_factor_snapshot": conversion_factor,
        "pricing_type": pricing_type,
        "quantity": quantity,
        "selling_price_per_package": selling_price_per_package,
        "total_amount": total_amount,
        "base_quantity": quantity * conversion_factor,
    }