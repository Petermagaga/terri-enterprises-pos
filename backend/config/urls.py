
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.products.api.urls")),
    path("api/", include("apps.suppliers.api.urls")),
    path("api/", include("apps.sales.api.urls")),
    path("api/", include("apps.expenses.api.urls")),
    path("api/", include("apps.reporting.api.urls")),
    path("api/", include("apps.dashboard.api.urls")),
    path("api/inventory/", include("apps.inventory.api.urls")),
]
