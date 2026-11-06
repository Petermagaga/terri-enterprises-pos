from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.accounts.models import User
from apps.expenses.models import Expense


@transaction.atomic
def delete_expense(
    *,
    expense,
    deleted_by,
):

    if (
        deleted_by is None
        or not deleted_by.is_authenticated
    ):
        raise PermissionDenied("Authentication is required.")

    if not deleted_by.is_active:
        raise PermissionDenied("Inactive users cannot delete expenses.")

    if deleted_by.role != User.Role.OWNER:
        raise PermissionDenied("Only the Owner can delete expenses.")

    expense.delete()