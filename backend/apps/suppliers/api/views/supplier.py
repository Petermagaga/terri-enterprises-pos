from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsOwner
from apps.suppliers.api.serializers import SupplierSerializer
from apps.suppliers.models import Supplier


class SupplierViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Supplier management API.

    Only active business owners can view or manage suppliers.
    Suppliers cannot be permanently deleted.
    """

    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()

    permission_classes = [IsAuthenticated, IsOwner]