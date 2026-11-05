from rest_framework import serializers

from apps.inventory.models import StockMovement


class StockAdjustmentMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    product_sku = serializers.CharField(
        source="product.sku",
        read_only=True,
    )

    base_unit = serializers.CharField(
        source="product.base_unit",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = StockMovement

        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "base_unit",
            "stock_batch",
            "movement_type",
            "direction",
            "quantity",
            "unit_cost",
            "reference",
            "notes",
            "created_by",
            "created_by_username",
            "created_at",
        ]

        read_only_fields = fields