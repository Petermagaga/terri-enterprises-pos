from rest_framework import mixins, viewsets

from apps.accounts.permissions import IsOwner, IsOwnerOrCashier
from apps.products.api.serializers import CategorySerializer
from apps.products.models import Category


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            permission_classes = [IsOwnerOrCashier]
        elif self.action in ("create", "update", "partial_update"):
            permission_classes = [IsOwner]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]