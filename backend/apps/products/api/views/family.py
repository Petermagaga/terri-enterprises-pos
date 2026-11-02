from rest_framework import mixins, viewsets

from apps.accounts.permissions import IsOwner, IsOwnerOrCashier
from apps.products.api.serializers import ProductFamilySerializer
from apps.products.models import ProductFamily


class ProductFamilyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProductFamilySerializer
    queryset = ProductFamily.objects.all()

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            permission_classes = [IsOwnerOrCashier]
        elif self.action in ("create", "update", "partial_update"):
            permission_classes = [IsOwner]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]