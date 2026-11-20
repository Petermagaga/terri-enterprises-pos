
from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.accounts.models import User
from apps.expenses.models import Expense


@transaction.atomic
def update_expense(
    *,
    expense,
    updated_by,
    description=None,
    category=None,
    amount=None,
    expense_date=None,
    payment_method=None,
    payment_reference=None,
    expense_type=None,
    custom_category=None,
    cost_behaviour=None,
    payee=None,
    is_recurring=None,
):
    if (
        updated_by is None
        or not updated_by.is_authenticated
    ):
        raise PermissionDenied("Authentication is required.")

    if not updated_by.is_active:
        raise PermissionDenied("Inactive users cannot update expenses.")

    if updated_by.role != User.Role.OWNER:
        raise PermissionDenied("Only the Owner can update expenses.")

    update_fields = {
        "description": description,
        "category": category,
        "amount": amount,
        "expense_date": expense_date,
        "payment_method": payment_method,
        "payment_reference": payment_reference,
        "expense_type": expense_type,
        "custom_category": custom_category,
        "cost_behaviour": cost_behaviour,
        "payee": payee,
        "is_recurring": is_recurring,
    }

    for field, value in update_fields.items():
        if value is not None:
            setattr(expense, field, value)

    # recorded_by is intentionally preserved.
    expense.full_clean()
    expense.save()

    return expense
