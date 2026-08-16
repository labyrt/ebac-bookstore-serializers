from rest_framework.routers import DefaultRouter

from .viewsets import OrderViewSet


router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = router.urls
