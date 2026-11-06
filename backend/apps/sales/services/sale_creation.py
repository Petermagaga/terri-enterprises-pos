from django.core.exceptions import ValidationError
from django.db import transaction

from apps.accounts.models import User
from apps.products.models import Product
from apps.inventory.models import ProductPackaging
from apps.sales.models import Sale, SaleItem

from apps.sales.services.pricing import calculate_sale_item_pricing


@transaction.atomic
def create_sale(*, processed_by):
    """
    Create a draft sale.

    Stock is not deducted until the sale is completed.
    """

    if not isinstance(processed_by, User):
        raise ValidationError("A valid user is required.")

    if not processed_by.is_active:
        raise ValidationError("An inactive user cannot process sales.")

    if processed_by.role not in {
        User.Role.OWNER,
        User.Role.CASHIER,
    }:
        raise ValidationError("This user is not allowed to process sales.")

    sale = Sale(
        processed_by=processed_by,
    )

    sale.full_clean()
    sale.save()

    return sale


@transaction.atomic
def add_sale_item(
    *,
    sale,
    product,
    pricing_type,
    quantity,
    packaging=None,
):
    """
    Add a product line to a draft sale.

    Selling prices are calculated by the pricing service.
    Stock is not deducted at this stage.
    """

    if not isinstance(sale, Sale):
        raise ValidationError("A valid sale is required.")

    if not isinstance(product, Product):
        raise ValidationError("A valid product is required.")

    try:
        sale = (
            Sale.objects
            .select_for_update()
            .get(pk=sale.pk)
        )
    except Sale.DoesNotExist:
        raise ValidationError("The selected sale does not exist.")

    if sale.status != Sale.Status.DRAFT:
        raise ValidationError("Items can only be added to draft sales.")

    try:
        product = (
            Product.objects
            .select_for_update()
            .get(pk=product.pk)
        )
    except Product.DoesNotExist:
        raise ValidationError("The selected product does not exist.")

    if packaging is not None:
        if not isinstance(packaging, ProductPackaging):
            raise ValidationError("A valid packaging option is required.")

        try:
            packaging = (
                ProductPackaging.objects
                .select_for_update()
                .get(pk=packaging.pk)
            )
        except ProductPackaging.DoesNotExist:
            raise ValidationError("The selected packaging does not exist.")

    pricing = calculate_sale_item_pricing(
        product=product,
        pricing_type=pricing_type,
        quantity=quantity,
        packaging=packaging,
    )

    sale_item_data = {
        key: value
        for key, value in pricing.items()
        if key != "base_quantity"
    }

    sale_item = SaleItem(
        sale=sale,
        product=product,
        packaging=packaging,
        **sale_item_data,
    )

    sale_item.full_clean()
    sale_item.save()

    sale.total_amount += sale_item.total_amount
    sale.save(update_fields=["total_amount"])

    return sale_item