from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.accounts.models import User
from apps.expenses.models import Expense


@transaction.atomic
def create_expense(
    *,
    description,
    category,
    amount,
    payment_method,
    recorded_by,
    expense_date=None,
    payment_reference="",
):
    if (
        recorded_by is None
        or not recorded_by.is_authenticated
    ):
        raise PermissionDenied("Authentication is required.")


    if not recorded_by.is_active:
        raise PermissionDenied("Inactive users cannot record expenses.")

    if recorded_by.role != User.Role.OWNER:
        raise PermissionDenied("Only the Owner can record expenses.")

    expense_data = {
        "description": description,
        "category": category,
        "amount": amount,
        "payment_method": payment_method,
        "payment_reference": payment_reference,
        "recorded_by": recorded_by,
    }

    if expense_date is not None:
        expense_data["expense_date"] = expense_date

    expense = Expense(**expense_data)
    expense.save()

    return expense