from rest_framework import serializers

from apps.products.models import ProductFamily


class ProductFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFamily
        fields = [
            "id",
            "name",
            "sku_prefix",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "sku_prefix",
            "created_at",
            "updated_at",
        ]