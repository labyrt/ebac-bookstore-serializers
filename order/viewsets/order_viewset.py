from rest_framework.viewsets import ModelViewSet

from order.models import Order
from order.serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
    queryset = (
        Order.objects.all()
        .select_related("user")
        .prefetch_related("product", "product__category")
        .order_by("id")
    )
    serializer_class = OrderSerializer
