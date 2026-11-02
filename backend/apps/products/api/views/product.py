
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsOwner, IsOwnerOrCashier
from apps.products.api.serializers import ProductSerializer
from apps.products.models import Product


class ProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Product catalogue API.

    Owners can manage products.
    Owners and cashiers can view the catalogue.
    Products cannot be permanently deleted through this API.
    """

    serializer_class = ProductSerializer
    queryset = Product.objects.select_related(
        "product_family",
        "category",
    ).all()

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            permission_classes = [IsOwnerOrCashier]
        elif self.action in ("create", "update", "partial_update"):
            permission_classes = [IsOwner]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
