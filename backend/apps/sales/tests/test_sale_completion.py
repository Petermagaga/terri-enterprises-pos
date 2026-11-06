
import pytest

from decimal import Decimal

from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.inventory.models import (
    InventoryBalance,
    ProductPackaging,
    StockBatch,
    StockMovement,
    Purchase,
)
from apps.inventory.services.purchase_creation import (
    create_purchase,
    add_purchase_item,
)
from apps.inventory.services.purchase_receiving import receive_purchase
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.sales.models import Sale, SalePayment
from apps.sales.services.sale_creation import create_sale, add_sale_item
from apps.sales.services.payment_creation import add_sale_payment
from apps.sales.services.sale_completion import complete_sale
from apps.suppliers.models import Supplier


pytestmark = pytest.mark.django_db


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="completion_cashier",
        email="completion@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def supplier():
    return Supplier.objects.create(
        name="Completion Distributors",
        phone="0712345678",
    )


@pytest.fixture
def product():
    category = Category.objects.create(name="Completion Groceries")
    family = ProductFamily.objects.create(name="Completion Oil")

    return create_product(
        name="Cooking Oil 1L",
        product_family=family,
        category=category,
        size_value=1000,
        size_unit="ML",
        base_unit="bottle",
        retail_price=250,
        wholesale_price=230,
    )


@pytest.fixture
def carton(product):
    return ProductPackaging.objects.create(
        product=product,
        name="Carton",
        conversion_factor=12,
        purchase_enabled=True,
        sales_enabled=True,
    )


@pytest.fixture
def stocked_product(product, carton, supplier, cashier):
    purchase = create_purchase(
        supplier=supplier,
        created_by=cashier,
        transport_cost=Decimal("0.00"),
    )

    add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=carton,
        package_quantity=2,
        purchase_unit_cost=Decimal("1200.00"),
    )

    batches = receive_purchase(purchase=purchase)

    return batches[0]


@pytest.fixture
def paid_sale(product, cashier, stocked_product):
    sale = create_sale(processed_by=cashier)

    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=2,
    )

    add_sale_payment(
        sale=sale,
        payment_method=SalePayment.PaymentMethod.CASH,
        amount=Decimal("500.00"),
        received_by=cashier,
    )

    return sale


def test_complete_sale_deducts_stock_and_records_fifo_cost(
    paid_sale,
    product,
    stocked_product,
):
    sale = complete_sale(sale=paid_sale)

    sale.refresh_from_db()
    stocked_product.refresh_from_db()

    item = sale.items.get()

    balance = InventoryBalance.objects.get(product=product)

    assert sale.status == Sale.Status.COMPLETED
    assert sale.completed_at is not None
    assert sale.receipt_number.startswith("TE-")

    assert sale.total_amount == Decimal("500.00")
    assert sale.total_cost == Decimal("200.00")
    assert sale.gross_profit == Decimal("300.00")

    assert item.total_cost == Decimal("200.00")

    assert stocked_product.remaining_quantity == Decimal("22.000")
    assert balance.quantity_on_hand == Decimal("22.000")

    movement = StockMovement.objects.get(
        product=product,
        movement_type=StockMovement.MovementType.SALE,
    )

    assert movement.quantity == Decimal("2.000")
    assert movement.unit_cost == Decimal("100.000000")
    assert movement.reference == sale.receipt_number


def test_complete_carton_sale_deducts_base_units(
    product,
    carton,
    supplier,
    cashier,
):
    purchase = create_purchase(
        supplier=supplier,
        created_by=cashier,
        transport_cost=Decimal("0.00"),
    )

    add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=carton,
        package_quantity=2,
        purchase_unit_cost=Decimal("1200.00"),
    )

    receive_purchase(purchase=purchase)

    sale = create_sale(processed_by=cashier)

    item = add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=2,
        packaging=carton,
    )

    add_sale_payment(
        sale=sale,
        payment_method=SalePayment.PaymentMethod.MPESA,
        amount=Decimal("6000.00"),
        received_by=cashier,
        reference="MPESA123456",
    )

    completed_sale = complete_sale(sale=sale)

    item.refresh_from_db()

    balance = InventoryBalance.objects.get(product=product)

    assert completed_sale.status == Sale.Status.COMPLETED

    # Two cartons x twelve bottles = twenty-four bottles.
    assert item.base_quantity == 24
    assert item.total_cost == Decimal("2400.00")
    assert balance.quantity_on_hand == Decimal("0.000")


def test_completion_rejects_underpaid_sale(paid_sale, product):
    payment = paid_sale.payments.get()
    payment.amount = Decimal("400.00")
    payment.save()

    with pytest.raises(ValidationError):
        complete_sale(sale=paid_sale)

    paid_sale.refresh_from_db()

    assert paid_sale.status == Sale.Status.DRAFT
    assert paid_sale.receipt_number is None
    assert StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.SALE,
    ).count() == 0


def test_completion_rejects_sale_without_items(cashier):
    sale = create_sale(processed_by=cashier)

    with pytest.raises(ValidationError):
        complete_sale(sale=sale)

    sale.refresh_from_db()

    assert sale.status == Sale.Status.DRAFT
    assert sale.receipt_number is None


def test_completion_rejects_insufficient_stock(
    product,
    cashier,
):
    sale = create_sale(processed_by=cashier)

    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=1,
    )

    add_sale_payment(
        sale=sale,
        payment_method=SalePayment.PaymentMethod.CASH,
        amount=Decimal("250.00"),
        received_by=cashier,
    )

    with pytest.raises(ValidationError):
        complete_sale(sale=sale)

    sale.refresh_from_db()

    assert sale.status == Sale.Status.DRAFT
    assert sale.receipt_number is None
    assert sale.total_cost == Decimal("0.00")


def test_completed_sale_cannot_be_completed_twice(paid_sale):
    complete_sale(sale=paid_sale)

    with pytest.raises(ValidationError):
        complete_sale(sale=paid_sale)

    assert StockMovement.objects.filter(
        movement_type=StockMovement.MovementType.SALE,
    ).count() == 1


def test_failed_completion_rolls_back_previous_product_deductions(
    product,
    carton,
    supplier,
    cashier,
):
    # Prepare stock for the first product only.
    purchase = create_purchase(
        supplier=supplier,
        created_by=cashier,
        transport_cost=Decimal("0.00"),
    )

    add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=carton,
        package_quantity=1,
        purchase_unit_cost=Decimal("1200.00"),
    )

    batches = receive_purchase(purchase=purchase)
    first_batch = batches[0]

    # Create a second product without receiving any stock.
    category = Category.objects.create(name="Completion Drinks")
    family = ProductFamily.objects.create(name="Completion Juice")

    second_product = create_product(
        name="Orange Juice 500ml",
        product_family=family,
        category=category,
        size_value=500,
        size_unit="ML",
        base_unit="bottle",
        retail_price=100,
        wholesale_price=90,
    )

    sale = create_sale(processed_by=cashier)

    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=1,
    )

    add_sale_item(
        sale=sale,
        product=second_product,
        pricing_type="RETAIL",
        quantity=1,
    )

    add_sale_payment(
        sale=sale,
        payment_method=SalePayment.PaymentMethod.CASH,
        amount=Decimal("350.00"),
        received_by=cashier,
    )

    # The first product has stock; the second does not.
    # Completion must roll back the first product's deduction.
    with pytest.raises(ValidationError):
        complete_sale(sale=sale)

    sale.refresh_from_db()
    first_batch.refresh_from_db()

    first_balance = InventoryBalance.objects.get(product=product)

    assert sale.status == Sale.Status.DRAFT
    assert sale.receipt_number is None
    assert sale.total_cost == Decimal("0.00")

    assert first_batch.remaining_quantity == Decimal("12.000")
    assert first_balance.quantity_on_hand == Decimal("12.000")

    assert not StockMovement.objects.filter(
        movement_type=StockMovement.MovementType.SALE,
    ).exists()

    assert all(
        item.total_cost == Decimal("0.00")
        for item in sale.items.all()
    )
