
from rest_framework import serializers

from apps.accounts.models import User


class CashierCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        from apps.accounts.services.cashiers import create_cashier

        return create_cashier(**validated_data)


class CashierUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
        ]
        read_only_fields = ["id"]


class CashierPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
        style={"input_type": "password"},
    )
