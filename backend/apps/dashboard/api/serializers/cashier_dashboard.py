from rest_framework import serializers


class CashierDashboardSerializer(serializers.Serializer):
    date = serializers.DateField()

    sales_summary = serializers.DictField()

    payment_summary = serializers.DictField()

    stock_summary = serializers.DictField()

    recent_sales = serializers.ListField(
        child=serializers.DictField(),
    )