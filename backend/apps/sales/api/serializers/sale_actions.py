from decimal import Decimal

from rest_framework import serializers

from apps.products.models import Product
from apps.inventory.models import ProductPackaging
from apps.sales.models import SaleItem, SalePayment


class AddSaleItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
    )
    pricing_type = serializers.ChoiceField(
        choices=SaleItem.PricingType.choices,
    )
    quantity = serializers.IntegerField(min_value=1)
    packaging = serializers.PrimaryKeyRelatedField(
        queryset=ProductPackaging.objects.all(),
        required=False,
        allow_null=True,
    )


class AddSalePaymentSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(
        choices=SalePayment.PaymentMethod.choices,
    )
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    reference = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
    )