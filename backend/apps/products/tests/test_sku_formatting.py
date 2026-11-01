import pytest
from django.core.exceptions import ValidationError

from apps.products.services.sku import (
    normalize_family_name,
    generate_prefix_candidates,
    format_size_for_sku,
)


@pytest.mark.parametrize(
    "size, unit, expected",
    [
        (50, "G", "050G"),
        (500, "G", "500G"),
        (1, "KG", "001KG"),
        (500, "ML", "500ML"),
        ("0.5", "L", "0P5L"),
        ("1.5", "L", "1P5L"),
        ("0.05", "L", "0P05L"),
        ("0.500", "L", "0P5L"),
    ],
)
def test_format_size_for_sku(size, unit, expected):
    assert format_size_for_sku(size, unit) == expected


@pytest.mark.parametrize(
    "size, unit",
    [
        (0, "L"),
        (-1, "G"),
        ("invalid", "ML"),
        (1, "INVALID"),
    ],
)
def test_invalid_size_is_rejected(size, unit):
    with pytest.raises(ValidationError):
        format_size_for_sku(size, unit)


def test_normalize_family_name():
    assert normalize_family_name("Cooking Oil") == "COOKINGOIL"
    assert normalize_family_name("Margarine 500g") == "MARGARINEG"


def test_prefix_candidates_are_four_letters_and_unique():
    candidates = generate_prefix_candidates("Margarine")

    assert candidates[0] == "MARG"
    assert all(len(candidate) == 4 for candidate in candidates)
    assert len(candidates) == len(set(candidates))


def test_short_family_names_generate_four_letter_prefixes():
    candidates = generate_prefix_candidates("OMO")

    assert candidates[0] == "OMOA"
    assert all(len(candidate) == 4 for candidate in candidates)
    assert len(candidates) == len(set(candidates))