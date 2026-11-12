
from django.db import transaction

from apps.accounts.models import User
from apps.accounts.services.tokens import revoke_user_token


@transaction.atomic
def create_cashier(*, username, password, first_name="", last_name="", email=""):
    return User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=User.Role.CASHIER,
    )


@transaction.atomic
def update_cashier(cashier, *, username=None, first_name=None, last_name=None, email=None):
    if cashier.role != User.Role.CASHIER:
        raise ValueError("Only cashier accounts can be managed here.")

    fields_to_update = []

    for field, value in (
        ("username", username),
        ("first_name", first_name),
        ("last_name", last_name),
        ("email", email),
    ):
        if value is not None:
            setattr(cashier, field, value)
            fields_to_update.append(field)

    if fields_to_update:
        cashier.save(update_fields=fields_to_update)

    return cashier


@transaction.atomic
def set_cashier_active_status(cashier, *, is_active):
    if cashier.role != User.Role.CASHIER:
        raise ValueError("Only cashier accounts can be managed here.")

    cashier.is_active = is_active
    cashier.save(update_fields=["is_active"])

    if not is_active:
        revoke_user_token(cashier)

    return cashier


@transaction.atomic
def reset_cashier_password(cashier, *, password):
    if cashier.role != User.Role.CASHIER:
        raise ValueError("Only cashier accounts can be managed here.")

    cashier.set_password(password)
    cashier.save(update_fields=["password"])

    revoke_user_token(cashier)

    return cashier
