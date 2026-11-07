from django.urls import path

from apps.dashboard.api.views import (
    OwnerDashboardView,
    CashierDashboardView,
)


urlpatterns = [
    path(
        "dashboard/owner/",
        OwnerDashboardView.as_view(),
        name="dashboard-owner",
    ),
    path(
        "dashboard/cashier/",
        CashierDashboardView.as_view(),
        name="dashboard-cashier",
    ),
]