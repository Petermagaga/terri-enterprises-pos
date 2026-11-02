from rest_framework.routers import DefaultRouter

from apps.products.api.views import (
    CategoryViewSet,
    ProductFamilyViewSet,
    ProductViewSet,
)


router = DefaultRouter()

router.register("categories", CategoryViewSet, basename="category")
router.register("product-families", ProductFamilyViewSet, basename="product-family")
router.register("products", ProductViewSet, basename="product")


urlpatterns = router.urls