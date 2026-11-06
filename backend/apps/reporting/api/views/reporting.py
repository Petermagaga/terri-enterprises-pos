
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOwner
from apps.reporting.api.serializers import (
    DateRangeQuerySerializer,
    SalesSummaryQuerySerializer,
)
from apps.reporting.services.date_ranges import get_date_range
from apps.reporting.services.profit_loss import calculate_profit_loss
from apps.reporting.services.product_profitability import (
    calculate_product_profitability,
)
from apps.reporting.services.payment_summary import calculate_payment_summary
from apps.reporting.services.sales_summary import calculate_sales_summary


class BaseReportingAPIView(APIView):
    """
    Shared behavior for owner-only reporting endpoints.
    """

    permission_classes = [IsAuthenticated, IsOwner]
    query_serializer_class = DateRangeQuerySerializer

    def get_report(self, date_range, query_data):
        raise NotImplementedError(
            "Reporting views must implement get_report()."
        )

    def get(self, request, *args, **kwargs):
        query_serializer = self.query_serializer_class(
            data=request.query_params,
        )
        query_serializer.is_valid(raise_exception=True)

        query_data = query_serializer.validated_data

        try:
            date_range = get_date_range(
                preset=query_data["preset"],
                start_date=query_data.get("start_date"),
                end_date=query_data.get("end_date"),
            )

            report_data = self.get_report(date_range, query_data)

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            ) from exc

        return Response({
            "date_range": {
                "start_date": date_range.start_date,
                "end_date": date_range.end_date,
            },
            "data": report_data,
        })


class ProfitLossReportView(BaseReportingAPIView):

    def get_report(self, date_range, query_data):
        return calculate_profit_loss(date_range)


class ProductProfitabilityReportView(BaseReportingAPIView):

    def get_report(self, date_range, query_data):
        return calculate_product_profitability(date_range)


class PaymentSummaryReportView(BaseReportingAPIView):

    def get_report(self, date_range, query_data):
        return calculate_payment_summary(date_range)


class SalesSummaryReportView(BaseReportingAPIView):
    query_serializer_class = SalesSummaryQuerySerializer

    def get_report(self, date_range, query_data):
        return calculate_sales_summary(
            date_range=date_range,
            group_by=query_data["group_by"],
        )
