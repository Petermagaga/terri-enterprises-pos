from rest_framework import mixins, viewsets

from apps.accounts.permissions import IsOwner
from apps.inventory.api.serializers import PurchaseSerializer
from apps.inventory.models import Purchase


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