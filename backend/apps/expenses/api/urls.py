from rest_framework.routers import DefaultRouter

from apps.expenses.api.views import ExpenseViewSet


router = DefaultRouter()

router.register(
    "expenses",
    ExpenseViewSet,
    basename="expense",
)

urlpatterns = router.urls