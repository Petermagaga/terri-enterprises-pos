
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.products.models import Product
from apps.products.services.product_creation import create_product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializes product data for the POS API.

    Product creation is delegated to the product creation service
    so that SKU generation and model validation remain centralized.
    """

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "product_family",
            "sku",
            "category",
            "brand",
            "size_value",
            "size_unit",
            "base_unit",
            "retail_price",
            "wholesale_price",
            "reorder_level",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "sku",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        try:
            return create_product(**validated_data)
        except DjangoValidationError as exc:
            detail = getattr(exc, "message_dict", None) or exc.messages
            raise serializers.ValidationError(detail) from exc

    def update(self, instance, validated_data):
        try:
            for field, value in validated_data.items():
                setattr(instance, field, value)

            instance.full_clean()
            instance.save()

            return instance

        except DjangoValidationError as exc:
            detail = getattr(exc, "message_dict", None) or exc.messages
            raise serializers.ValidationError(detail) from exc
