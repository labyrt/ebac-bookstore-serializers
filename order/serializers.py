from rest_framework import serializers

from product.models import Product
from product.serializers import ProductSerializer

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    products = ProductSerializer(source="product", many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        source="product",
        many=True,
        queryset=Product.objects.all(),
        write_only=True,
        allow_empty=False,
    )
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user", "products", "product_ids", "total"]
        read_only_fields = ["id", "total"]

    def get_total(self, instance):
        return sum(product.price or 0 for product in instance.product.all())

    def create(self, validated_data):
        products = validated_data.pop("product")
        order = Order.objects.create(**validated_data)
        order.product.set(products)
        return order

    def update(self, instance, validated_data):
        products = validated_data.pop("product", None)
        instance = super().update(instance, validated_data)
        if products is not None:
            instance.product.set(products)
        return instance
