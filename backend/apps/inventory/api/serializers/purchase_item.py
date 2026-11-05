from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.inventory.models import PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):

    purchase_reference = serializers.CharField(
        source="purchase.supplier_reference",
        read_only=True,
    )

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    packaging_name = serializers.CharField(
        source="packaging_name_snapshot",
        read_only=True,
    )

    base_quantity = serializers.DecimalField(
        max_digits=15,
        decimal_places=3,
        read_only=True,
    )

    line_subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    landed_total_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    landed_unit_cost = serializers.DecimalField(
        max_digits=15,
        decimal_places=6,
        read_only=True,
    )

    class Meta:
        model = PurchaseItem

        fields = [
            "id",
            "purchase",
            "purchase_reference",
            "product",
            "product_name",
            "packaging",
            "packaging_name",
            "conversion_factor_snapshot",
            "package_quantity",
            "base_quantity",
            "purchase_unit_cost",
            "line_subtotal",
            "allocated_transport_cost",
            "landed_total_cost",
            "landed_unit_cost",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "purchase_reference",
            "product_name",
            "packaging_name",
            "conversion_factor_snapshot",
            "base_quantity",
            "line_subtotal",
            "allocated_transport_cost",
            "landed_total_cost",
            "landed_unit_cost",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        from apps.inventory.services.purchase_creation import (
            add_purchase_item,
        )

        try:
            return add_purchase_item(**validated_data)

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc