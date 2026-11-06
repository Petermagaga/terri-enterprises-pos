
from dataclasses import dataclass
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone


@dataclass(frozen=True)
class DateRange:
    start_date: date
    end_date: date


def get_date_range(
    preset: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> DateRange:
    """
    Return an inclusive reporting date range using Django's local date.

    Supported presets:
        today, yesterday, this_week, this_month,
        this_quarter, this_year, custom
    """
    today = timezone.localdate()

    if preset == "today":
        return DateRange(today, today)

    if preset == "yesterday":
        yesterday = today - timedelta(days=1)
        return DateRange(yesterday, yesterday)

    if preset == "this_week":
        monday = today - timedelta(days=today.weekday())
        return DateRange(monday, today)

    if preset == "this_month":
        first_day = today.replace(day=1)
        return DateRange(first_day, today)

    if preset == "this_quarter":
        quarter_start_month = ((today.month - 1) // 3) * 3 + 1
        first_day = today.replace(
            month=quarter_start_month,
            day=1,
        )
        return DateRange(first_day, today)

    if preset == "this_year":
        first_day = today.replace(month=1, day=1)
        return DateRange(first_day, today)

    if preset == "custom":
        if start_date is None or end_date is None:
            raise ValidationError(
                "Both start_date and end_date are required for a custom range."
            )

        if start_date > end_date:
            raise ValidationError(
                "start_date cannot be later than end_date."
            )

        if end_date > today:
            raise ValidationError(
                "end_date cannot be in the future."
            )

        return DateRange(start_date, end_date)

    raise ValidationError(
        f"Unsupported date range preset: {preset}."
    )
