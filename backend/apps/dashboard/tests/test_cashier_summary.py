from decimal import Decimal

import pytest

from apps.accounts.models import User
from apps.dashboard.services.cashier_summary import (
    get_cashier_dashboard_summary,
)
from apps.inventory.models import ProductPackaging
from apps.inventory.services.purchase_creation import (
    create_purchase,
    add_purchase_item,
)
from apps.inventory.services.purchase_receiving import receive_purchase
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.sales.models import SalePayment
from apps.sales.services.sale_creation import create_sale, add_sale_item
from apps.sales.services.payment_creation import add_sale_payment
from apps.sales.services.sale_completion import complete_sale
from apps.suppliers.models import Supplier


pytestmark = pytest.mark.django_db


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="dashboard_cashier",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def other_cashier():
    return User.objects.create_user(
        username="dashboard_other_cashier",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def supplier():
    return Supplier.objects.create(
        name="Dashboard Distributors",
        phone="0712345678",
    )


@pytest.fixture
def product():
    category = Category.objects.create(name="Dashboard Groceries")
    family = ProductFamily.objects.create(name="Dashboard Cooking Oil")

    return create_product(
        name="Dashboard Cooking Oil 1L",
        product_family=family,
        category=category,
        size_value=1000,
        size_unit="ML",
        base_unit="bottle",
        retail_price=250,
        wholesale_price=230,
    )


@pytest.fixture
def stocked_product(product, cashier, supplier):
    carton = ProductPackaging.objects.create(
        product=product,
        name="Carton",
        conversion_factor=12,
        purchase_enabled=True,
        sales_enabled=True,
    )

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

    return receive_purchase(purchase=purchase)





def test_cashier_dashboard_only_includes_own_sales_and_collections(
    cashier,
    other_cashier,
    product,
    stocked_product,
):
    # Attach the product to the sale helper for this test.
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

    completed_sale = complete_sale(sale=sale)

    other_sale = create_sale(processed_by=other_cashier)

    add_sale_item(
        sale=other_sale,
        product=product,
        pricing_type="RETAIL",
        quantity=2,
    )

    add_sale_payment(
        sale=other_sale,
        payment_method=SalePayment.PaymentMethod.MPESA,
        amount=Decimal("500.00"),
        received_by=other_cashier,
        reference="MPESA123",
    )

    complete_sale(sale=other_sale)

    summary = get_cashier_dashboard_summary(cashier)

    assert summary["sales_summary"]["sale_count"] == 1
    assert summary["sales_summary"]["revenue"] == Decimal("500.00")

    assert summary["payment_summary"]["cash"]["total_amount"] == Decimal("500.00")
    assert summary["payment_summary"]["mpesa"]["total_amount"] == Decimal("0.00")
    assert summary["payment_summary"]["total_collections"] == Decimal("500.00")

    assert len(summary["recent_sales"]) == 1
    assert summary["recent_sales"][0]["id"] == completed_sale.id

    assert "total_cost" not in summary
    assert "gross_profit" not in summary