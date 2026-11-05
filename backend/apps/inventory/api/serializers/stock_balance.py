from rest_framework import serializers

from apps.inventory.models import InventoryBalance


class StockBalanceSerializer(serializers.ModelSerializer):
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

    reorder_level = serializers.IntegerField(
        source="product.reorder_level",
        read_only=True,
    )

    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = InventoryBalance

        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "base_unit",
            "quantity_on_hand",
            "reorder_level",
            "is_low_stock",
            "updated_at",
        ]

        read_only_fields = fields

    def get_is_low_stock(self, obj):
        return (
            obj.quantity_on_hand
            <= obj.product.reorder_level
        )