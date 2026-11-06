from rest_framework import serializers


class DateRangeQuerySerializer(serializers.Serializer):
    PRESET_CHOICES = [
        ("today", "Today"),
        ("yesterday", "Yesterday"),
        ("this_week", "This week"),
        ("this_month", "This month"),
        ("this_quarter", "This quarter"),
        ("this_year", "This year"),
        ("custom", "Custom range"),
    ]

    preset = serializers.ChoiceField(
        choices=PRESET_CHOICES,
        default="today",
    )

    start_date = serializers.DateField(
        required=False,
    )

    end_date = serializers.DateField(
        required=False,
    )


class SalesSummaryQuerySerializer(DateRangeQuerySerializer):
    GROUPING_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]

    group_by = serializers.ChoiceField(
        choices=GROUPING_CHOICES,
        default="daily",
    )