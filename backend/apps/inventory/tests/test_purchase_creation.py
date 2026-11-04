from decimal import Decimal

import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.inventory.models import Purchase, StockBatch
from apps.inventory.services.purchase_creation import create_purchase
from apps.suppliers.models import Supplier


pytestmark = pytest.mark.django_db


@pytest.fixture
def supplier():
    return Supplier.objects.create(
        name="ABC Distributors",
        phone="0712345678",
    )


@pytest.fixture
def owner():
    User = get_user_model()

    return User.objects.create_user(
        username="purchase_owner",
        password="test-password",
    )


def test_purchase_is_created_successfully(supplier, owner):
    purchase = create_purchase(
        supplier=supplier,
        created_by=owner,
        supplier_reference="INV-001",
        transport_cost=Decimal("500.00"),
    )

    assert purchase.pk is not None
    assert purchase.supplier == supplier
    assert purchase.created_by == owner
    assert purchase.supplier_reference == "INV-001"
    assert purchase.transport_cost == Decimal("500.00")


def test_new_purchase_has_draft_status(supplier, owner):
    purchase = create_purchase(
        supplier=supplier,
        created_by=owner,
    )

    assert purchase.status == Purchase.Status.DRAFT
    assert purchase.received_at is None


def test_purchase_rejects_inactive_supplier(owner):
    inactive_supplier = Supplier.objects.create(
        name="Inactive Distributors",
        phone="0722222222",
        is_active=False,
    )

    with pytest.raises(ValidationError):
        create_purchase(
            supplier=inactive_supplier,
            created_by=owner,
        )

    assert Purchase.objects.count() == 0


def test_purchase_rejects_invalid_supplier(owner):
    with pytest.raises(ValidationError):
        create_purchase(
            supplier="ABC Distributors",
            created_by=owner,
        )

    assert Purchase.objects.count() == 0


def test_purchase_rejects_negative_transport_cost(supplier, owner):
    with pytest.raises(ValidationError):
        create_purchase(
            supplier=supplier,
            created_by=owner,
            transport_cost=Decimal("-100.00"),
        )

    assert Purchase.objects.count() == 0


def test_creating_purchase_does_not_create_stock(supplier, owner):
    create_purchase(
        supplier=supplier,
        created_by=owner,
    )

    assert StockBatch.objects.count() == 0