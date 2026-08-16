from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from product.models import Product
from product.serializers import ProductSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all().prefetch_related("category").order_by("id")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
