from django.urls import path

from apps.accounts.api.views.auth import (
    LoginView,
    LogoutView,
    CurrentUserView,
)

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),
]