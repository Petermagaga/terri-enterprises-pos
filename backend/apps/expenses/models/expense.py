
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Expense(models.Model):

    class ExpenseType(models.TextChoices):
        SETUP = "SETUP", "Setup Cost"
        OPERATING = "OPERATING", "Operating Cost"
        CAPITAL = "CAPITAL", "Capital Expense"

    class Category(models.TextChoices):

    # Setup Costs
        BUSINESS_REGISTRATION = "BUSINESS_REGISTRATION", "Business Registration"
        LICENSES_PERMITS = "LICENSES_PERMITS", "Licenses & Permits"
        INITIAL_RENT_DEPOSIT = "INITIAL_RENT_DEPOSIT", "Initial Rent Deposit"
        SHOP_RENOVATION = "SHOP_RENOVATION", "Shop Renovation & Fittings"
        SHELVES_DISPLAY_SETUP = "SHELVES_DISPLAY_SETUP", "Shelves & Display Setup"
        REFRIGERATION_SETUP = "REFRIGERATION_SETUP", "Refrigerators & Freezers Setup"
        INITIAL_STOCK_ARRANGEMENT = "INITIAL_STOCK_ARRANGEMENT", "Initial Stock Arrangement"
        INITIAL_MARKETING = "INITIAL_MARKETING", "Initial Marketing & Branding"
        STAFF_TRAINING = "STAFF_TRAINING", "Staff Recruitment & Training"
        UTILITY_CONNECTIONS = "UTILITY_CONNECTIONS", "Utility Connections"

        # Operating Costs
        RENT = "RENT", "Rent"
        ELECTRICITY = "ELECTRICITY", "Electricity"
        WATER = "WATER", "Water"
        INTERNET = "INTERNET", "Internet"
        SALARIES_WAGES = "SALARIES_WAGES", "Salaries & Wages"
        FUEL_TRANSPORT = "FUEL_TRANSPORT", "Fuel & Transport"
        LOADING_OFFLOADING = "LOADING_OFFLOADING", "Loading & Offloading"
        MAINTENANCE_REPAIRS = "MAINTENANCE_REPAIRS", "Repairs & Maintenance"
        CLEANING = "CLEANING", "Cleaning & Sanitation"
        SECURITY = "SECURITY", "Security"
        MARKETING_ADVERTISING = "MARKETING_ADVERTISING", "Marketing & Advertising"
        INSURANCE = "INSURANCE", "Insurance"
        PACKAGING_MATERIALS = "PACKAGING_MATERIALS", "Packaging Materials"
        SHOP_SUPPLIES = "SHOP_SUPPLIES", "Shop Supplies"
        TELEPHONE_AIRTIME = "TELEPHONE_AIRTIME", "Telephone & Airtime"
        BANK_CHARGES = "BANK_CHARGES", "Bank & Transaction Charges"
        WASTE_COLLECTION = "WASTE_COLLECTION", "Waste Collection"
        MISCELLANEOUS = "MISCELLANEOUS", "Miscellaneous Expenses"

        # Capital Expenses
        LAND = "LAND", "Land"
        BUILDING = "BUILDING", "Building"
        MOTOR_VEHICLE = "MOTOR_VEHICLE", "Motor Vehicle"
        REFRIGERATORS_FREEZERS = "REFRIGERATORS_FREEZERS", "Refrigerators & Freezers"
        SHELVING_DISPLAY_EQUIPMENT = "SHELVING_DISPLAY_EQUIPMENT", "Shelving & Display Equipment"
        CHECKOUT_COUNTERS = "CHECKOUT_COUNTERS", "Checkout Counters"
        POS_EQUIPMENT = "POS_EQUIPMENT", "POS Machines & Equipment"
        COMPUTERS_LAPTOPS = "COMPUTERS_LAPTOPS", "Computers & Laptops"
        PRINTERS = "PRINTERS", "Printers"
        CCTV_SECURITY = "CCTV_SECURITY", "CCTV & Security Equipment"
        GENERATORS_BACKUP = "GENERATORS_BACKUP", "Generators & Power Backup"
        WEIGHING_SCALES = "WEIGHING_SCALES", "Weighing Scales"
        MACHINERY_EQUIPMENT = "MACHINERY_EQUIPMENT", "Machinery & Equipment"
        SOFTWARE_LICENSES = "SOFTWARE_LICENSES", "Software & Licenses"

        OTHER = "OTHER", "Other – Specify"


    class CostBehaviour(models.TextChoices):
        FIXED = "FIXED", "Fixed"
        VARIABLE = "VARIABLE", "Variable"
        SEMI_VARIABLE = "SEMI_VARIABLE", "Semi-Variable"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        MPESA = "MPESA", "M-Pesa"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
        CHEQUE = "CHEQUE", "Cheque"
        CREDIT_CARD = "CREDIT_CARD", "Credit Card"

    expense_type = models.CharField(
        max_length=20,
        choices=ExpenseType.choices,
        default=ExpenseType.OPERATING,
    )
    category = models.CharField(
        max_length=40,
        choices=Category.choices,
        default=Category.MISCELLANEOUS,
    )

    custom_category = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )
    cost_behaviour = models.CharField(
        max_length=20,
        choices=CostBehaviour.choices,
        default=CostBehaviour.VARIABLE,
    )
    description = models.CharField(max_length=255)
    payee = models.CharField(max_length=255, blank=True, default="")
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    expense_date = models.DateField(default=timezone.localdate)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )
    payment_reference = models.CharField(max_length=100, blank=True)
    is_recurring = models.BooleanField(default=False)

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="expenses_recorded",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-expense_date", "-created_at"]
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="expense_amount_positive",
            ),
            models.CheckConstraint(
                condition=(
                    Q(payment_method="CASH", payment_reference="")
                    | Q(
                        payment_method__in=["MPESA", "BANK_TRANSFER"],
                        payment_reference__gt="",
                    )
                    | Q(payment_method__in=["CHEQUE", "CREDIT_CARD"])
                ),
                name="expense_payment_reference_valid",
            ),
        ]


    def clean(self):
        errors = {}

        # Validate custom category
        if self.category == self.Category.OTHER:
            if not self.custom_category.strip():
                errors["custom_category"] = (
                    "Please specify the expense category."
                )
        elif self.custom_category.strip():
            errors["custom_category"] = (
                "Custom category should only be provided when "
                "Other – Specify is selected."
            )

        # Define categories allowed under each expense type
        setup_categories = {
            self.Category.BUSINESS_REGISTRATION,
            self.Category.LICENSES_PERMITS,
            self.Category.INITIAL_RENT_DEPOSIT,
            self.Category.SHOP_RENOVATION,
            self.Category.SHELVES_DISPLAY_SETUP,
            self.Category.REFRIGERATION_SETUP,
            self.Category.INITIAL_STOCK_ARRANGEMENT,
            self.Category.INITIAL_MARKETING,
            self.Category.STAFF_TRAINING,
            self.Category.UTILITY_CONNECTIONS,
        }

        operating_categories = {
            self.Category.RENT,
            self.Category.ELECTRICITY,
            self.Category.WATER,
            self.Category.INTERNET,
            self.Category.SALARIES_WAGES,
            self.Category.FUEL_TRANSPORT,
            self.Category.LOADING_OFFLOADING,
            self.Category.MAINTENANCE_REPAIRS,
            self.Category.CLEANING,
            self.Category.SECURITY,
            self.Category.MARKETING_ADVERTISING,
            self.Category.INSURANCE,
            self.Category.PACKAGING_MATERIALS,
            self.Category.SHOP_SUPPLIES,
            self.Category.TELEPHONE_AIRTIME,
            self.Category.BANK_CHARGES,
            self.Category.WASTE_COLLECTION,
            self.Category.MISCELLANEOUS,
        }

        capital_categories = {
            self.Category.LAND,
            self.Category.BUILDING,
            self.Category.MOTOR_VEHICLE,
            self.Category.REFRIGERATORS_FREEZERS,
            self.Category.SHELVING_DISPLAY_EQUIPMENT,
            self.Category.CHECKOUT_COUNTERS,
            self.Category.POS_EQUIPMENT,
            self.Category.COMPUTERS_LAPTOPS,
            self.Category.PRINTERS,
            self.Category.CCTV_SECURITY,
            self.Category.GENERATORS_BACKUP,
            self.Category.WEIGHING_SCALES,
            self.Category.MACHINERY_EQUIPMENT,
            self.Category.SOFTWARE_LICENSES,
        }

        allowed_categories = {
            self.ExpenseType.SETUP: setup_categories,
            self.ExpenseType.OPERATING: operating_categories,
            self.ExpenseType.CAPITAL: capital_categories,
        }

        if (
            self.category != self.Category.OTHER
            and self.category not in allowed_categories.get(
                self.expense_type, set()
            )
        ):
            errors["category"] = (
                "This category does not belong to the selected expense type."
            )

        # Validate payment reference
        if self.payment_method in [
            self.PaymentMethod.MPESA,
            self.PaymentMethod.BANK_TRANSFER,
        ] and not self.payment_reference.strip():
            errors["payment_reference"] = (
                "A transaction reference is required for M-Pesa "
                "and bank transfer payments."
            )

        if (
            self.payment_method == self.PaymentMethod.CASH
            and self.payment_reference.strip()
        ):
            errors["payment_reference"] = (
                "Cash expenses should not have a payment reference."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_category_display()} - KSh {self.amount}"
