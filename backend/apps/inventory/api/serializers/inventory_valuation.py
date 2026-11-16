from rest_framework import serializers


class InventoryValuationProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(read_only=True)
    product_name = serializers.CharField(read_only=True)
    product_sku = serializers.CharField(read_only=True)
    base_unit = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    quantity_on_hand = serializers.DecimalField(
        max_digits=30,
        decimal_places=3,
        read_only=True,
    )
    unit_cost = serializers.DecimalField(
        max_digits=30,
        decimal_places=6,
        read_only=True,
    )
    stock_value = serializers.DecimalField(
        max_digits=30,
        decimal_places=2,
        read_only=True,
    )


class InventoryValuationSerializer(serializers.Serializer):
    total_inventory_value = serializers.DecimalField(
        max_digits=30,
        decimal_places=2,
        read_only=True,
    )
    products_with_stock = serializers.IntegerField(read_only=True)
    products = InventoryValuationProductSerializer(
        many=True,
        read_only=True,
    )
