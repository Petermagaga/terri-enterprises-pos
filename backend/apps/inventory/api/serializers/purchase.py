from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.inventory.models import Purchase
from apps.suppliers.models import Supplier


class PurchaseSerializer(serializers.ModelSerializer):

    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = Purchase
        fields = [
            "id",
            "supplier",
            "supplier_name",
            "supplier_reference",
            "purchase_date",
            "status",
            "transport_cost",
            "created_by",
            "created_by_username",
            "received_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_by",
            "created_by_username",
            "received_at",
            "created_at",
            "updated_at",
        ]

    def validate_supplier(self, supplier):
        if not supplier.is_active:
            raise serializers.ValidationError(
                "Cannot create a purchase for an inactive supplier."
            )
        return supplier

    def create(self, validated_data):
        from apps.inventory.services.purchase_creation import (
            create_purchase,
        )

        try:
            return create_purchase(
                supplier=validated_data["supplier"],
                created_by=self.context["request"].user,
                purchase_date=validated_data.get("purchase_date"),
                supplier_reference=validated_data.get(
                    "supplier_reference", ""
                ),
                transport_cost=validated_data.get(
                    "transport_cost", "0.00"
                ),
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc

    def update(self, instance, validated_data):
        if instance.status != Purchase.Status.DRAFT:
            raise serializers.ValidationError(
                "Received purchases cannot be modified."
            )

        try:
            for field, value in validated_data.items():
                setattr(instance, field, value)

            instance.full_clean()
            instance.save()

            return instance

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc