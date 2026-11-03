from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.products.api.urls")),
    path("api/", include("apps.suppliers.api.urls")),
]