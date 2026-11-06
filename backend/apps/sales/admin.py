from django.contrib import admin

from apps.sales.models import Sale, SaleItem, SalePayment


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    can_delete = False
    readonly_fields = [
        "product",
        "product_name_snapshot",
        "product_sku_snapshot",
        "packaging_name_snapshot",
        "conversion_factor_snapshot",
        "pricing_type",
        "quantity",
        "selling_price_per_package",
        "total_amount",
        "total_cost",
    ]


class SalePaymentInline(admin.TabularInline):
    model = SalePayment
    extra = 0
    can_delete = False
    readonly_fields = [
        "payment_method",
        "amount",
        "reference",
        "received_by",
        "created_at",
    ]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = [
        "receipt_number",
        "processed_by",
        "status",
        "total_amount",
        "total_cost",
        "created_at",
    ]

    list_filter = ["status", "created_at"]
    search_fields = ["receipt_number", "processed_by__username"]

    readonly_fields = [
        "receipt_number",
        "total_amount",
        "total_cost",
        "created_at",
        "completed_at",
    ]

    inlines = [SaleItemInline, SalePaymentInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = [
        "product_name_snapshot",
        "sale",
        "quantity",
        "total_amount",
        "total_cost",
    ]

    readonly_fields = [field.name for field in SaleItem._meta.fields]


@admin.register(SalePayment)
class SalePaymentAdmin(admin.ModelAdmin):
    list_display = [
        "sale",
        "payment_method",
        "amount",
        "reference",
        "received_by",
        "created_at",
    ]

    readonly_fields = [field.name for field in SalePayment._meta.fields]
    