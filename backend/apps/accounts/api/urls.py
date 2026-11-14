
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.api.views.auth import (
    LoginView,
    LogoutView,
    CurrentUserView,
    AccountSettingsView
)
from apps.accounts.api.views.cashiers import CashierViewSet


router = DefaultRouter()
router.register("cashiers", CashierViewSet, basename="cashier")


urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),
    path("", include(router.urls)),
    path("auth/settings/", AccountSettingsView.as_view(), name="auth-settings"),
]
