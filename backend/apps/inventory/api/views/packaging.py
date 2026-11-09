from rest_framework import mixins, viewsets

from apps.accounts.permissions import IsOwner, IsOwnerOrCashier
from apps.inventory.api.serializers import ProductPackagingSerializer
from apps.inventory.models import ProductPackaging


class ProductPackagingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProductPackagingSerializer

    queryset = ProductPackaging.objects.select_related(
        "product",
    ).all()

    def get_queryset(self):
        queryset = super().get_queryset()

        product_id = self.request.query_params.get("product")

        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)

        return queryset

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            permission_classes = [IsOwnerOrCashier]
        else:
            permission_classes = [IsOwner]

        return [permission() for permission in permission_classes]