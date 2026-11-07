from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOwner
from apps.dashboard.api.serializers import OwnerDashboardSerializer
from apps.dashboard.services.owner_summary import (
    get_owner_dashboard_summary,
)


class OwnerDashboardView(APIView):
    """
    Returns the business owner's dashboard summary.
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        dashboard_data = get_owner_dashboard_summary()

        serializer = OwnerDashboardSerializer(
            instance=dashboard_data,
        )

        return Response(serializer.data)