from rest_framework import serializers

from apps.inventory.models import StockMovement
from apps.products.models import Product
from decimal import Decimal

class StockAdjustmentSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
    )

    quantity = serializers.DecimalField(
        max_digits=15,
        decimal_places=3,
        min_value=Decimal("0.001"),
    )

    movement_type = serializers.ChoiceField(
        choices=[
            StockMovement.MovementType.ADJUSTMENT_IN,
            StockMovement.MovementType.ADJUSTMENT_OUT,
            StockMovement.MovementType.DAMAGE,
        ],
    )

    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )

    unit_cost = serializers.DecimalField(
        max_digits=15,
        decimal_places=6,
        min_value=0,
        required=False,
        allow_null=True,
    )

    reference = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
        default="",
    )

    def validate(self, attrs):
        movement_type = attrs["movement_type"]
        unit_cost = attrs.get("unit_cost")

        if movement_type == StockMovement.MovementType.ADJUSTMENT_IN:
            if unit_cost is None:
                raise serializers.ValidationError({
                    "unit_cost": "Unit cost is required for stock increases."
                })

        elif unit_cost is not None:
            raise serializers.ValidationError({
                "unit_cost": (
                    "Unit cost must not be supplied for stock reductions "
                    "or damage."
                )
            })

        return attrs