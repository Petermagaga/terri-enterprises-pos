from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOwnerOrCashier
from apps.inventory.api.serializers import StockAlertSerializer
from apps.inventory.models import StockAlert


class StockAlertListView(APIView):
    permission_classes = [IsOwnerOrCashier]

    def get(self, request):
        alerts = (
            StockAlert.objects
            .filter(resolved_at__isnull=True)
            .select_related("product")
            .order_by("-created_at")
        )

        unread_count = alerts.filter(is_read=False).count()

        return Response({
            "alerts": StockAlertSerializer(
                alerts,
                many=True,
            ).data,
            "unread_count": unread_count,
        })


class StockAlertMarkAllReadView(APIView):
    permission_classes = [IsOwnerOrCashier]

    @transaction.atomic
    def post(self, request):
        unread_alerts = StockAlert.objects.filter(
            resolved_at__isnull=True,
            is_read=False,
        )

        marked_count = unread_alerts.count()

        unread_alerts.update(
            is_read=True,
        )

        return Response({
            "marked_read": marked_count,
            "unread_count": 0,
        }, status=status.HTTP_200_OK)
