from decimal import Decimal
from django.core.exceptions import ValidationError
import pytest

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.inventory.models import (
    InventoryBalance,
    ProductPackaging,
    Purchase,
    StockBatch,
    StockMovement,
)
from apps.inventory.services.purchase_creation import (
    add_purchase_item,
    create_purchase,
)
from apps.inventory.services.purchase_receiving import receive_purchase
from apps.inventory.services.stock_deduction import deduct_stock_fifo
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.suppliers.models import Supplier


pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    User = get_user_model()
    return User.objects.create_user(
        username="fifo_owner",
        password="test-password",
    )


@pytest.fixture
def supplier():
    return Supplier.objects.create(
        name="FIFO Distributors",
        phone="0712345678",
    )


@pytest.fixture
def product_and_packaging():
    category = Category.objects.create(name="FIFO Groceries")
    family = ProductFamily.objects.create(name="FIFO Cooking Oil")

    product = create_product(
        name="FIFO Cooking Oil 1L",
        product_family=family,
        category=category,
        size_value=1000,
        size_unit="ML",
        base_unit="bottle",
        retail_price=250,
        wholesale_price=230,
    )

    packaging = ProductPackaging.objects.create(
        product=product,
        name="Bottle",
        conversion_factor=1,
    )

    return product, packaging


def create_received_batch(
    *,
    supplier,
    owner,
    product,
    packaging,
    quantity,
    unit_cost,
    received_at,
):
    """
    Create a real received purchase and return its stock batch.
    """

    purchase = create_purchase(
        supplier=supplier,
        created_by=owner,
        transport_cost=Decimal("0.00"),
    )

    add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity=Decimal(str(quantity)),
        purchase_unit_cost=Decimal(str(unit_cost)),
    )

    batches = receive_purchase(
        purchase=purchase,
        received_at=received_at,
    )

    return batches[0]

def test_deduct_stock_uses_oldest_batch_first(
    supplier, owner, product_and_packaging
):
    product, packaging = product_and_packaging
    now = timezone.now()

    # Older batch: 8 bottles at KSh 100 each.
    first_batch = create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=8,
        unit_cost="100.00",
        received_at=now - timedelta(days=2),
    )

    # Newer batch: 24 bottles at KSh 120 each.
    second_batch = create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=24,
        unit_cost="120.00",
        received_at=now - timedelta(days=1),
    )

    deductions = deduct_stock_fifo(
        product=product,
        quantity=Decimal("10.000"),
        created_by=owner,
        reference="TEST-SALE-001",
    )

    # The oldest batch is exhausted first.
    assert first_batch.__class__.objects.get(
        pk=first_batch.pk
    ).remaining_quantity == Decimal("0.000")

    # The remaining 2 bottles come from the newer batch.
    assert second_batch.__class__.objects.get(
        pk=second_batch.pk
    ).remaining_quantity == Decimal("22.000")

    assert len(deductions) == 2

    assert deductions[0]["quantity"] == Decimal("8.000")
    assert deductions[0]["unit_cost"] == Decimal("100.000000")
    assert deductions[0]["total_cost"] == Decimal("800.000000")

    assert deductions[1]["quantity"] == Decimal("2.000")
    assert deductions[1]["unit_cost"] == Decimal("120.000000")
    assert deductions[1]["total_cost"] == Decimal("240.000000")

    # Total cost of goods sold: KSh 1,040.
    total_cost = sum(
        (item["total_cost"] for item in deductions),
        Decimal("0.000000"),
    )
    assert total_cost == Decimal("1040.000000")

    balance = InventoryBalance.objects.get(product=product)
    assert balance.quantity_on_hand == Decimal("22.000")

    sale_movements = StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.SALE,
    )

    assert sale_movements.count() == 2

    movements = list(
        sale_movements.order_by("stock_batch__received_at")
    )

    assert movements[0].stock_batch_id == first_batch.pk
    assert movements[0].quantity == Decimal("8.000")
    assert movements[0].unit_cost == Decimal("100.000000")
    assert movements[0].direction == StockMovement.Direction.OUT

    assert movements[1].stock_batch_id == second_batch.pk
    assert movements[1].quantity == Decimal("2.000")
    assert movements[1].unit_cost == Decimal("120.000000")
    assert movements[1].direction == StockMovement.Direction.OUT


def test_deduction_rejects_insufficient_stock_without_changes(
    supplier, owner, product_and_packaging
):
    product, packaging = product_and_packaging

    batch = create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=10,
        unit_cost="100.00",
        received_at=timezone.now(),
    )

    with pytest.raises(ValidationError, match="Insufficient stock"):
        deduct_stock_fifo(
            product=product,
            quantity=Decimal("15.000"),
            created_by=owner,
            reference="TEST-SALE-002",
        )

    batch.refresh_from_db()
    assert batch.remaining_quantity == Decimal("10.000")

    balance = InventoryBalance.objects.get(product=product)
    assert balance.quantity_on_hand == Decimal("10.000")

    assert not StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.SALE,
    ).exists()

def test_deduction_rejects_inconsistent_inventory_balance(
    supplier, owner, product_and_packaging
):
    product, packaging = product_and_packaging

    create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=10,
        unit_cost="100.00",
        received_at=timezone.now(),
    )

    balance = InventoryBalance.objects.get(product=product)

    # Simulate an inventory inconsistency.
    balance.quantity_on_hand = Decimal("8.000")
    balance.save(update_fields=["quantity_on_hand", "updated_at"])

    with pytest.raises(
        ValidationError,
        match="Inventory balance does not match",
    ):
        deduct_stock_fifo(
            product=product,
            quantity=Decimal("2.000"),
            created_by=owner,
            reference="TEST-SALE-003",
        )

    # No stock batch or sale movement should be changed.
    batch = StockBatch.objects.get(product=product)
    assert batch.remaining_quantity == Decimal("10.000")

    assert not StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.SALE,
    ).exists()

def test_failed_fifo_deduction_rolls_back_all_changes(
    supplier, owner, product_and_packaging, monkeypatch
):
    product, packaging = product_and_packaging
    now = timezone.now()

    first_batch = create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=5,
        unit_cost="100.00",
        received_at=now - timedelta(days=2),
    )

    second_batch = create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=5,
        unit_cost="120.00",
        received_at=now - timedelta(days=1),
    )

    original_save = StockMovement.save
    save_calls = 0

    def failing_save(self, *args, **kwargs):
        nonlocal save_calls
        save_calls += 1

        if save_calls == 2:
            raise ValidationError("Simulated sale movement failure.")

        return original_save(self, *args, **kwargs)

    monkeypatch.setattr(StockMovement, "save", failing_save)

    with pytest.raises(
        ValidationError,
        match="Simulated sale movement failure",
    ):
        deduct_stock_fifo(
            product=product,
            quantity=Decimal("7.000"),
            created_by=owner,
            reference="TEST-SALE-ROLLBACK",
        )

    first_batch.refresh_from_db()
    second_batch.refresh_from_db()

    assert first_batch.remaining_quantity == Decimal("5.000")
    assert second_batch.remaining_quantity == Decimal("5.000")

    balance = InventoryBalance.objects.get(product=product)
    assert balance.quantity_on_hand == Decimal("10.000")

    # The two original purchase movements remain.
    assert StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.PURCHASE_RECEIPT,
    ).count() == 2

    # No partial sale movement remains.
    assert not StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.SALE,
    ).exists()