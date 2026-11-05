import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from apps.accounts.models import User
from apps.inventory.models import (
    InventoryBalance,
    ProductPackaging,
    Purchase,
    PurchaseItem,
    StockBatch,
    StockMovement,
)

from apps.inventory.services.purchase_creation import (
    add_purchase_item,
    create_purchase,
)
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.inventory.services.purchase_creation import create_purchase
from apps.suppliers.models import Supplier


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        username="purchase_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="purchase_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def supplier(db):
    return Supplier.objects.create(
        name="Test Distributor",
        phone="0712345678",
    )


@pytest.fixture
def purchase(owner, supplier):
    return create_purchase(
        supplier=supplier,
        created_by=owner,
        supplier_reference="INV-001",
        transport_cost="200.00",
    )


@pytest.fixture
def product(db):
    category = Category.objects.create(name="Groceries")
    family = ProductFamily.objects.create(name="Cooking Oil")

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
def packaging(product):
    return ProductPackaging.objects.create(
        product=product,
        name="Carton",
        conversion_factor=12,
        purchase_enabled=True,
        sales_enabled=True,
    )


@pytest.fixture
def purchase_with_item(purchase, product, packaging):
    add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity="2.000",
        purchase_unit_cost="2400.00",
    )

    return purchase

@pytest.fixture
def purchase_data(supplier):
    return {
        "supplier": supplier.pk,
        "supplier_reference": "INV-002",
        "transport_cost": "150.00",
    }

# AUTHENTICATION TESTS

@pytest.mark.django_db
def test_unauthenticated_user_cannot_view_purchases(api_client):
    response = api_client.get(
        reverse("inventory-purchase-list")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_purchase(
    api_client, purchase_data
):
    response = api_client.post(
        reverse("inventory-purchase-list"),
        purchase_data,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Purchase.objects.count() == 0

# CASHIER PERMISSION TESTS

@pytest.mark.django_db
def test_cashier_cannot_view_purchases(
    api_client, cashier, purchase
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("inventory-purchase-list")
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_cashier_cannot_create_purchase(
    api_client, cashier, purchase_data
):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("inventory-purchase-list"),
        purchase_data,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Purchase.objects.count() == 0


@pytest.mark.django_db
def test_cashier_cannot_update_purchase(
    api_client, cashier, purchase
):
    api_client.force_authenticate(user=cashier)

    response = api_client.patch(
        reverse(
            "inventory-purchase-detail",
            args=[purchase.pk],
        ),
        {"supplier_reference": "CHANGED-001"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    purchase.refresh_from_db()
    assert purchase.supplier_reference == "INV-001"


# OWNER API TESTS

@pytest.mark.django_db
def test_owner_can_view_purchases(
    api_client, owner, purchase
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("inventory-purchase-list")
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["supplier_name"] == "Test Distributor"


@pytest.mark.django_db
def test_owner_can_retrieve_purchase(
    api_client, owner, purchase
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse(
            "inventory-purchase-detail",
            args=[purchase.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["supplier_reference"] == "INV-001"
    assert response.data["transport_cost"] == "200.00"


@pytest.mark.django_db
def test_owner_can_create_purchase(
    api_client, owner, purchase_data
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("inventory-purchase-list"),
        purchase_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["supplier_reference"] == "INV-002"
    assert response.data["status"] == Purchase.Status.DRAFT
    assert Purchase.objects.count() == 1

    created_purchase = Purchase.objects.get()
    assert created_purchase.created_by == owner


@pytest.mark.django_db
def test_owner_can_update_draft_purchase(
    api_client, owner, purchase
):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse(
            "inventory-purchase-detail",
            args=[purchase.pk],
        ),
        {"supplier_reference": "UPDATED-001"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    purchase.refresh_from_db()
    assert purchase.supplier_reference == "UPDATED-001"


# VALIDATION TESTS

@pytest.mark.django_db
def test_purchase_requires_an_active_supplier(
    api_client, owner, supplier
):
    supplier.is_active = False
    supplier.save()

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("inventory-purchase-list"),
        {
            "supplier": supplier.pk,
            "supplier_reference": "INV-003",
            "transport_cost": "100.00",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Purchase.objects.count() == 0


@pytest.mark.django_db
def test_purchase_transport_cost_cannot_be_negative(
    api_client, owner, purchase_data
):
    api_client.force_authenticate(user=owner)
    purchase_data["transport_cost"] = "-50.00"

    response = api_client.post(
        reverse("inventory-purchase-list"),
        purchase_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Purchase.objects.count() == 0


@pytest.mark.django_db
def test_purchase_requires_a_valid_supplier(
    api_client, owner, purchase_data
):
    api_client.force_authenticate(user=owner)
    purchase_data["supplier"] = 999999

    response = api_client.post(
        reverse("inventory-purchase-list"),
        purchase_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Purchase.objects.count() == 0

# DATA PROTECTION TESTS

@pytest.mark.django_db
def test_client_cannot_override_purchase_id(
    api_client, owner, purchase_data
):
    api_client.force_authenticate(user=owner)
    purchase_data["id"] = 9999

    response = api_client.post(
        reverse("inventory-purchase-list"),
        purchase_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["id"] != 9999


@pytest.mark.django_db
def test_client_cannot_override_purchase_status(
    api_client, owner, purchase_data
):
    api_client.force_authenticate(user=owner)
    purchase_data["status"] = Purchase.Status.RECEIVED

    response = api_client.post(
        reverse("inventory-purchase-list"),
        purchase_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == Purchase.Status.DRAFT


@pytest.mark.django_db
def test_received_purchase_cannot_be_updated(
    api_client, owner, purchase
):
    purchase.status = Purchase.Status.RECEIVED
    purchase.save(update_fields=["status"])

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse(
            "inventory-purchase-detail",
            args=[purchase.pk],
        ),
        {"supplier_reference": "CHANGED-AFTER-RECEIVING"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    purchase.refresh_from_db()
    assert purchase.supplier_reference == "INV-001"


@pytest.mark.django_db
def test_purchase_cannot_be_permanently_deleted(
    api_client, owner, purchase
):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(
        reverse(
            "inventory-purchase-detail",
            args=[purchase.pk],
        )
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert Purchase.objects.filter(pk=purchase.pk).exists()


# PURCHASE RECEIVING API TESTS

@pytest.mark.django_db
def test_owner_can_receive_purchase(
    api_client, owner, purchase_with_item, product
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse(
            "inventory-purchase-receive",
            args=[purchase_with_item.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == Purchase.Status.RECEIVED
    assert response.data["received_at"] is not None

    purchase_with_item.refresh_from_db()
    assert purchase_with_item.status == Purchase.Status.RECEIVED

    batch = StockBatch.objects.get(
        purchase_item__purchase=purchase_with_item
    )

    assert batch.product == product
    assert batch.received_quantity == 24
    assert batch.remaining_quantity == 24

    movement = StockMovement.objects.get(
        stock_batch=batch
    )

    assert movement.movement_type == (
        StockMovement.MovementType.PURCHASE_RECEIPT
    )
    assert movement.direction == StockMovement.Direction.IN
    assert movement.quantity == 24

    balance = InventoryBalance.objects.get(product=product)
    assert balance.quantity_on_hand == 24


@pytest.mark.django_db
def test_cashier_cannot_receive_purchase(
    api_client, cashier, purchase_with_item
):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse(
            "inventory-purchase-receive",
            args=[purchase_with_item.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    purchase_with_item.refresh_from_db()
    assert purchase_with_item.status == Purchase.Status.DRAFT

    assert StockBatch.objects.count() == 0
    assert StockMovement.objects.count() == 0


@pytest.mark.django_db
def test_unauthenticated_user_cannot_receive_purchase(
    api_client, purchase_with_item
):
    response = api_client.post(
        reverse(
            "inventory-purchase-receive",
            args=[purchase_with_item.pk],
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    purchase_with_item.refresh_from_db()
    assert purchase_with_item.status == Purchase.Status.DRAFT


@pytest.mark.django_db
def test_receiving_purchase_without_items_returns_validation_error(
    api_client, owner, purchase
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse(
            "inventory-purchase-receive",
            args=[purchase.pk],
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Purchase.objects.get(pk=purchase.pk).status == (
        Purchase.Status.DRAFT
    )

    assert StockBatch.objects.count() == 0
    assert StockMovement.objects.count() == 0
    