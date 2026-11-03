from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.suppliers.models import Supplier
from apps.suppliers.services.supplier_management import (
    create_supplier,
    update_supplier,
)


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier

        fields = [
            "id",
            "name",
            "contact_person",
            "phone",
            "email",
            "address",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        try:
            return create_supplier(**validated_data)

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            ) from exc

    def update(self, instance, validated_data):
        try:
            return update_supplier(
                instance,
                **validated_data,
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            ) from exc