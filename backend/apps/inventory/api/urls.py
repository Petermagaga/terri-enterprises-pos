from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.inventory.api.views import (
    ProductPackagingViewSet,
    PurchaseViewSet,
    PurchaseItemViewSet,
    StockBalanceViewSet,
    StockMovementViewSet,
    StockAdjustmentView
)


router = DefaultRouter()

router.register(
    "packaging",
    ProductPackagingViewSet,
    basename="inventory-packaging",
)

router.register(
    "purchases",
    PurchaseViewSet,
    basename="inventory-purchase",
)

router.register(
    "purchase-items",
    PurchaseItemViewSet,
    basename="inventory-purchase-item",
)

router.register(
    "stock-balances",
    StockBalanceViewSet,
    basename="inventory-stock-balance",
)

router.register(
    "stock-movements",
    StockMovementViewSet,
    basename="inventory-stock-movement",
)


urlpatterns = [
    path(
        "stock-adjustments/",
        StockAdjustmentView.as_view(),
        name="inventory-stock-adjustment",
    ),
    *router.urls,
]
