
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
    expense_type=Expense.ExpenseType.OPERATING,
    custom_category="",
    cost_behaviour=Expense.CostBehaviour.VARIABLE,
    payee="",
    expense_date=None,
    payment_reference="",
    is_recurring=False,
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
        "expense_type": expense_type,
        "category": category,
        "custom_category": custom_category,
        "cost_behaviour": cost_behaviour,
        "description": description,
        "payee": payee,
        "amount": amount,
        "payment_method": payment_method,
        "payment_reference": payment_reference,
        "is_recurring": is_recurring,
        "recorded_by": recorded_by,
    }

    if expense_date is not None:
        expense_data["expense_date"] = expense_date

    expense = Expense(**expense_data)

    # Run field validation and the model's custom business rules.
    expense.full_clean()

    expense.save()

    return expense
