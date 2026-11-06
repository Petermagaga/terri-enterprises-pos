from rest_framework import serializers

from apps.sales.models import Sale, SaleItem, SalePayment


class OwnerFinancialFieldsMixin:
    """
    Hide financial cost fields from users who are not Owners.
    """

    def get_fields(self):
        fields = super().get_fields()

        request = self.context.get("request")
        user = getattr(request, "user", None)

        is_owner = (
            getattr(user, "is_authenticated", False)
            and getattr(user, "role", None) == "OWNER"
        )

        if not is_owner:
            fields.pop("total_cost", None)
            fields.pop("gross_profit", None)

        return fields


class SaleItemSerializer(
    OwnerFinancialFieldsMixin,
    serializers.ModelSerializer,
):
    base_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = SaleItem
        fields = [
            "id",
            "product",
            "product_name_snapshot",
            "product_sku_snapshot",
            "base_unit_snapshot",
            "packaging",
            "packaging_name_snapshot",
            "conversion_factor_snapshot",
            "base_quantity",
            "pricing_type",
            "quantity",
            "selling_price_per_package",
            "total_amount",
            "total_cost",
            "created_at",
        ]
        read_only_fields = fields


class SalePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePayment
        fields = [
            "id",
            "payment_method",
            "amount",
            "reference",
            "received_by",
            "created_at",
        ]
        read_only_fields = fields


class SaleSerializer(
    OwnerFinancialFieldsMixin,
    serializers.ModelSerializer,
):
    items = SaleItemSerializer(many=True, read_only=True)
    payments = SalePaymentSerializer(many=True, read_only=True)
    gross_profit = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Sale
        fields = [
            "id",
            "receipt_number",
            "processed_by",
            "status",
            "total_amount",
            "total_cost",
            "gross_profit",
            "items",
            "payments",
            "created_at",
            "completed_at",
        ]
        read_only_fields = fields