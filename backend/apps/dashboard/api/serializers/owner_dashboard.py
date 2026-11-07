from rest_framework import serializers


class OwnerDashboardSerializer(serializers.Serializer):
    date = serializers.DateField()

    financial_summary = serializers.DictField()

    payment_summary = serializers.DictField()

    sales_summary = serializers.DictField()

    stock_summary = serializers.DictField()

    top_products = serializers.ListField(
        child=serializers.DictField(),
    )