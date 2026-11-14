import pytest

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from apps.accounts.models import User


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def owner():
    return User.objects.create_superuser(
        username="auth_owner",
        email="auth_owner@test.com",
        password="TestPassword123!",
    )


@pytest.fixture
def cashier():
    return User.objects.create_user(
        username="auth_cashier",
        email="auth_cashier@test.com",
        password="TestPassword123!",
        role=User.Role.CASHIER,
    )


def test_owner_can_login(api_client, owner):
    response = api_client.post(
        "/api/auth/login/",
        {
            "username": "auth_owner",
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.data
    assert response.data["user"]["role"] == User.Role.OWNER
    assert response.data["user"]["username"] == owner.username
    assert "password" not in response.data["user"]


def test_cashier_can_login(api_client, cashier):
    response = api_client.post(
        "/api/auth/login/",
        {
            "username": "auth_cashier",
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["user"]["role"] == User.Role.CASHIER


def test_login_rejects_invalid_password(api_client, owner):
    response = api_client.post(
        "/api/auth/login/",
        {
            "username": "auth_owner",
            "password": "WrongPassword123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in response.data


def test_login_rejects_unknown_username(api_client):
    response = api_client.post(
        "/api/auth/login/",
        {
            "username": "unknown_user",
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_rejects_inactive_user(api_client, cashier):
    cashier.is_active = False
    cashier.save(update_fields=["is_active"])

    response = api_client.post(
        "/api/auth/login/",
        {
            "username": "auth_cashier",
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_reuses_existing_token(api_client, owner):
    existing_token = Token.objects.create(user=owner)

    response = api_client.post(
        "/api/auth/login/",
        {
            "username": "auth_owner",
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["token"] == existing_token.key
    assert Token.objects.filter(user=owner).count() == 1


def test_current_user_returns_authenticated_user(api_client, cashier):
    token = Token.objects.create(user=cashier)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Token {token.key}"
    )

    response = api_client.get("/api/auth/me/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == cashier.username
    assert response.data["role"] == User.Role.CASHIER


def test_current_user_requires_authentication(api_client):
    response = api_client.get("/api/auth/me/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_deletes_authentication_token(api_client, owner):
    token = Token.objects.create(user=owner)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Token {token.key}"
    )

    response = api_client.post("/api/auth/logout/")

    assert response.status_code == status.HTTP_200_OK
    assert not Token.objects.filter(user=owner).exists()


def test_logout_requires_authentication(api_client):
    response = api_client.post("/api/auth/logout/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_owner_can_change_username(api_client, owner):
    token = Token.objects.create(user=owner)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Token {token.key}"
    )

    response = api_client.patch(
        "/api/auth/settings/",
        {
            "username": "new_owner_name",
            "current_password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    owner.refresh_from_db()
    assert owner.username == "new_owner_name"


def test_cashier_can_change_password(api_client, cashier):
    token = Token.objects.create(user=cashier)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Token {token.key}"
    )

    response = api_client.patch(
        "/api/auth/settings/",
        {
            "current_password": "TestPassword123!",
            "new_password": "NewSecurePassword456!",
            "confirm_new_password": "NewSecurePassword456!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    cashier.refresh_from_db()
    assert cashier.check_password("NewSecurePassword456!")


def test_account_settings_rejects_wrong_current_password(api_client, owner):
    token = Token.objects.create(user=owner)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Token {token.key}"
    )

    response = api_client.patch(
        "/api/auth/settings/",
        {
            "username": "changed_name",
            "current_password": "WrongPassword123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    owner.refresh_from_db()
    assert owner.username == "auth_owner"


def test_account_settings_rejects_duplicate_username(api_client, owner, cashier):
    token = Token.objects.create(user=owner)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Token {token.key}"
    )

    response = api_client.patch(
        "/api/auth/settings/",
        {
            "username": cashier.username,
            "current_password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_account_settings_rejects_mismatched_passwords(api_client, owner):
    token = Token.objects.create(user=owner)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Token {token.key}"
    )

    response = api_client.patch(
        "/api/auth/settings/",
        {
            "current_password": "TestPassword123!",
            "new_password": "NewSecurePassword456!",
            "confirm_new_password": "DifferentPassword789!",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    owner.refresh_from_db()
    assert owner.check_password("TestPassword123!")