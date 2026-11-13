
from django.contrib import admin
from django.urls import include, path

from config.health import health_check


urlpatterns = [
    path("health/", health_check),
    path("admin/", admin.site.urls),
    path("api/", include("apps.accounts.api.urls")),
    path("api/", include("apps.products.api.urls")),
    path("api/", include("apps.suppliers.api.urls")),
    path("api/", include("apps.sales.api.urls")),
    path("api/", include("apps.expenses.api.urls")),
    path("api/", include("apps.reporting.api.urls")),
    path("api/", include("apps.dashboard.api.urls")),
    path("api/inventory/", include("apps.inventory.api.urls")),
]
