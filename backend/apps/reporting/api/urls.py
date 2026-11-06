
from django.urls import path

from apps.reporting.api.views import (
    ProfitLossReportView,
    ProductProfitabilityReportView,
    PaymentSummaryReportView,
    SalesSummaryReportView,
)


urlpatterns = [
    path(
        "reports/profit-loss/",
        ProfitLossReportView.as_view(),
        name="report-profit-loss",
    ),
    path(
        "reports/product-profitability/",
        ProductProfitabilityReportView.as_view(),
        name="report-product-profitability",
    ),
    path(
        "reports/payment-summary/",
        PaymentSummaryReportView.as_view(),
        name="report-payment-summary",
    ),
    path(
        "reports/sales-summary/",
        SalesSummaryReportView.as_view(),
        name="report-sales-summary",
    ),
]
