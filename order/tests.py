from django.contrib.auth import get_user_model
from django.test import TestCase

from product.models import Category, Product

from .models import Order
from .serializers import OrderSerializer


class OrderSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="lucy",
            password="senha-segura",
        )
        category = Category.objects.create(title="Backend", slug="backend")
        self.product = Product.objects.create(title="Django", price=100)
        self.product.category.add(category)

    def valid_data(self):
        return {
            "user": self.user.pk,
            "product_ids": [self.product.pk],
        }

    def test_accepts_valid_data(self):
        serializer = OrderSerializer(data=self.valid_data())

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_requires_user_and_products(self):
        serializer = OrderSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("user", serializer.errors)
        self.assertIn("product_ids", serializer.errors)

    def test_rejects_empty_or_unknown_product_list(self):
        empty_serializer = OrderSerializer(
            data={"user": self.user.pk, "product_ids": []}
        )
        unknown_serializer = OrderSerializer(
            data={"user": self.user.pk, "product_ids": [9999]}
        )

        self.assertFalse(empty_serializer.is_valid())
        self.assertFalse(unknown_serializer.is_valid())
        self.assertIn("product_ids", empty_serializer.errors)
        self.assertIn("product_ids", unknown_serializer.errors)

    def test_creates_order_with_product_relationship(self):
        serializer = OrderSerializer(data=self.valid_data())
        self.assertTrue(serializer.is_valid(), serializer.errors)

        order = serializer.save()

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.user, self.user)
        self.assertEqual(list(order.product.all()), [self.product])

    def test_returns_nested_products_expected_fields_and_total(self):
        second_product = Product.objects.create(title="REST", price=50)
        order = Order.objects.create(user=self.user)
        order.product.set([self.product, second_product])
        data = OrderSerializer(order).data

        self.assertEqual(set(data), {"id", "user", "products", "total"})
        self.assertEqual(len(data["products"]), 2)
        self.assertEqual(data["total"], 150)
        self.assertNotIn("product_ids", data)
