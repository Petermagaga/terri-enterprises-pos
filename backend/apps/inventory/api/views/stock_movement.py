from rest_framework import mixins, viewsets

from apps.accounts.permissions import IsOwnerOrCashier
from apps.inventory.api.serializers import StockMovementSerializer
from apps.inventory.models import StockMovement


class StockMovementViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = StockMovementSerializer

    queryset = StockMovement.objects.select_related(
        "product",
        "stock_batch",
        "created_by",
    ).all()

    permission_classes = [IsOwnerOrCashier]