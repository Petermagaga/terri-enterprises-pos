from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOwner
from apps.inventory.api.serializers import InventoryValuationSerializer
from apps.inventory.services.inventory_valuation import (
    get_inventory_valuation,
)


class InventoryValuationView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        valuation = get_inventory_valuation()
        serializer = InventoryValuationSerializer(valuation)

        return Response(serializer.data)
