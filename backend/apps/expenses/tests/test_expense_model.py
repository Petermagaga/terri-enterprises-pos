import pytest

from decimal import Decimal
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.expenses.models import Expense


pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    return User.objects.create_superuser(
        username="owner_expense",
        email="owner_expense@test.com",
        password="TestPassword123!",
    )


def test_create_cash_expense(owner):
    expense = Expense.objects.create(
        description="Shop rent",
        category=Expense.Category.RENT,
        amount=Decimal("15000.00"),
        payment_method=Expense.PaymentMethod.CASH,
        recorded_by=owner,
    )

    assert expense.amount == Decimal("15000.00")
    assert expense.payment_method == Expense.PaymentMethod.CASH
    assert expense.payment_reference == ""
    assert expense.recorded_by == owner


def test_create_mpesa_expense(owner):
    expense = Expense.objects.create(
        description="Electricity tokens",
        category=Expense.Category.ELECTRICITY,
        amount=Decimal("2500.00"),
        payment_method=Expense.PaymentMethod.MPESA,
        payment_reference="QWE123456",
        recorded_by=owner,
    )

    assert expense.payment_reference == "QWE123456"


def test_create_bank_expense(owner):
    expense = Expense.objects.create(
        description="Internet subscription",
        category=Expense.Category.INTERNET,
        amount=Decimal("3000.00"),
        payment_method=Expense.PaymentMethod.BANK_TRANSFER,
        payment_reference="BANK123456",
        recorded_by=owner,
    )

    assert expense.payment_method == Expense.PaymentMethod.BANK_TRANSFER

def test_mpesa_expense_requires_reference(owner):
    expense = Expense(
        description="Electricity tokens",
        category=Expense.Category.ELECTRICITY,
        amount=Decimal("2500.00"),
        payment_method=Expense.PaymentMethod.MPESA,
        recorded_by=owner,
    )

    with pytest.raises(ValidationError):
        expense.save()


def test_bank_expense_requires_reference(owner):
    expense = Expense(
        description="Internet subscription",
        category=Expense.Category.INTERNET,
        amount=Decimal("3000.00"),
        payment_method=Expense.PaymentMethod.BANK_TRANSFER,
        recorded_by=owner,
    )

    with pytest.raises(ValidationError):
        expense.save()


def test_cash_expense_rejects_reference(owner):
    expense = Expense(
        description="Shop rent",
        category=Expense.Category.RENT,
        amount=Decimal("15000.00"),
        payment_method=Expense.PaymentMethod.CASH,
        payment_reference="CASH123",
        recorded_by=owner,
    )

    with pytest.raises(ValidationError):
        expense.save()


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("0.00"),
        Decimal("-100.00"),
    ],
)
def test_expense_rejects_non_positive_amount(owner, amount):
    expense = Expense(
        description="Invalid expense",
        category=Expense.Category.MISCELLANEOUS,
        amount=amount,
        payment_method=Expense.PaymentMethod.CASH,
        recorded_by=owner,
    )

    with pytest.raises(ValidationError):
        expense.save()
@pytest.mark.parametrize(
    "expense_type, category",
    [
        (Expense.ExpenseType.SETUP, Expense.Category.BUSINESS_REGISTRATION),
        (Expense.ExpenseType.OPERATING, Expense.Category.RENT),
        (Expense.ExpenseType.CAPITAL, Expense.Category.POS_EQUIPMENT),
    ],
)
def test_expense_accepts_matching_type_and_category(
    owner, expense_type, category
):
    expense = Expense.objects.create(
        expense_type=expense_type,
        description="Valid expense",
        category=category,
        amount=Decimal("5000.00"),
        payment_method=Expense.PaymentMethod.CASH,
        recorded_by=owner,
    )

    assert expense.expense_type == expense_type
    assert expense.category == category


@pytest.mark.parametrize(
    "expense_type, category",
    [
        (Expense.ExpenseType.SETUP, Expense.Category.RENT),
        (Expense.ExpenseType.OPERATING, Expense.Category.POS_EQUIPMENT),
        (Expense.ExpenseType.CAPITAL, Expense.Category.ELECTRICITY),
    ],
)
def test_expense_rejects_category_from_another_type(
    owner, expense_type, category
):
    expense = Expense(
        expense_type=expense_type,
        description="Mismatched expense",
        category=category,
        amount=Decimal("5000.00"),
        payment_method=Expense.PaymentMethod.CASH,
        recorded_by=owner,
    )

    with pytest.raises(ValidationError):
        expense.save()


def test_other_category_requires_custom_category(owner):
    expense = Expense(
        expense_type=Expense.ExpenseType.OPERATING,
        description="Unspecified expense",
        category=Expense.Category.OTHER,
        amount=Decimal("1000.00"),
        payment_method=Expense.PaymentMethod.CASH,
        recorded_by=owner,
    )

    with pytest.raises(ValidationError):
        expense.save()


def test_other_category_accepts_custom_category(owner):
    expense = Expense.objects.create(
        expense_type=Expense.ExpenseType.OPERATING,
        description="Unspecified expense",
        category=Expense.Category.OTHER,
        custom_category="Pest control",
        amount=Decimal("1000.00"),
        payment_method=Expense.PaymentMethod.CASH,
        recorded_by=owner,
    )

    assert expense.custom_category == "Pest control"


def test_custom_category_rejected_for_standard_category(owner):
    expense = Expense(
        expense_type=Expense.ExpenseType.OPERATING,
        description="Shop rent",
        category=Expense.Category.RENT,
        custom_category="Pest control",
        amount=Decimal("15000.00"),
        payment_method=Expense.PaymentMethod.CASH,
        recorded_by=owner,
    )

    with pytest.raises(ValidationError):
        expense.save()


@pytest.mark.parametrize(
    "payment_method",
    [
        Expense.PaymentMethod.CHEQUE,
        Expense.PaymentMethod.CREDIT_CARD,
    ],
)
def test_optional_payment_reference_methods(owner, payment_method):
    expense = Expense.objects.create(
        description="Shop supplies",
        category=Expense.Category.SHOP_SUPPLIES,
        amount=Decimal("2000.00"),
        payment_method=payment_method,
        recorded_by=owner,
    )

    assert expense.payment_reference == ""


def test_recurring_expense_is_saved(owner):
    expense = Expense.objects.create(
        description="Monthly internet subscription",
        category=Expense.Category.INTERNET,
        amount=Decimal("3000.00"),
        payment_method=Expense.PaymentMethod.MPESA,
        payment_reference="MPESA123",
        is_recurring=True,
        recorded_by=owner,
    )

    assert expense.is_recurring is True


def test_expense_saves_additional_classification_fields(owner):
    expense = Expense.objects.create(
        expense_type=Expense.ExpenseType.OPERATING,
        category=Expense.Category.FUEL_TRANSPORT,
        cost_behaviour=Expense.CostBehaviour.SEMI_VARIABLE,
        description="Goods delivery transport",
        payee="ABC Transport Services",
        amount=Decimal("4500.00"),
        payment_method=Expense.PaymentMethod.CASH,
        is_recurring=False,
        recorded_by=owner,
    )

    assert expense.cost_behaviour == Expense.CostBehaviour.SEMI_VARIABLE
    assert expense.payee == "ABC Transport Services"
    assert expense.is_recurring is False
