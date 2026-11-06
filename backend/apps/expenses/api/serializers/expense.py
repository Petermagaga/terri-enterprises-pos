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
            "description",
            "category",
            "amount",
            "expense_date",
            "payment_method",
            "payment_reference",
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