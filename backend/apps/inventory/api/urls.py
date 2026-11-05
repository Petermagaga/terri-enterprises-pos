from rest_framework.routers import DefaultRouter

from apps.inventory.api.views import (
    ProductPackagingViewSet,
    PurchaseViewSet,
    PurchaseItemViewSet,
    StockBalanceViewSet,
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

urlpatterns = router.urls