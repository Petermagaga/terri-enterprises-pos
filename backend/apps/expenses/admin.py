from django.contrib import admin

from apps.expenses.models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "category",
        "amount",
        "payment_method",
        "expense_date",
        "recorded_by",
    ]

    list_filter = [
        "category",
        "payment_method",
        "expense_date",
    ]

    search_fields = [
        "description",
        "payment_reference",
        "recorded_by__username",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]

    ordering = ["-expense_date", "-created_at"]