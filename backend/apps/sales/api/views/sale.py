from datetime import timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsOwnerOrCashier
from apps.sales.api.serializers import (
    SaleSerializer,
    AddSaleItemSerializer,
    AddSalePaymentSerializer,
)
from apps.sales.models import Sale
from apps.sales.services.sale_creation import (
    create_sale,
    add_sale_item,
)
from apps.sales.services.payment_creation import add_sale_payment
from apps.sales.services.sale_completion import complete_sale


class SaleViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrCashier]

    queryset = (
        Sale.objects
        .select_related("processed_by")
        .prefetch_related(
            "items__product",
            "items__packaging",
            "payments__received_by",
        )
    )

    def get_queryset(self):
        """
        Owners can access all sales.

        Cashiers can access only their own sales
        created within the last seven days.

        Draft sales are excluded from list responses,
        but remain accessible through detail endpoints.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == "OWNER":
            pass

        elif user.role == "CASHIER":
            seven_days_ago = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(
                processed_by=user,
                created_at__gte=seven_days_ago,
            )

        else:
            return queryset.none()

        if self.action == "list":
            queryset = queryset.exclude(
                status=Sale.Status.DRAFT
            )

        return queryset
    def create(self, request, *args, **kwargs):
        """
        Create a draft sale for the authenticated user.
        """

        try:
            sale = create_sale(
                processed_by=request.user,
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc

        return Response(
            self.get_serializer(sale).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="add-item",
    )
    def add_item(self, request, pk=None):
        sale = self.get_object()

        input_serializer = AddSaleItemSerializer(
            data=request.data,
        )
        input_serializer.is_valid(raise_exception=True)

        data = input_serializer.validated_data

        try:
            add_sale_item(
                sale=sale,
                product=data["product"],
                pricing_type=data["pricing_type"],
                quantity=data["quantity"],
                packaging=data.get("packaging"),
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc

        sale.refresh_from_db()

        return Response(
            self.get_serializer(sale).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="add-payment",
    )
    def add_payment(self, request, pk=None):
        sale = self.get_object()

        input_serializer = AddSalePaymentSerializer(
            data=request.data,
        )
        input_serializer.is_valid(raise_exception=True)

        data = input_serializer.validated_data

        try:
            add_sale_payment(
                sale=sale,
                payment_method=data["payment_method"],
                amount=data["amount"],
                received_by=request.user,
                reference=data.get("reference", ""),
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc

        sale.refresh_from_db()

        return Response(
            self.get_serializer(sale).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="complete",
    )
    def complete(self, request, pk=None):
        sale = self.get_object()

        try:
            complete_sale(sale=sale)

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc

        sale.refresh_from_db()

        return Response(
            self.get_serializer(sale).data,
            status=status.HTTP_200_OK,
        )