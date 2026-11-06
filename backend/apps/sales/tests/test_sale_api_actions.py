
from decimal import Decimal

import pytest

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.inventory.models import (
    InventoryBalance,
    ProductPackaging,
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
from apps.suppliers.models import Supplier


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="sales_action_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def another_cashier(db):
    return User.objects.create_user(
        username="another_action_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def product(db):
    category = Category.objects.create(name="Sales Action Groceries")
    family = ProductFamily.objects.create(name="Sales Action Oil")

    return create_product(
        name="Cooking Oil 1L",
        product_family=family,
        category=category,
        size_value=1000,
        size_unit="ML",
        base_unit="bottle",
        retail_price="250.00",
        wholesale_price="230.00",
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
def supplier(db):
    return Supplier.objects.create(
        name="Sales Action Distributor",
        phone="0712345678",
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

    return receive_purchase(purchase=purchase)[0]


# ADD ITEM API TESTS

@pytest.mark.django_db
def test_cashier_can_add_retail_item(
    api_client,
    cashier,
    product,
):
    sale = create_sale(processed_by=cashier)
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-add-item", args=[sale.pk]),
        {
            "product": product.pk,
            "pricing_type": "RETAIL",
            "quantity": 2,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_amount"] == "500.00"
    assert len(response.data["items"]) == 1
    assert response.data["items"][0]["total_amount"] == "500.00"

    sale.refresh_from_db()
    assert sale.total_amount == Decimal("500.00")


@pytest.mark.django_db
def test_cashier_can_add_wholesale_carton(
    api_client,
    cashier,
    product,
    carton,
):
    sale = create_sale(processed_by=cashier)
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-add-item", args=[sale.pk]),
        {
            "product": product.pk,
            "pricing_type": "WHOLESALE",
            "quantity": 2,
            "packaging": carton.pk,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_amount"] == "5520.00"

    item = response.data["items"][0]
    assert item["base_quantity"] == 24
    assert item["conversion_factor_snapshot"] == 12


@pytest.mark.django_db
def test_add_item_rejects_zero_quantity(
    api_client,
    cashier,
    product,
):
    sale = create_sale(processed_by=cashier)
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-add-item", args=[sale.pk]),
        {
            "product": product.pk,
            "pricing_type": "RETAIL",
            "quantity": 0,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    sale.refresh_from_db()
    assert sale.items.count() == 0
    assert sale.total_amount == Decimal("0.00")


@pytest.mark.django_db
def test_cashier_cannot_add_item_to_another_cashiers_sale(
    api_client,
    cashier,
    another_cashier,
    product,
):
    other_sale = create_sale(processed_by=another_cashier)
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-add-item", args=[other_sale.pk]),
        {
            "product": product.pk,
            "pricing_type": "RETAIL",
            "quantity": 1,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert other_sale.items.count() == 0


# ADD PAYMENT API TESTS

@pytest.mark.django_db
def test_cashier_can_add_cash_payment(
    api_client,
    cashier,
    product,
):
    sale = create_sale(processed_by=cashier)
    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=2,
    )

    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-add-payment", args=[sale.pk]),
        {
            "payment_method": "CASH",
            "amount": "500.00",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["payments"]) == 1
    assert response.data["payments"][0]["payment_method"] == "CASH"
    assert response.data["payments"][0]["amount"] == "500.00"

    assert SalePayment.objects.filter(
        sale=sale,
        payment_method="CASH",
        amount=Decimal("500.00"),
    ).exists()


@pytest.mark.django_db
def test_cashier_can_add_mpesa_payment_with_reference(
    api_client,
    cashier,
    product,
):
    sale = create_sale(processed_by=cashier)
    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=1,
    )

    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-add-payment", args=[sale.pk]),
        {
            "payment_method": "MPESA",
            "amount": "250.00",
            "reference": "MPESA123456",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    payment = SalePayment.objects.get(sale=sale)

    assert payment.payment_method == "MPESA"
    assert payment.reference == "MPESA123456"


@pytest.mark.django_db
def test_mpesa_payment_requires_reference(
    api_client,
    cashier,
    product,
):
    sale = create_sale(processed_by=cashier)
    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=1,
    )

    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-add-payment", args=[sale.pk]),
        {
            "payment_method": "MPESA",
            "amount": "250.00",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert SalePayment.objects.filter(sale=sale).count() == 0


@pytest.mark.django_db
def test_payment_cannot_exceed_sale_balance(
    api_client,
    cashier,
    product,
):
    sale = create_sale(processed_by=cashier)
    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=1,
    )

    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-add-payment", args=[sale.pk]),
        {
            "payment_method": "CASH",
            "amount": "300.00",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert SalePayment.objects.filter(sale=sale).count() == 0


# SALE COMPLETION API TESTS

@pytest.mark.django_db
def test_cashier_can_complete_fully_paid_sale(
    api_client,
    cashier,
    product,
    stocked_product,
):
    sale = create_sale(processed_by=cashier)

    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=2,
    )

    sale.payments.create(
        payment_method=SalePayment.PaymentMethod.CASH,
        amount=Decimal("500.00"),
        received_by=cashier,
    )

    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-complete", args=[sale.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == Sale.Status.COMPLETED
    assert response.data["receipt_number"].startswith("TE-")

    sale.refresh_from_db()
    stocked_product.refresh_from_db()

    assert sale.status == Sale.Status.COMPLETED
    assert sale.completed_at is not None
    assert sale.total_cost == Decimal("200.00")
    assert sale.gross_profit == Decimal("300.00")

    assert stocked_product.remaining_quantity == Decimal("22.000")

    balance = InventoryBalance.objects.get(product=product)
    assert balance.quantity_on_hand == Decimal("22.000")

    assert StockMovement.objects.filter(
        product=product,
        movement_type=StockMovement.MovementType.SALE,
    ).count() == 1


@pytest.mark.django_db
def test_cannot_complete_unpaid_sale(
    api_client,
    cashier,
    product,
    stocked_product,
):
    sale = create_sale(processed_by=cashier)

    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=1,
    )

    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-complete", args=[sale.pk])
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    sale.refresh_from_db()

    assert sale.status == Sale.Status.DRAFT
    assert sale.receipt_number is None
    assert StockMovement.objects.filter(
        movement_type=StockMovement.MovementType.SALE,
    ).count() == 0
