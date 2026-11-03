from django.db import transaction

from apps.suppliers.models import Supplier


@transaction.atomic
def create_supplier(**validated_data):
    supplier = Supplier(**validated_data)

    supplier.full_clean()
    supplier.save()

    return supplier


@transaction.atomic
def update_supplier(supplier, **validated_data):
    for field, value in validated_data.items():
        setattr(supplier, field, value)

    supplier.full_clean()
    supplier.save()

    return supplier