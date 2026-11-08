from rest_framework import mixins, viewsets

from apps.accounts.permissions import IsOwnerOrCashier
from apps.inventory.api.serializers import StockBalanceSerializer
from apps.inventory.models import InventoryBalance


class StockBalanceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = StockBalanceSerializer

    queryset = InventoryBalance.objects.select_related(
        "product",
    ).order_by("pk")

    permission_classes = [IsOwnerOrCashier]