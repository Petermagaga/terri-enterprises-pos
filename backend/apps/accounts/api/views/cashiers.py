
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from apps.accounts.api.serializers.cashiers import (
    CashierCreateSerializer,
    CashierPasswordResetSerializer,
    CashierUpdateSerializer,
    CashierSerializer,
    
)
from apps.accounts.models import User
from apps.accounts.permissions import IsOwner
from apps.accounts.services.cashiers import (
    reset_cashier_password,
    set_cashier_active_status,
    update_cashier,
)


class CashierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return User.objects.filter(role=User.Role.CASHIER).order_by("username")

    def get_serializer_class(self):
        if self.action == "create":
            return CashierCreateSerializer

        if self.action in ("update", "partial_update"):
            return CashierUpdateSerializer

        if self.action == "reset_password":
            return CashierPasswordResetSerializer

        return CashierSerializer

    def perform_update(self, serializer):
        cashier = self.get_object()
        data = serializer.validated_data.copy()

        is_active = data.pop("is_active", None)

        update_cashier(cashier, **data)

        if is_active is not None:
            set_cashier_active_status(cashier, is_active=is_active)

        serializer.instance = cashier

    def destroy(self, request, *args, **kwargs):
        cashier = self.get_object()

        set_cashier_active_status(cashier, is_active=False)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="reset-password")
    def reset_password(self, request, pk=None):
        cashier = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_cashier_password(
            cashier,
            password=serializer.validated_data["password"],
        )

        return Response(
            {"detail": "Cashier password reset successfully."},
            status=status.HTTP_200_OK,
        )
