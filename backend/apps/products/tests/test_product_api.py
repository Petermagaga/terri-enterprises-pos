
import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.products.models import Category, Product, ProductFamily
from apps.products.services.product_creation import create_product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        username="pos_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="pos_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def product_data(db):
    family = ProductFamily.objects.create(name="Margarine")
    category = Category.objects.create(name="Spreads")

    return {
        "name": "Margarine 500g",
        "product_family": family.pk,
        "category": category.pk,
        "brand": "Test Brand",
        "size_value": "500",
        "size_unit": "G",
        "base_unit": "piece",
        "retail_price": "75.00",
        "wholesale_price": "68.00",
        "reorder_level": 10,
    }


@pytest.fixture
def existing_product(product_data):
    family = ProductFamily.objects.get(pk=product_data["product_family"])
    category = Category.objects.get(pk=product_data["category"])

    return create_product(
        name=product_data["name"],
        product_family=family,
        category=category,
        size_value=product_data["size_value"],
        size_unit=product_data["size_unit"],
        base_unit=product_data["base_unit"],
        retail_price=product_data["retail_price"],
        wholesale_price=product_data["wholesale_price"],
        brand=product_data["brand"],
        reorder_level=product_data["reorder_level"],
    )


@pytest.mark.django_db
def test_owner_can_create_product_and_sku_is_generated(
    api_client, owner, product_data
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("product-list"),
        product_data,
        format="json",
    )
    print("API response:", response.data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["sku"] == "MARG-500G"
    assert Product.objects.filter(sku="MARG-500G").exists()


@pytest.mark.django_db
def test_client_cannot_override_product_sku(
    api_client, owner, product_data
):
    api_client.force_authenticate(user=owner)
    product_data["sku"] = "FAKE-999G"

    response = api_client.post(
        reverse("product-list"),
        product_data,
        format="json",
    )
    print("API response:", response.data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["sku"] == "MARG-500G"
    assert not Product.objects.filter(sku="FAKE-999G").exists()


@pytest.mark.django_db
def test_cashier_can_view_product_catalogue(
    api_client, cashier, existing_product
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(reverse("product-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == existing_product.pk


@pytest.mark.django_db
def test_cashier_cannot_create_product(
    api_client, cashier, product_data
):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("product-list"),
        product_data,
        format="json",
    )
    print("API response:", response.data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Product.objects.count() == 0


@pytest.mark.django_db
def test_cashier_cannot_update_product(
    api_client, cashier, existing_product
):
    api_client.force_authenticate(user=cashier)

    response = api_client.patch(
        reverse("product-detail", args=[existing_product.pk]),
        {"retail_price": "90.00"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    existing_product.refresh_from_db()
    assert str(existing_product.retail_price) == "75.00"


@pytest.mark.django_db
def test_owner_can_update_product_without_changing_sku(
    api_client, owner, existing_product
):
    original_sku = existing_product.sku
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse("product-detail", args=[existing_product.pk]),
        {"retail_price": "80.00"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["sku"] == original_sku

    existing_product.refresh_from_db()
    assert str(existing_product.retail_price) == "80.00"
    assert existing_product.sku == original_sku


@pytest.mark.django_db
def test_product_cannot_be_permanently_deleted(
    api_client, owner, existing_product
):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(
        reverse("product-detail", args=[existing_product.pk])
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert Product.objects.filter(pk=existing_product.pk).exists()
