import pytest
from rest_framework.test import APIRequestFactory

from apps.accounts.models import User
from apps.accounts.permissions import IsOwner, IsOwnerOrCashier


@pytest.fixture
def owner(db):
    return User.objects.create_superuser(
        username="owner_test",
        email="owner@test.com",
        password="TestPassword123!",
    )


@pytest.fixture
def cashier(db):
    return User.objects.create_user(
        username="cashier_test",
        email="cashier@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


def test_owner_can_access_owner_resources(owner):
    request = APIRequestFactory().get("/")
    request.user = owner

    assert IsOwner().has_permission(request, None) is True


def test_cashier_cannot_access_owner_resources(cashier):
    request = APIRequestFactory().get("/")
    request.user = cashier

    assert IsOwner().has_permission(request, None) is False


def test_owner_can_access_shared_resources(owner):
    request = APIRequestFactory().get("/")
    request.user = owner

    assert IsOwnerOrCashier().has_permission(request, None) is True


def test_cashier_can_access_shared_resources(cashier):
    request = APIRequestFactory().get("/")
    request.user = cashier

    assert IsOwnerOrCashier().has_permission(request, None) is True

def test_superuser_is_always_created_as_owner(db):
    user = User.objects.create_superuser(
        username="forced_owner_test",
        email="forced_owner@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )

    assert user.role == User.Role.OWNER
    assert user.is_superuser is True
    assert user.is_staff is True