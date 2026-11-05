from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOwner
from apps.inventory.api.serializers import (
    StockAdjustmentSerializer,
    StockAdjustmentMovementSerializer,
)
from apps.inventory.services.stock_adjustment import adjust_stock


class StockAdjustmentView(APIView):
    permission_classes = [IsOwner]

    def post(self, request):
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            result = adjust_stock(
                product=data["product"],
                quantity=data["quantity"],
                movement_type=data["movement_type"],
                created_by=request.user,
                reason=data["reason"],
                unit_cost=data.get("unit_cost"),
                reference=data.get("reference", ""),
            )

        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                raise ValidationError(exc.message_dict)

            raise ValidationError(exc.messages)

        if "movement" in result:
            movements = [result["movement"]]
        else:
            movement_ids = [
                deduction["movement_id"]
                for deduction in result["deductions"]
            ]

            from apps.inventory.models import StockMovement

            movements = list(
                StockMovement.objects.filter(
                    pk__in=movement_ids
                ).select_related(
                    "product",
                    "stock_batch",
                    "created_by",
                ).order_by("created_at", "id")
            )

        response_data = {
            "movement_type": result["movement_type"],
            "quantity": result["quantity"],
            "movements": StockAdjustmentMovementSerializer(
                movements,
                many=True,
            ).data,
        }

        if "batch" in result:
            response_data["batch_id"] = result["batch"].pk

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )