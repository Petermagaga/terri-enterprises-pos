from django.core.exceptions import ValidationError
from django.db import transaction
from apps.products.models import Product
from apps.inventory.models import Purchase,PurchaseItem,ProductPackaging
from apps.suppliers.models import Supplier


@transaction.atomic
def create_purchase(*, supplier, created_by, purchase_date=None,
                    supplier_reference="", transport_cost="0.00"):
    """
    Create a draft stock purchase.

    Creating a purchase does not increase inventory.
    Stock is updated only when the purchase is received.
    """

    if not isinstance(supplier, Supplier):
        raise ValidationError("A valid supplier is required.")

    try:
        supplier = Supplier.objects.select_for_update().get(pk=supplier.pk)
    except Supplier.DoesNotExist:
        raise ValidationError("The selected supplier does not exist.")

    if not supplier.is_active:
        raise ValidationError("Cannot create a purchase for an inactive supplier.")


    purchase = Purchase(
        supplier=supplier,
        created_by=created_by,
        supplier_reference=supplier_reference.strip(),
        transport_cost=transport_cost,
    )

    if purchase_date is not None:
        purchase.purchase_date = purchase_date

    purchase.full_clean()
    purchase.save()

    return purchase

@transaction.atomic
def add_purchase_item(
    *,
    purchase,
    product,
    packaging,
    package_quantity,
    purchase_unit_cost,
):
    """
    Add a product line to a draft purchase.

    Packaging details are snapshotted to preserve historical accuracy.
    """

    if not isinstance(purchase, Purchase):
        raise ValidationError("A valid purchase is required.")

    if not isinstance(product, Product):
        raise ValidationError("A valid product is required.")

    if not isinstance(packaging, ProductPackaging):
        raise ValidationError("A valid packaging option is required.")

    try:
        purchase = (
            Purchase.objects
            .select_for_update()
            .get(pk=purchase.pk)
        )
    except Purchase.DoesNotExist:
        raise ValidationError("The selected purchase does not exist.")

    if purchase.status != Purchase.Status.DRAFT:
        raise ValidationError("Items can only be added to draft purchases.")

    try:
        product = (
            Product.objects
            .select_for_update()
            .get(pk=product.pk)
        )
    except Product.DoesNotExist:
        raise ValidationError("The selected product does not exist.")

    if not product.is_active:
        raise ValidationError("Cannot purchase an inactive product.")

    try:
        packaging = (
            ProductPackaging.objects
            .select_for_update()
            .get(pk=packaging.pk)
        )
    except ProductPackaging.DoesNotExist:
        raise ValidationError("The selected packaging option does not exist.")

    if packaging.product_id != product.pk:
        raise ValidationError(
            "This packaging option belongs to a different product."
        )

    if not packaging.is_active:
        raise ValidationError("This packaging option is inactive.")

    if not packaging.purchase_enabled:
        raise ValidationError(
            "This packaging option is not enabled for purchasing."
        )

    purchase_item = PurchaseItem(
        purchase=purchase,
        product=product,
        packaging=packaging,
        packaging_name_snapshot=packaging.name,
        conversion_factor_snapshot=packaging.conversion_factor,
        package_quantity=package_quantity,
        purchase_unit_cost=purchase_unit_cost,
    )

    purchase_item.full_clean()
    purchase_item.save()

    return purchase_item