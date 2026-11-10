from rest_framework import mixins, viewsets

from apps.accounts.permissions import IsOwner
from apps.inventory.api.serializers import PurchaseItemSerializer
from apps.inventory.models import PurchaseItem


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