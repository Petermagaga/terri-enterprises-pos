from rest_framework import serializers

from apps.inventory.models import ProductPackaging


class ProductPackagingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductPackaging

        fields = [
            "id",
            "product",
            "name",
            "conversion_factor",
            "purchase_enabled",
            "sales_enabled",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        instance = self.instance

        if instance is not None:
            new_factor = attrs.get(
                "conversion_factor",
                instance.conversion_factor,
            )

            new_product = attrs.get(
                "product",
                instance.product,
            )

            if instance.purchase_items.exists():
                if new_factor != instance.conversion_factor:
                    raise serializers.ValidationError({
                        "conversion_factor": (
                            "This packaging has been used in purchases. "
                            "Deactivate it and create a new packaging "
                            "option instead."
                        )
                    })

                if new_product.pk != instance.product_id:
                    raise serializers.ValidationError({
                        "product": (
                            "You cannot change the product of packaging "
                            "that has already been used."
                        )
                    })

        return attrs