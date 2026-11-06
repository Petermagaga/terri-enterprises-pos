
from datetime import date
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from apps.reporting.services.date_ranges import (
    DateRange,
    get_date_range,
)


TODAY = date(2026, 11, 6)


@pytest.fixture
def mock_today():
    with patch(
        "apps.reporting.services.date_ranges.timezone.localdate",
        return_value=TODAY,
    ):
        yield


def test_today_range(mock_today):
    result = get_date_range("today")

    assert result == DateRange(TODAY, TODAY)


def test_yesterday_range(mock_today):
    result = get_date_range("yesterday")

    assert result == DateRange(
        date(2026, 11, 5),
        date(2026, 11, 5),
    )


def test_this_week_range(mock_today):
    result = get_date_range("this_week")

    assert result == DateRange(
        date(2026, 11, 2),
        TODAY,
    )


def test_this_month_range(mock_today):
    result = get_date_range("this_month")

    assert result == DateRange(
        date(2026, 11, 1),
        TODAY,
    )


def test_this_quarter_range(mock_today):
    result = get_date_range("this_quarter")

    assert result == DateRange(
        date(2026, 10, 1),
        TODAY,
    )


def test_this_year_range(mock_today):
    result = get_date_range("this_year")

    assert result == DateRange(
        date(2026, 1, 1),
        TODAY,
    )


def test_custom_range(mock_today):
    result = get_date_range(
        "custom",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 31),
    )

    assert result == DateRange(
        date(2026, 10, 1),
        date(2026, 10, 31),
    )


def test_custom_range_requires_both_dates(mock_today):
    with pytest.raises(ValidationError):
        get_date_range(
            "custom",
            start_date=date(2026, 10, 1),
        )


def test_custom_range_rejects_start_after_end(mock_today):
    with pytest.raises(ValidationError):
        get_date_range(
            "custom",
            start_date=date(2026, 10, 31),
            end_date=date(2026, 10, 1),
        )


def test_custom_range_rejects_future_end_date(mock_today):
    with pytest.raises(ValidationError):
        get_date_range(
            "custom",
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
        )


def test_unsupported_preset(mock_today):
    with pytest.raises(ValidationError):
        get_date_range("last_month")
