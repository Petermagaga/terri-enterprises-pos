
from datetime import timedelta

import pytest

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.products.models import Category, ProductFamily
from apps.products.services.product_creation import create_product
from apps.sales.models import Sale
from apps.sales.services.sale_creation import create_sale, add_sale_item


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        username="sales_api_owner",
        password="test-password-123",
        role=User.Role.OWNER,
    )


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="sales_api_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def another_cashier(db):
    return User.objects.create_user(
        username="another_sales_cashier",
        password="test-password-123",
        role=User.Role.CASHIER,
    )


@pytest.fixture
def product(db):
    category = Category.objects.create(name="Sales API Groceries")
    family = ProductFamily.objects.create(name="Sales API Margarine")

    return create_product(
        name="Margarine 500g",
        product_family=family,
        category=category,
        size_value=500,
        size_unit="G",
        base_unit="tub",
        retail_price="250.00",
        wholesale_price="230.00",
    )


@pytest.fixture
def cashier_sale(cashier):
    return create_sale(processed_by=cashier)


@pytest.fixture
def sale_with_item(cashier, product):
    sale = create_sale(processed_by=cashier)

    add_sale_item(
        sale=sale,
        product=product,
        pricing_type="RETAIL",
        quantity=2,
    )

    return sale

def mark_sale_completed(sale):
    Sale.objects.filter(pk=sale.pk).update(
        status=Sale.Status.COMPLETED,
    )
    sale.refresh_from_db()
    return sale


# AUTHENTICATION TESTS

@pytest.mark.django_db
def test_unauthenticated_user_cannot_view_sales(api_client):
    response = api_client.get(reverse("sale-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_sale(api_client):
    response = api_client.post(
        reverse("sale-list"),
        {},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Sale.objects.count() == 0


# SALE CREATION TESTS

@pytest.mark.django_db
def test_owner_can_create_draft_sale(api_client, owner):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        reverse("sale-list"),
        {},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == Sale.Status.DRAFT
    assert response.data["processed_by"] == owner.pk

    sale = Sale.objects.get(pk=response.data["id"])
    assert sale.processed_by == owner


@pytest.mark.django_db
def test_cashier_can_create_draft_sale(api_client, cashier):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-list"),
        {},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == Sale.Status.DRAFT
    assert response.data["processed_by"] == cashier.pk

    sale = Sale.objects.get(pk=response.data["id"])
    assert sale.processed_by == cashier


@pytest.mark.django_db
def test_client_cannot_override_sale_status_or_processed_by(
    api_client,
    cashier,
    another_cashier,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.post(
        reverse("sale-list"),
        {
            "status": Sale.Status.COMPLETED,
            "processed_by": another_cashier.pk,
            "total_amount": "999999.00",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == Sale.Status.DRAFT
    assert response.data["processed_by"] == cashier.pk
    assert response.data["total_amount"] == "0.00"

    sale = Sale.objects.get(pk=response.data["id"])
    assert sale.processed_by == cashier
    assert sale.total_amount == 0


# SALE ACCESS TESTS

@pytest.mark.django_db
def test_owner_can_view_all_sales(
    api_client,
    owner,
    cashier_sale,
):
    mark_sale_completed(cashier_sale)
    api_client.force_authenticate(user=owner)

    response = api_client.get(reverse("sale-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == cashier_sale.pk

@pytest.mark.django_db
def test_owner_sales_list_excludes_drafts(
    api_client,
    owner,
):
    draft_sale = create_sale(processed_by=owner)
    completed_sale = create_sale(processed_by=owner)

    mark_sale_completed(completed_sale)

    api_client.force_authenticate(user=owner)

    response = api_client.get(reverse("sale-list"))

    assert response.status_code == status.HTTP_200_OK

    sale_ids = [
        item["id"] for item in response.data["results"]
    ]

    assert completed_sale.pk in sale_ids
    assert draft_sale.pk not in sale_ids
    assert response.data["count"] == 1
@pytest.mark.django_db
def test_cashier_sales_list_excludes_drafts(
    api_client,
    cashier,
):
    draft_sale = create_sale(processed_by=cashier)
    completed_sale = create_sale(processed_by=cashier)

    mark_sale_completed(completed_sale)

    api_client.force_authenticate(user=cashier)

    response = api_client.get(reverse("sale-list"))

    assert response.status_code == status.HTTP_200_OK

    sale_ids = [
        item["id"] for item in response.data["results"]
    ]

    assert completed_sale.pk in sale_ids
    assert draft_sale.pk not in sale_ids
    assert response.data["count"] == 1

@pytest.mark.django_db
def test_owner_can_retrieve_draft_sale(
    api_client,
    owner,
):
    draft_sale = create_sale(processed_by=owner)

    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("sale-detail", args=[draft_sale.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == draft_sale.pk
    assert response.data["status"] == Sale.Status.DRAFT

@pytest.mark.django_db
def test_cashier_can_view_only_their_own_sales(
    api_client,
    cashier,
    another_cashier,
):

    own_sale = create_sale(processed_by=cashier)
    other_sale = create_sale(processed_by=another_cashier)

    mark_sale_completed(own_sale)
    mark_sale_completed(other_sale)

    api_client.force_authenticate(user=cashier)

    response = api_client.get(reverse("sale-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == own_sale.pk

@pytest.mark.django_db
def test_cashier_cannot_retrieve_another_cashiers_sale(
    api_client,
    cashier,
    another_cashier,
):
    other_sale = create_sale(processed_by=another_cashier)

    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("sale-detail", args=[other_sale.pk])
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_cashier_cannot_view_sales_older_than_seven_days(
    api_client,
    cashier,
):    
    recent_sale = create_sale(processed_by=cashier)
    old_sale = create_sale(processed_by=cashier)

    mark_sale_completed(recent_sale)
    mark_sale_completed(old_sale)

    Sale.objects.filter(pk=old_sale.pk).update(
        created_at=timezone.now() - timedelta(days=8)
    )

    api_client.force_authenticate(user=cashier)

    response = api_client.get(reverse("sale-list"))

    assert response.status_code == status.HTTP_200_OK    
    sale_ids = [
        item["id"] for item in response.data["results"]
    ]

    assert recent_sale.pk in sale_ids
    assert old_sale.pk not in sale_ids


# FINANCIAL DATA VISIBILITY TESTS

@pytest.mark.django_db
def test_owner_can_view_sale_cost_and_gross_profit(
    api_client,
    owner,
    sale_with_item,
):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        reverse("sale-detail", args=[sale_with_item.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert "total_cost" in response.data
    assert "gross_profit" in response.data


    item = response.data["items"][0]
    assert "total_cost" in item


@pytest.mark.django_db
def test_cashier_cannot_view_sale_cost_or_gross_profit(
    api_client,
    cashier,
    sale_with_item,
):
    api_client.force_authenticate(user=cashier)

    response = api_client.get(
        reverse("sale-detail", args=[sale_with_item.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert "total_cost" not in response.data
    assert "gross_profit" not in response.data

    item = response.data["items"][0]
    assert "total_cost" not in item
