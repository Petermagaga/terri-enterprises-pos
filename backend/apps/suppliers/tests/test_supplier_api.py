
import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.suppliers.models import Supplier


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        username="supplier_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="supplier_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def supplier(db):
    return Supplier.objects.create(
        name="ABC Distributors",
        contact_person="John Doe",
        phone="0712345678",
        email="abc@example.com",
        address="Mlolongo",
    )


@pytest.fixture
def supplier_data():
    return {
        "name": "XYZ Wholesalers",
        "contact_person": "Jane Doe",
        "phone": "0723456789",
        "email": "xyz@example.com",
        "address": "Nairobi",
        "notes": "Main stock supplier",
    }


# AUTHENTICATION TESTS

@pytest.mark.django_db
def test_unauthenticated_user_cannot_view_suppliers(api_client):
    response = api_client.get(reverse("supplier-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_supplier(
    api_client, supplier_data
):
    response = api_client.post(
        reverse("supplier-list"),
        supplier_data,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Supplier.objects.count() == 0


# CASHIER PERMISSION TESTS

@pytest.mark.django_db
def test_cashier_cannot_view_suppliers(
    api_client, cashier, supplier
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(reverse("supplier-list"))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_cashier_cannot_create_supplier(
    api_client, cashier, supplier_data
):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("supplier-list"),
        supplier_data,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Supplier.objects.count() == 0


@pytest.mark.django_db
def test_cashier_cannot_update_supplier(
    api_client, cashier, supplier
):
    api_client.force_authenticate(user=cashier)

    response = api_client.patch(
        reverse("supplier-detail", args=[supplier.pk]),
        {"name": "Changed Supplier"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    supplier.refresh_from_db()
    assert supplier.name == "ABC Distributors"


# OWNER API TESTS

@pytest.mark.django_db
def test_owner_can_view_suppliers(
    api_client, owner, supplier
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(reverse("supplier-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "ABC Distributors"


@pytest.mark.django_db
def test_owner_can_retrieve_supplier(
    api_client, owner, supplier
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("supplier-detail", args=[supplier.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "ABC Distributors"


@pytest.mark.django_db
def test_owner_can_create_supplier(
    api_client, owner, supplier_data
):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("supplier-list"),
        supplier_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Supplier.objects.filter(
        name="XYZ Wholesalers"
    ).exists()


@pytest.mark.django_db
def test_owner_can_update_supplier(
    api_client, owner, supplier
):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse("supplier-detail", args=[supplier.pk]),
        {"name": "ABC Wholesale Distributors"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    supplier.refresh_from_db()
    assert supplier.name == "ABC Wholesale Distributors"


@pytest.mark.django_db
def test_owner_can_deactivate_supplier(
    api_client, owner, supplier
):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        reverse("supplier-detail", args=[supplier.pk]),
        {"is_active": False},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    supplier.refresh_from_db()
    assert supplier.is_active is False


# VALIDATION TESTS

@pytest.mark.django_db
def test_supplier_name_cannot_be_blank(
    api_client, owner, supplier_data
):
    api_client.force_authenticate(user=owner)
    supplier_data["name"] = ""

    response = api_client.post(
        reverse("supplier-list"),
        supplier_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Supplier.objects.count() == 0


@pytest.mark.django_db
def test_supplier_phone_cannot_be_blank(
    api_client, owner, supplier_data
):
    api_client.force_authenticate(user=owner)
    supplier_data["phone"] = ""

    response = api_client.post(
        reverse("supplier-list"),
        supplier_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Supplier.objects.count() == 0


@pytest.mark.django_db
def test_supplier_email_must_be_valid(
    api_client, owner, supplier_data
):
    api_client.force_authenticate(user=owner)
    supplier_data["email"] = "not-an-email"

    response = api_client.post(
        reverse("supplier-list"),
        supplier_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Supplier.objects.count() == 0


# DATA PROTECTION TESTS

@pytest.mark.django_db
def test_client_cannot_override_supplier_id(
    api_client, owner, supplier_data
):
    api_client.force_authenticate(user=owner)
    supplier_data["id"] = 9999

    response = api_client.post(
        reverse("supplier-list"),
        supplier_data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["id"] != 9999
    assert not Supplier.objects.filter(pk=9999).exists()


@pytest.mark.django_db
def test_supplier_cannot_be_permanently_deleted(
    api_client, owner, supplier
):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(
        reverse("supplier-detail", args=[supplier.pk])
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert Supplier.objects.filter(pk=supplier.pk).exists()
