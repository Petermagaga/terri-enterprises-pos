import re
from decimal import Decimal, InvalidOperation
from itertools import product as cartesian_product
from string import ascii_uppercase

from django.core.exceptions import ValidationError
from django.db import connection, transaction

from apps.products.models import ProductFamily


def normalize_family_name(name):
    """Convert a family name into uppercase letters only."""
    return re.sub(r"[^A-Z]", "", name.upper())


def generate_prefix_candidates(name):
    letters = normalize_family_name(name)

    if not letters:
        raise ValidationError(
            "Product family names must contain at least one letter."
        )

    candidates = []

    # Short names are padded with letters to produce four-letter prefixes.
    if len(letters) < 4:
        for suffix in cartesian_product(
            ascii_uppercase,
            repeat=4 - len(letters),
        ):
            candidates.append(letters + "".join(suffix))
        return candidates

    first_candidate = letters[:4]
    candidates.append(first_candidate)

    for index in range(4, len(letters)):
        candidate = letters[:3] + letters[index]
        if candidate not in candidates:
            candidates.append(candidate)

    for first in range(len(letters)):
        for second in range(first + 1, len(letters)):
            for third in range(second + 1, len(letters)):
                for fourth in range(third + 1, len(letters)):
                    candidate = (
                        letters[first] + letters[second]
                        + letters[third] + letters[fourth]
                    )
                    if candidate not in candidates:
                        candidates.append(candidate)

    return candidates

@transaction.atomic
def assign_family_prefix(family):
    """
    Allocate a permanent, unique four-letter prefix.

    PostgreSQL advisory locking serializes allocations across
    different families, including when no prefixes exist yet.
    """
    if family.pk is None:
        raise ValidationError(
            "Save the product family before assigning its SKU prefix."
        )

    if connection.vendor != "postgresql":
        raise RuntimeError(
            "SKU prefix allocation requires PostgreSQL."
        )

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT pg_advisory_xact_lock(%s, %s)",
            [73521, 1],
        )

    locked_family = ProductFamily.objects.select_for_update().get(
        pk=family.pk
    )

    if locked_family.sku_prefix:
        return locked_family.sku_prefix

    candidates = generate_prefix_candidates(locked_family.name)

    used_prefixes = set(
        ProductFamily.objects.exclude(sku_prefix__isnull=True)
        .values_list("sku_prefix", flat=True)
    )

    # Try family-related candidates first.
    for candidate in candidates:
        if candidate not in used_prefixes:
            locked_family.sku_prefix = candidate
            locked_family.save(
                update_fields=["sku_prefix", "updated_at"]
            )
            return candidate

    # Exhaustively search the four-letter alphabet if necessary.
    for letters in cartesian_product(ascii_uppercase, repeat=4):
        candidate = "".join(letters)

        if candidate not in used_prefixes:
            locked_family.sku_prefix = candidate
            locked_family.save(
                update_fields=["sku_prefix", "updated_at"]
            )
            return candidate

    raise ValidationError("All available four-letter SKU prefixes are used.")


def format_size_for_sku(size_value, size_unit):
    """Format whole and fractional product sizes for SKUs."""
    try:
        size = Decimal(str(size_value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Invalid product size.")

    if not size.is_finite() or size <= 0:
        raise ValidationError("Product size must be greater than zero.")

    unit = size_unit.upper()

    if unit not in ("G", "KG", "ML", "L"):
        raise ValidationError("Unsupported product size unit.")

    normalized_size = format(size.normalize(), "f")

    if "." in normalized_size:
        numeric_part = normalized_size.replace(".", "P")
    else:
        numeric_part = normalized_size.zfill(3)

    return f"{numeric_part}{unit}"


def generate_product_sku(family, size_value, size_unit):
    """Generate a SKU from a family's permanent prefix and product size."""
    size_suffix = format_size_for_sku(size_value, size_unit)
    prefix = assign_family_prefix(family)

    return f"{prefix}-{size_suffix}"