from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOwnerOrCashier
from apps.dashboard.api.serializers import CashierDashboardSerializer
from apps.dashboard.services.cashier_summary import (
    get_cashier_dashboard_summary,
)


class CashierDashboardView(APIView):
    """
    Returns the authenticated cashier's dashboard summary.
    """

    permission_classes = [IsAuthenticated, IsOwnerOrCashier]

    def get(self, request):
        dashboard_data = get_cashier_dashboard_summary(
            cashier=request.user,
        )

        serializer = CashierDashboardSerializer(
            instance=dashboard_data,
        )

        return Response(serializer.data)