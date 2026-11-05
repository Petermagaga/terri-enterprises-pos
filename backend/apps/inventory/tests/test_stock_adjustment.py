
from decimal import Decimal
from datetime import timedelta

import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.inventory.models import (
    InventoryBalance,
    ProductPackaging,
    StockBatch,
    StockMovement,
)
from apps.inventory.services.purchase_creation import (
    add_purchase_item,
    create_purchase,
)
from apps.inventory.services.purchase_receiving import receive_purchase
from apps.inventory.services.stock_adjustment import adjust_stock
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.suppliers.models import Supplier


pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    User = get_user_model()
    return User.objects.create_user(
        username="adjustment_owner",
        password="test-password",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier():
    User = get_user_model()
    return User.objects.create_user(
        username="adjustment_cashier",
        password="test-password",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def supplier():
    return Supplier.objects.create(
        name="Adjustment Distributors",
        phone="0712345678",
    )


@pytest.fixture
def product_and_packaging():
    category = Category.objects.create(name="Adjustment Groceries")
    family = ProductFamily.objects.create(name="Adjustment Cooking Oil")

    product = create_product(
        name="Adjustment Cooking Oil 1L",
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


def test_owner_can_increase_stock(owner, product_and_packaging):
    product, packaging = product_and_packaging

    result = adjust_stock(
        product=product,
        quantity=Decimal("10"),
        movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
        created_by=owner,
        reason="Physical stock count correction",
        unit_cost=Decimal("120.000000"),
        reference="COUNT-001",
    )

    balance = InventoryBalance.objects.get(product=product)

    assert balance.quantity_on_hand == Decimal("10")

    assert result["batch"].received_quantity == Decimal("10")
    assert result["batch"].remaining_quantity == Decimal("10")
    assert result["batch"].landed_unit_cost == Decimal("120.000000")
    assert result["batch"].purchase_item is None

    assert result["movement"].movement_type == (
        StockMovement.MovementType.ADJUSTMENT_IN
    )
    assert result["movement"].direction == StockMovement.Direction.IN
    assert result["movement"].quantity == Decimal("10")
    assert result["movement"].created_by == owner
    assert result["movement"].notes == "Physical stock count correction"


def test_cashier_cannot_increase_stock(cashier, product_and_packaging):
    product, packaging = product_and_packaging

    with pytest.raises(
        ValidationError,
        match="Only an active business owner",
    ):
        adjust_stock(
            product=product,
            quantity=Decimal("10"),
            movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
            created_by=cashier,
            reason="Attempted stock increase",
            unit_cost=Decimal("120.000000"),
        )

    assert StockBatch.objects.filter(product=product).count() == 0
    assert StockMovement.objects.filter(product=product).count() == 0
    assert not InventoryBalance.objects.filter(product=product).exists()


def test_owner_reduces_stock_using_fifo(
    owner,
    supplier,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    older_batch = create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=10,
        unit_cost=100,
        received_at=timezone.now() - timedelta(days=2),
    )

    newer_batch = create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=10,
        unit_cost=150,
        received_at=timezone.now() - timedelta(days=1),
    )

    result = adjust_stock(
        product=product,
        quantity=Decimal("12"),
        movement_type=StockMovement.MovementType.ADJUSTMENT_OUT,
        created_by=owner,
        reason="Physical stock count correction",
        reference="COUNT-002",
    )

    older_batch.refresh_from_db()
    newer_batch.refresh_from_db()

    balance = InventoryBalance.objects.get(product=product)

    assert older_batch.remaining_quantity == Decimal("0")
    assert newer_batch.remaining_quantity == Decimal("8")
    assert balance.quantity_on_hand == Decimal("8")

    assert len(result["deductions"]) == 2
    assert result["deductions"][0]["quantity"] == Decimal("10")
    assert result["deductions"][0]["unit_cost"] == Decimal("100.000000")
    assert result["deductions"][1]["quantity"] == Decimal("2")
    assert result["deductions"][1]["unit_cost"] == Decimal("150.000000")

    assert StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.ADJUSTMENT_OUT,
    ).count() == 2


def test_owner_cannot_reduce_more_stock_than_available(
    owner,
    supplier,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    batch = create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=5,
        unit_cost=100,
        received_at=timezone.now(),
    )

    with pytest.raises(ValidationError, match="Insufficient stock"):
        adjust_stock(
            product=product,
            quantity=Decimal("8"),
            movement_type=StockMovement.MovementType.ADJUSTMENT_OUT,
            created_by=owner,
            reason="Physical stock count correction",
        )

    batch.refresh_from_db()

    balance = InventoryBalance.objects.get(product=product)

    assert batch.remaining_quantity == Decimal("5")
    assert balance.quantity_on_hand == Decimal("5")

    assert StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.ADJUSTMENT_OUT,
    ).count() == 0


def test_owner_can_write_off_damaged_stock(
    owner,
    supplier,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    batch = create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=10,
        unit_cost=100,
        received_at=timezone.now(),
    )

    result = adjust_stock(
        product=product,
        quantity=Decimal("3"),
        movement_type=StockMovement.MovementType.DAMAGE,
        created_by=owner,
        reason="Three bottles were damaged during handling",
        reference="DAMAGE-001",
    )

    batch.refresh_from_db()

    balance = InventoryBalance.objects.get(product=product)

    assert batch.remaining_quantity == Decimal("7")
    assert balance.quantity_on_hand == Decimal("7")

    assert len(result["deductions"]) == 1
    assert result["deductions"][0]["quantity"] == Decimal("3")
    assert result["deductions"][0]["unit_cost"] == Decimal("100.000000")

    movement = StockMovement.objects.get(
        product=product,
        movement_type=StockMovement.MovementType.DAMAGE,
    )

    assert movement.direction == StockMovement.Direction.OUT
    assert movement.quantity == Decimal("3")
    assert movement.notes == "Three bottles were damaged during handling"
    assert movement.reference == "DAMAGE-001"
    assert movement.created_by == owner


def test_adjustment_requires_a_reason(owner, product_and_packaging):
    product, packaging = product_and_packaging

    with pytest.raises(
        ValidationError,
        match="adjustment reason is required",
    ):
        adjust_stock(
            product=product,
            quantity=Decimal("5"),
            movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
            created_by=owner,
            reason="   ",
            unit_cost=Decimal("100"),
        )

    assert StockBatch.objects.filter(product=product).count() == 0
    assert StockMovement.objects.filter(product=product).count() == 0


def test_stock_increase_requires_unit_cost(owner, product_and_packaging):
    product, packaging = product_and_packaging

    with pytest.raises(
        ValidationError,
        match="Unit cost is required",
    ):
        adjust_stock(
            product=product,
            quantity=Decimal("5"),
            movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
            created_by=owner,
            reason="Opening stock correction",
        )

    assert StockBatch.objects.filter(product=product).count() == 0
    assert StockMovement.objects.filter(product=product).count() == 0


def test_stock_increase_rejects_negative_unit_cost(
    owner,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    with pytest.raises(
        ValidationError,
        match="Unit cost cannot be negative",
    ):
        adjust_stock(
            product=product,
            quantity=Decimal("5"),
            movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
            created_by=owner,
            reason="Opening stock correction",
            unit_cost=Decimal("-100"),
        )

    assert StockBatch.objects.filter(product=product).count() == 0
    assert StockMovement.objects.filter(product=product).count() == 0


def test_stock_reduction_rejects_manual_unit_cost(
    owner,
    supplier,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=10,
        unit_cost=100,
        received_at=timezone.now(),
    )

    with pytest.raises(
        ValidationError,
        match="Unit cost must not be supplied",
    ):
        adjust_stock(
            product=product,
            quantity=Decimal("3"),
            movement_type=StockMovement.MovementType.ADJUSTMENT_OUT,
            created_by=owner,
            reason="Physical stock correction",
            unit_cost=Decimal("50"),
        )

    balance = InventoryBalance.objects.get(product=product)

    assert balance.quantity_on_hand == Decimal("10")

    assert StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.ADJUSTMENT_OUT,
    ).count() == 0

def test_stock_increase_stops_when_balance_does_not_match_batches(
    owner,
    supplier,
    product_and_packaging,
):
    product, packaging = product_and_packaging

    create_received_batch(
        supplier=supplier,
        owner=owner,
        product=product,
        packaging=packaging,
        quantity=10,
        unit_cost=100,
        received_at=timezone.now(),
    )

    balance = InventoryBalance.objects.get(product=product)

    # Simulate an existing inventory data inconsistency.
    balance.quantity_on_hand = Decimal("12")
    balance.save(update_fields=["quantity_on_hand", "updated_at"])

    with pytest.raises(
        ValidationError,
        match="Inventory balance does not match available stock batches",
    ):
        adjust_stock(
            product=product,
            quantity=Decimal("5"),
            movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
            created_by=owner,
            reason="Physical stock count correction",
            unit_cost=Decimal("100"),
        )

    balance.refresh_from_db()

    assert balance.quantity_on_hand == Decimal("12")

    assert StockBatch.objects.filter(product=product).count() == 1
    assert StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.ADJUSTMENT_IN,
    ).count() == 0