
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOwner
from apps.dashboard.api.serializers import (
    OwnerDashboardQuerySerializer,
    OwnerDashboardSerializer,
)
from apps.dashboard.services.owner_summary import (
    get_owner_dashboard_summary,
)


class OwnerDashboardView(APIView):
    """
    Returns the business owner's dashboard summary.
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        query_serializer = OwnerDashboardQuerySerializer(
            data=request.query_params,
        )
        query_serializer.is_valid(raise_exception=True)

        query_data = query_serializer.validated_data

        try:
            dashboard_data = get_owner_dashboard_summary(
                period=query_data["period"],
                start_date=query_data.get("start_date"),
                end_date=query_data.get("end_date"),
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc

        serializer = OwnerDashboardSerializer(
            instance=dashboard_data,
        )

        return Response(serializer.data)
