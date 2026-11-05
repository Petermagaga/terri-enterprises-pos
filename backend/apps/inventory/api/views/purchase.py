from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsOwner
from apps.inventory.api.serializers import PurchaseSerializer
from apps.inventory.models import Purchase
from apps.inventory.services.purchase_receiving import receive_purchase


class PurchaseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PurchaseSerializer

    queryset = Purchase.objects.select_related(
        "supplier",
        "created_by",
    ).all()

    permission_classes = [IsOwner]

    @action(
        detail=True,
        methods=["post"],
        url_path="receive",
    )
    def receive(self, request, pk=None):
        purchase = self.get_object()

        try:
            receive_purchase(purchase=purchase)

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc

        purchase.refresh_from_db()

        return Response(
            self.get_serializer(purchase).data,
            status=status.HTTP_200_OK,
        )