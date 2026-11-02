
import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.products.models import Category, ProductFamily


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        username="category_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="category_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        name="Spreads",
        description="Butter and margarine products.",
    )


@pytest.fixture
def family(db):
    return ProductFamily.objects.create(name="Margarine")


# CATEGORY API TESTS

@pytest.mark.django_db
def test_owner_can_create_category(api_client, owner):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("category-list"),
        {
            "name": "Beverages",
            "description": "Drinks and beverages.",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Category.objects.filter(name="Beverages").exists()


@pytest.mark.django_db
def test_cashier_can_view_categories(api_client, cashier, category):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(reverse("category-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Spreads"


@pytest.mark.django_db
def test_cashier_cannot_create_category(api_client, cashier):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("category-list"),
        {"name": "Beverages"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Category.objects.filter(name="Beverages").exists()


@pytest.mark.django_db
def test_owner_can_update_category(api_client, owner, category):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse("category-detail", args=[category.pk]),
        {"name": "Dairy and Spreads"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    category.refresh_from_db()
    assert category.name == "Dairy and Spreads"


@pytest.mark.django_db
def test_cashier_cannot_update_category(api_client, cashier, category):
    api_client.force_authenticate(user=cashier)

    response = api_client.patch(
        reverse("category-detail", args=[category.pk]),
        {"name": "Changed Category"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    category.refresh_from_db()
    assert category.name == "Spreads"


@pytest.mark.django_db
def test_category_cannot_be_permanently_deleted(
    api_client, owner, category
):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(
        reverse("category-detail", args=[category.pk])
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert Category.objects.filter(pk=category.pk).exists()


# PRODUCT FAMILY API TESTS

@pytest.mark.django_db
def test_owner_can_create_product_family(api_client, owner):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("product-family-list"),
        {"name": "Cooking Oil"},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    created_family = ProductFamily.objects.get(name="Cooking Oil")
    assert created_family.sku_prefix is None
    assert response.data["sku_prefix"] is None


@pytest.mark.django_db
def test_cashier_can_view_product_families(
    api_client, cashier, family
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(reverse("product-family-list"))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Margarine"


@pytest.mark.django_db
def test_cashier_cannot_create_product_family(api_client, cashier):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("product-family-list"),
        {"name": "Cooking Oil"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not ProductFamily.objects.filter(name="Cooking Oil").exists()


@pytest.mark.django_db
def test_owner_can_update_product_family(api_client, owner, family):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse("product-family-detail", args=[family.pk]),
        {"name": "Margarine Products"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    family.refresh_from_db()
    assert family.name == "Margarine Products"


@pytest.mark.django_db
def test_cashier_cannot_update_product_family(
    api_client, cashier, family
):
    api_client.force_authenticate(user=cashier)

    response = api_client.patch(
        reverse("product-family-detail", args=[family.pk]),
        {"name": "Changed Family"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    family.refresh_from_db()
    assert family.name == "Margarine"


@pytest.mark.django_db
def test_client_cannot_assign_product_family_sku_prefix(
    api_client, owner
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("product-family-list"),
        {
            "name": "Cooking Oil",
            "sku_prefix": "FAKE",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    created_family = ProductFamily.objects.get(name="Cooking Oil")

    assert created_family.sku_prefix is None
    assert response.data["sku_prefix"] is None


@pytest.mark.django_db
def test_product_family_cannot_be_permanently_deleted(
    api_client, owner, family
):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(
        reverse("product-family-detail", args=[family.pk])
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert ProductFamily.objects.filter(pk=family.pk).exists()
