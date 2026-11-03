import pytest
from django.core.exceptions import ValidationError

from apps.suppliers.models import Supplier


@pytest.mark.django_db
def test_supplier_can_be_created():
    supplier = Supplier(
        name="ABC Distributors",
        phone="0712345678",
    )

    supplier.full_clean()
    supplier.save()

    assert supplier.pk is not None
    assert supplier.name == "ABC Distributors"
    assert supplier.is_active is True


@pytest.mark.django_db
def test_supplier_name_is_trimmed():
    supplier = Supplier(
        name="  ABC Distributors  ",
        phone="  0712345678  ",
    )

    supplier.full_clean()

    assert supplier.name == "ABC Distributors"
    assert supplier.phone == "0712345678"


@pytest.mark.django_db
def test_supplier_name_cannot_be_blank():
    supplier = Supplier(
        name="   ",
        phone="0712345678",
    )

    with pytest.raises(ValidationError):
        supplier.full_clean()


@pytest.mark.django_db
def test_supplier_phone_cannot_be_blank():
    supplier = Supplier(
        name="ABC Distributors",
        phone="   ",
    )

    with pytest.raises(ValidationError):
        supplier.full_clean()


@pytest.mark.django_db
def test_supplier_email_must_be_valid():
    supplier = Supplier(
        name="ABC Distributors",
        phone="0712345678",
        email="invalid-email",
    )

    with pytest.raises(ValidationError):
        supplier.full_clean()


@pytest.mark.django_db
def test_supplier_can_have_optional_contact_details():
    supplier = Supplier(
        name="ABC Distributors",
        phone="0712345678",
    )

    supplier.full_clean()

    assert supplier.contact_person == ""
    assert supplier.email == ""
    assert supplier.address == ""
    assert supplier.notes == ""


@pytest.mark.django_db
def test_supplier_can_be_deactivated():
    supplier = Supplier.objects.create(
        name="ABC Distributors",
        phone="0712345678",
        is_active=False,
    )

    assert supplier.is_active is False


@pytest.mark.django_db
def test_supplier_names_do_not_have_to_be_unique():
    Supplier.objects.create(
        name="ABC Distributors",
        phone="0711111111",
    )

    Supplier.objects.create(
        name="ABC Distributors",
        phone="0722222222",
    )

    assert Supplier.objects.filter(
        name="ABC Distributors"
    ).count() == 2