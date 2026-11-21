from rest_framework import serializers

from apps.inventory.models import StockAlert


class StockAlertSerializer(serializers.ModelSerializer):
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

    is_out_of_stock = serializers.SerializerMethodField()

    class Meta:
        model = StockAlert
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "base_unit",
            "quantity_on_hand",
            "reorder_level",
            "is_out_of_stock",
            "is_read",
            "created_at",
        ]
        read_only_fields = fields

    def get_is_out_of_stock(self, obj):
        return obj.quantity_on_hand <= 0
