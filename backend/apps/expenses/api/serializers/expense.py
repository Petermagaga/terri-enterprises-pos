
from rest_framework import serializers

from apps.expenses.models import Expense


class ExpenseSerializer(serializers.ModelSerializer):

    recorded_by_username = serializers.CharField(
        source="recorded_by.username",
        read_only=True,
    )

    class Meta:
        model = Expense
        fields = [
            "id",
            "expense_type",
            "category",
            "custom_category",
            "cost_behaviour",
            "description",
            "payee",
            "amount",
            "expense_date",
            "payment_method",
            "payment_reference",
            "is_recurring",
            "recorded_by",
            "recorded_by_username",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "recorded_by",
            "recorded_by_username",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        """
        Validate the complete expense, including partial updates.
        The model's clean() method handles the business rules.
        """
        instance = self.instance

        values = {
            "expense_type": attrs.get(
                "expense_type",
                instance.expense_type if instance else Expense.ExpenseType.OPERATING,
            ),
            "category": attrs.get(
                "category",
                instance.category if instance else None,
            ),
            "custom_category": attrs.get(
                "custom_category",
                instance.custom_category if instance else "",
            ),
            "payment_method": attrs.get(
                "payment_method",
                instance.payment_method if instance else None,
            ),
            "payment_reference": attrs.get(
                "payment_reference",
                instance.payment_reference if instance else "",
            ),
        }

        if values["category"] is None:
            return attrs

        expense = instance or Expense()

        for field, value in values.items():
            setattr(expense, field, value)

        try:
            expense.clean()
        except Exception as exc:
            from django.core.exceptions import ValidationError

            if isinstance(exc, ValidationError):
                raise serializers.ValidationError(exc.message_dict)
            raise

        return attrs
