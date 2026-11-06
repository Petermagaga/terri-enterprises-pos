from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.accounts.models import User
from apps.expenses.models import Expense


@transaction.atomic
def update_expense(
    *,
    expense,
    updated_by,
    description,
    category,
    amount,
    expense_date,
    payment_method,
    payment_reference="",
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

    expense.description = description
    expense.category = category
    expense.amount = amount
    expense.expense_date = expense_date
    expense.payment_method = payment_method
    expense.payment_reference = payment_reference

    # recorded_by is intentionally preserved.
    expense.save()

    return expense