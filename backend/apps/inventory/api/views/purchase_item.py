
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounts.permissions import IsOwner
from apps.inventory.api.serializers import PurchaseItemSerializer
from apps.inventory.models import PurchaseItem
from apps.inventory.services.purchase_item_removal import (
    remove_purchase_item,
)


class PurchaseItemViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PurchaseItemSerializer

    queryset = PurchaseItem.objects.select_related(
        "purchase",
        "product",
        "packaging",
    ).all()

    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super().get_queryset()

        purchase_id = self.request.query_params.get("purchase")

        if purchase_id is not None:
            queryset = queryset.filter(purchase_id=purchase_id)

        return queryset

    def destroy(self, request, *args, **kwargs):
        purchase_item = self.get_object()

        try:
            remove_purchase_item(purchase_item=purchase_item)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)

        return Response(status=status.HTTP_204_NO_CONTENT)
