from rest_framework.routers import DefaultRouter

from apps.inventory.api.views import (
    ProductPackagingViewSet,
    PurchaseViewSet,
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

urlpatterns = router.urls