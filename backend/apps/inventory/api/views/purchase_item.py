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