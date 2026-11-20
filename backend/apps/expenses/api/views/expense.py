
from django.core.exceptions import (
    PermissionDenied,
    ValidationError as DjangoValidationError,
)

from rest_framework import (
    mixins,
    serializers,
    status,
    viewsets,
)
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsOwner
from apps.expenses.api.serializers import ExpenseSerializer
from apps.expenses.models import Expense
from apps.expenses.services import (
    create_expense,
    update_expense,
    delete_expense,
)


class ExpenseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    queryset = Expense.objects.select_related("recorded_by")

    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        data = input_serializer.validated_data

        try:
            expense = create_expense(
                expense_type=data.get(
                    "expense_type",
                    Expense.ExpenseType.OPERATING,
                ),
                category=data["category"],
                custom_category=data.get("custom_category", ""),
                cost_behaviour=data.get(
                    "cost_behaviour",
                    Expense.CostBehaviour.VARIABLE,
                ),
                description=data["description"],
                payee=data.get("payee", ""),
                amount=data["amount"],
                expense_date=data.get("expense_date"),
                payment_method=data["payment_method"],
                payment_reference=data.get("payment_reference", ""),
                is_recurring=data.get("is_recurring", False),
                recorded_by=request.user,
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc

        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc)) from exc

        return Response(
            self.get_serializer(expense).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        expense = self.get_object()

        input_serializer = self.get_serializer(
            expense,
            data=request.data,
            partial=partial,
        )
        input_serializer.is_valid(raise_exception=True)

        data = input_serializer.validated_data

        try:
            expense = update_expense(
                expense=expense,
                updated_by=request.user,
                expense_type=data.get("expense_type", expense.expense_type),
                category=data.get("category", expense.category),
                custom_category=data.get(
                    "custom_category",
                    expense.custom_category,
                ),
                cost_behaviour=data.get(
                    "cost_behaviour",
                    expense.cost_behaviour,
                ),
                description=data.get("description", expense.description),
                payee=data.get("payee", expense.payee),
                amount=data.get("amount", expense.amount),
                expense_date=data.get(
                    "expense_date",
                    expense.expense_date,
                ),
                payment_method=data.get(
                    "payment_method",
                    expense.payment_method,
                ),
                payment_reference=data.get(
                    "payment_reference",
                    expense.payment_reference,
                ),
                is_recurring=data.get(
                    "is_recurring",
                    expense.is_recurring,
                ),
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc

        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc)) from exc

        return Response(
            self.get_serializer(expense).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        expense = self.get_object()

        try:
            delete_expense(
                expense=expense,
                deleted_by=request.user,
            )

        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc)) from exc

        return Response(status=status.HTTP_204_NO_CONTENT)
