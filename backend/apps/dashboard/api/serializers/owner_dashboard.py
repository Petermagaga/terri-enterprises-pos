
from rest_framework import serializers


class OwnerDashboardQuerySerializer(serializers.Serializer):
    PERIOD_CHOICES = [
        ("today", "Today"),
        ("yesterday", "Yesterday"),
        ("this_week", "This week"),
        ("this_month", "This month"),
        ("this_quarter", "This quarter"),
        ("this_year", "This year"),
        ("custom", "Custom range"),
    ]

    period = serializers.ChoiceField(
        choices=PERIOD_CHOICES,
        default="this_week",
    )

    start_date = serializers.DateField(
        required=False,
    )

    end_date = serializers.DateField(
        required=False,
    )


class OwnerDashboardSerializer(serializers.Serializer):
    date = serializers.DateField()

    date_range = serializers.DictField()

    financial_summary = serializers.DictField()

    payment_summary = serializers.DictField()

    sales_summary = serializers.DictField()

    sales_trend = serializers.ListField(
        child=serializers.DictField(),
    )

    stock_summary = serializers.DictField()

    inventory_valuation = serializers.DictField()

    top_products = serializers.ListField(
        child=serializers.DictField(),
    )

    category_performance = serializers.ListField(
        child=serializers.DictField(),
    )