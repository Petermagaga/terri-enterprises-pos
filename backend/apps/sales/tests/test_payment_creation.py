import pytest

from decimal import Decimal
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.inventory.models import ProductPackaging
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.sales.models import Sale, SalePayment
from apps.sales.services.sale_creation import create_sale, add_sale_item
from apps.sales.services.payment_creation import add_sale_payment


pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    return User.objects.create_superuser(
        username="owner_payment",
        email="owner_payment@test.com",
        password="TestPassword123!",
    )


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="cashier_payment",
        email="cashier_payment@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def product():
    category = Category.objects.create(name="Groceries")
    family = ProductFamily.objects.create(name="Margarine")

    return create_product(
        name="Margarine 500g",
        product_family=family,
        category=category,
        size_value=500,
        size_unit="G",
        base_unit="tub",
        retail_price=250,
        wholesale_price=230,
    )


@pytest.fixture
def sale(product, cashier):
    sale = create_sale(processed_by=cashier)

    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=2,
    )

    return sale


def test_cash_payment(sale, cashier):
    payment = add_sale_payment(
        sale=sale,
        payment_method=SalePayment.PaymentMethod.CASH,
        amount="500.00",
        received_by=cashier,
    )

    assert payment.amount == Decimal("500.00")
    assert payment.payment_method == SalePayment.PaymentMethod.CASH
    assert payment.reference == ""
    assert payment.received_by == cashier


def test_mpesa_payment_requires_reference(sale, cashier):
    payment = add_sale_payment(
        sale=sale,
        payment_method=SalePayment.PaymentMethod.MPESA,
        amount="500.00",
        received_by=cashier,
        reference="QWE123456",
    )

    assert payment.reference == "QWE123456"
    assert payment.payment_method == SalePayment.PaymentMethod.MPESA


def test_split_payment_is_allowed(sale, cashier):
    add_sale_payment(
        sale=sale,
        payment_method=SalePayment.PaymentMethod.CASH,
        amount="200.00",
        received_by=cashier,
    )

    add_sale_payment(
        sale=sale,
        payment_method=SalePayment.PaymentMethod.MPESA,
        amount="300.00",
        received_by=cashier,
        reference="QWE123456",
    )

    total_paid = sum(
        payment.amount for payment in sale.payments.all()
    )

    assert total_paid == Decimal("500.00")
    assert sale.payments.count() == 2


def test_payment_cannot_exceed_sale_total(sale, cashier):
    with pytest.raises(ValidationError):
        add_sale_payment(
            sale=sale,
            payment_method=SalePayment.PaymentMethod.CASH,
            amount="501.00",
            received_by=cashier,
        )

    assert sale.payments.count() == 0


def test_multiple_payments_cannot_exceed_sale_total(sale, cashier):
    add_sale_payment(
        sale=sale,
        payment_method=SalePayment.PaymentMethod.CASH,
        amount="300.00",
        received_by=cashier,
    )

    with pytest.raises(ValidationError):
        add_sale_payment(
            sale=sale,
            payment_method=SalePayment.PaymentMethod.CASH,
            amount="300.00",
            received_by=cashier,
        )

    assert sale.payments.count() == 1


def test_payment_rejects_empty_sale(cashier):
    empty_sale = create_sale(processed_by=cashier)

    with pytest.raises(ValidationError):
        add_sale_payment(
            sale=empty_sale,
            payment_method=SalePayment.PaymentMethod.CASH,
            amount="100.00",
            received_by=cashier,
        )


def test_payment_rejects_inactive_user(sale, cashier):
    cashier.is_active = False
    cashier.save()

    with pytest.raises(ValidationError):
        add_sale_payment(
            sale=sale,
            payment_method=SalePayment.PaymentMethod.CASH,
            amount="100.00",
            received_by=cashier,
        )


def test_payment_rejects_invalid_payment_method(sale, cashier):
    with pytest.raises(ValidationError):
        add_sale_payment(
            sale=sale,
            payment_method="CARD",
            amount="100.00",
            received_by=cashier,
        )


def test_payment_rejects_zero_amount(sale, cashier):
    with pytest.raises(ValidationError):
        add_sale_payment(
            sale=sale,
            payment_method=SalePayment.PaymentMethod.CASH,
            amount="0.00",
            received_by=cashier,
        )


def test_payment_rejects_negative_amount(sale, cashier):
    with pytest.raises(ValidationError):
        add_sale_payment(
            sale=sale,
            payment_method=SalePayment.PaymentMethod.CASH,
            amount="-10.00",
            received_by=cashier,
        )


def test_payment_rejects_mpesa_without_reference(sale, cashier):
    with pytest.raises(ValidationError):
        add_sale_payment(
            sale=sale,
            payment_method=SalePayment.PaymentMethod.MPESA,
            amount="100.00",
            received_by=cashier,
        )


def test_cash_payment_rejects_reference(sale, cashier):
    with pytest.raises(ValidationError):
        add_sale_payment(
            sale=sale,
            payment_method=SalePayment.PaymentMethod.CASH,
            amount="100.00",
            received_by=cashier,
            reference="QWE123456",
        )


def test_payment_rejects_completed_sale(sale, cashier):
    sale.status = Sale.Status.COMPLETED
    sale.save()

    with pytest.raises(ValidationError):
        add_sale_payment(
            sale=sale,
            payment_method=SalePayment.PaymentMethod.CASH,
            amount="100.00",
            received_by=cashier,
        )