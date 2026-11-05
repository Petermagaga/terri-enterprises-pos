from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsOwner
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

    permission_classes = [IsAuthenticated, IsOwner]