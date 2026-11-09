import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.inventory.models import ProductPackaging
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product

from apps.inventory.services.purchase_creation import (
    add_purchase_item,
    create_purchase,
)
from apps.suppliers.models import Supplier

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        username="inventory_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="inventory_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def product(db):
    family = ProductFamily.objects.create(name="Water")
    category = Category.objects.create(name="Drinks")

    return create_product(
        name="Mineral Water 500ml",
        product_family=family,
        category=category,
        size_value="500",
        size_unit="ML",
        base_unit="bottle",
        retail_price="50.00",
        wholesale_price="45.00",
        reorder_level=10,
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
def packaging_data(product):
    return {
        "product": product.pk,
        "name": "Pack of 6",
        "conversion_factor": 6,
        "purchase_enabled": True,
        "sales_enabled": True,
    }


# AUTHENTICATION TESTS

@pytest.mark.django_db
def test_unauthenticated_user_cannot_view_packaging(api_client):
    response = api_client.get(
        reverse("inventory-packaging-list")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_packaging(
    api_client, packaging_data
):
    response = api_client.post(
        reverse("inventory-packaging-list"),
        packaging_data,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert ProductPackaging.objects.count() == 0


# CASHIER PERMISSION TESTS

# CASHIER PERMISSION TESTS

@pytest.mark.django_db
def test_cashier_can_view_packaging(
    api_client, cashier, packaging
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("inventory-packaging-list")
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "Carton"


@pytest.mark.django_db
def test_cashier_can_retrieve_packaging(
    api_client, cashier, packaging
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse(
            "inventory-packaging-detail",
            args=[packaging.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Carton"
    assert response.data["conversion_factor"] == 12


@pytest.mark.django_db
def test_cashier_cannot_create_packaging(
    api_client, cashier, packaging_data
):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("inventory-packaging-list"),
        packaging_data,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert ProductPackaging.objects.count() == 0


@pytest.mark.django_db
def test_cashier_cannot_update_packaging(
    api_client, cashier, packaging
):
    api_client.force_authenticate(user=cashier)

    response = api_client.patch(
        reverse(
            "inventory-packaging-detail",
            args=[packaging.pk],
        ),
        {"name": "Changed Carton"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    packaging.refresh_from_db()
    assert packaging.name == "Carton"


# OWNER API TESTS

@pytest.mark.django_db
def test_owner_can_view_packaging(
    api_client, owner, packaging
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("inventory-packaging-list")
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "Carton"


@pytest.mark.django_db
def test_owner_can_retrieve_packaging(
    api_client, owner, packaging
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse(
            "inventory-packaging-detail",
            args=[packaging.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["conversion_factor"] == 12


@pytest.mark.django_db
def test_owner_can_create_packaging(
    api_client, owner, packaging_data
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("inventory-packaging-list"),
        packaging_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert ProductPackaging.objects.filter(
        name="Pack of 6",
        conversion_factor=6,
    ).exists()


@pytest.mark.django_db
def test_owner_can_update_packaging(
    api_client, owner, packaging
):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse(
            "inventory-packaging-detail",
            args=[packaging.pk],
        ),
        {"name": "Large Carton"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    packaging.refresh_from_db()
    assert packaging.name == "Large Carton"


@pytest.mark.django_db
def test_owner_can_deactivate_packaging(
    api_client, owner, packaging
):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse(
            "inventory-packaging-detail",
            args=[packaging.pk],
        ),
        {"is_active": False},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    packaging.refresh_from_db()
    assert packaging.is_active is False


# VALIDATION TESTS

@pytest.mark.django_db
def test_packaging_conversion_factor_must_be_positive(
    api_client, owner, packaging_data
):
    api_client.force_authenticate(user=owner)
    packaging_data["conversion_factor"] = 0

    response = api_client.post(
        reverse("inventory-packaging-list"),
        packaging_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ProductPackaging.objects.count() == 0


@pytest.mark.django_db
def test_packaging_name_cannot_be_blank(
    api_client, owner, packaging_data
):
    api_client.force_authenticate(user=owner)
    packaging_data["name"] = " "

    response = api_client.post(
        reverse("inventory-packaging-list"),
        packaging_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ProductPackaging.objects.count() == 0


@pytest.mark.django_db
def test_packaging_must_support_purchase_or_sales(
    api_client, owner, packaging_data
):
    api_client.force_authenticate(user=owner)

    packaging_data["purchase_enabled"] = False
    packaging_data["sales_enabled"] = False

    response = api_client.post(
        reverse("inventory-packaging-list"),
        packaging_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert ProductPackaging.objects.count() == 0


# DATA PROTECTION TESTS

@pytest.mark.django_db
def test_client_cannot_override_packaging_id(
    api_client, owner, packaging_data
):
    api_client.force_authenticate(user=owner)
    packaging_data["id"] = 9999

    response = api_client.post(
        reverse("inventory-packaging-list"),
        packaging_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["id"] != 9999


@pytest.mark.django_db
def test_packaging_cannot_be_permanently_deleted(
    api_client, owner, packaging
):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(
        reverse(
            "inventory-packaging-detail",
            args=[packaging.pk],
        )
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert ProductPackaging.objects.filter(pk=packaging.pk).exists()


@pytest.mark.django_db
def test_used_packaging_conversion_factor_cannot_be_changed(
    api_client, owner, product, packaging
):
    supplier = Supplier.objects.create(
        name="Test Supplier",
        phone="0712345678",
    )

    purchase = create_purchase(
        supplier=supplier,
        created_by=owner,
    )

    add_purchase_item(
        purchase=purchase,
        product=product,
        packaging=packaging,
        package_quantity="2",
        purchase_unit_cost="500.00",
    )

    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse(
            "inventory-packaging-detail",
            args=[packaging.pk],
        ),
        {"conversion_factor": 24},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    packaging.refresh_from_db()
    assert packaging.conversion_factor == 12

@pytest.mark.django_db
def test_packaging_list_can_be_filtered_by_product(
    api_client, cashier, product, packaging
):
    another_product = create_product(
        name="Mineral Water 1L",
        product_family=product.product_family,
        category=product.category,
        size_value="1",
        size_unit="L",
        base_unit="bottle",
        retail_price="80.00",
        wholesale_price="70.00",
        reorder_level=10,
    )

    ProductPackaging.objects.create(
        product=another_product,
        name="Carton",
        conversion_factor=12,
        purchase_enabled=True,
        sales_enabled=True,
    )

    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("inventory-packaging-list"),
        {"product": product.pk},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["product"] == product.pk
    assert response.data["results"][0]["name"] == packaging.name