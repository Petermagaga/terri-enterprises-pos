import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.inventory.models import (
    ProductPackaging,
    Purchase,
    PurchaseItem,
)
from apps.inventory.services.purchase_creation import create_purchase
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.suppliers.models import Supplier


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        username="purchase_item_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="purchase_item_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def supplier(db):
    return Supplier.objects.create(
        name="ABC Distributors",
        phone="0712345678",
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
def purchase(owner, supplier):
    return create_purchase(
        supplier=supplier,
        created_by=owner,
        supplier_reference="INV-001",
    )


@pytest.fixture
def purchase_item_data(purchase, product, packaging):
    return {
        "purchase": purchase.pk,
        "product": product.pk,
        "packaging": packaging.pk,
        "package_quantity": "2.000",
        "purchase_unit_cost": "2400.00",
    }

# AUTHENTICATION TESTS

@pytest.mark.django_db
def test_unauthenticated_user_cannot_view_purchase_items(api_client):
    response = api_client.get(
        reverse("inventory-purchase-item-list")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_purchase_item(
    api_client, purchase_item_data
):
    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert PurchaseItem.objects.count() == 0


# CASHIER PERMISSION TESTS

@pytest.mark.django_db
def test_cashier_cannot_view_purchase_items(
    api_client, cashier, purchase_item_data
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("inventory-purchase-item-list")
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_cashier_cannot_create_purchase_item(
    api_client, cashier, purchase_item_data
):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert PurchaseItem.objects.count() == 0

# OWNER API TESTS

@pytest.mark.django_db
def test_owner_can_view_purchase_items(
    api_client, owner, purchase_item_data
):
    api_client.force_authenticate(user=owner)

    create_response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert create_response.status_code == status.HTTP_201_CREATED

    response = api_client.get(
        reverse("inventory-purchase-item-list")
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["product_name"] == "Cooking Oil 1L"


@pytest.mark.django_db
def test_owner_can_retrieve_purchase_item(
    api_client, owner, purchase_item_data
):
    api_client.force_authenticate(user=owner)

    create_response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    item_id = create_response.data["id"]

    response = api_client.get(
        reverse(
            "inventory-purchase-item-detail",
            args=[item_id],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["packaging_name"] == "Carton"


@pytest.mark.django_db
def test_owner_can_create_purchase_item(
    api_client, owner, purchase_item_data
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert PurchaseItem.objects.count() == 1

    item = PurchaseItem.objects.get()

    assert item.package_quantity == 2
    assert item.purchase_unit_cost == 2400
    assert item.base_quantity == 24
    assert item.packaging_name_snapshot == "Carton"
    assert item.conversion_factor_snapshot == 12

# CALCULATION TESTS

@pytest.mark.django_db
def test_purchase_item_returns_correct_base_quantity(
    api_client, owner, purchase_item_data
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["base_quantity"] == "24.000"


@pytest.mark.django_db
def test_purchase_item_returns_correct_line_subtotal(
    api_client, owner, purchase_item_data
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["line_subtotal"] == "4800.00"


@pytest.mark.django_db
def test_purchase_item_exposes_packaging_snapshot(
    api_client, owner, purchase_item_data
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["packaging_name"] == "Carton"
    assert response.data["conversion_factor_snapshot"] == 12

# VALIDATION TESTS

@pytest.mark.django_db
def test_purchase_item_rejects_zero_package_quantity(
    api_client, owner, purchase_item_data
):
    api_client.force_authenticate(user=owner)
    purchase_item_data["package_quantity"] = "0"

    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert PurchaseItem.objects.count() == 0


@pytest.mark.django_db
def test_purchase_item_rejects_negative_purchase_cost(
    api_client, owner, purchase_item_data
):
    api_client.force_authenticate(user=owner)
    purchase_item_data["purchase_unit_cost"] = "-100.00"

    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert PurchaseItem.objects.count() == 0


@pytest.mark.django_db
def test_purchase_item_rejects_packaging_from_another_product(
    api_client, owner, purchase_item_data, product
):
    category = Category.objects.create(name="Beverages")
    family = ProductFamily.objects.create(name="Juice")

    another_product = create_product(
        name="Orange Juice 500ml",
        product_family=family,
        category=category,
        size_value=500,
        size_unit="ML",
        base_unit="bottle",
        retail_price="100.00",
        wholesale_price="90.00",
    )

    another_packaging = ProductPackaging.objects.create(
        product=another_product,
        name="Carton",
        conversion_factor=24,
    )

    api_client.force_authenticate(user=owner)

    purchase_item_data["packaging"] = another_packaging.pk

    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert PurchaseItem.objects.count() == 0


@pytest.mark.django_db
def test_purchase_item_rejects_inactive_product(
    api_client, owner, purchase_item_data, product
):
    product.is_active = False
    product.save()

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert PurchaseItem.objects.count() == 0


@pytest.mark.django_db
def test_purchase_item_rejects_received_purchase(
    api_client, owner, purchase_item_data, purchase
):
    purchase.status = Purchase.Status.RECEIVED
    purchase.save()

    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert PurchaseItem.objects.count() == 0

# DATA PROTECTION TESTS

@pytest.mark.django_db
def test_client_cannot_override_purchase_item_snapshots(
    api_client, owner, purchase_item_data
):
    api_client.force_authenticate(user=owner)

    purchase_item_data["packaging_name_snapshot"] = "Fake Pack"
    purchase_item_data["conversion_factor_snapshot"] = 99
    purchase_item_data["allocated_transport_cost"] = "999.00"

    response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    item = PurchaseItem.objects.get()

    assert item.packaging_name_snapshot == "Carton"
    assert item.conversion_factor_snapshot == 12
    assert item.allocated_transport_cost == 0


@pytest.mark.django_db
def test_purchase_item_cannot_be_updated(
    api_client, owner, purchase_item_data
):
    api_client.force_authenticate(user=owner)

    create_response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    item_id = create_response.data["id"]

    response = api_client.patch(
        reverse(
            "inventory-purchase-item-detail",
            args=[item_id],
        ),
        {"package_quantity": "5.000"},
        format="json",
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    item = PurchaseItem.objects.get(pk=item_id)
    assert item.package_quantity == 2


@pytest.mark.django_db
def test_purchase_item_cannot_be_deleted(
    api_client, owner, purchase_item_data
):
    api_client.force_authenticate(user=owner)

    create_response = api_client.post(
        reverse("inventory-purchase-item-list"),
        purchase_item_data,
        format="json",
    )

    item_id = create_response.data["id"]

    response = api_client.delete(
        reverse(
            "inventory-purchase-item-detail",
            args=[item_id],
        )
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert PurchaseItem.objects.filter(pk=item_id).exists()