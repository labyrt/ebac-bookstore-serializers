from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from product.models import Category, Product

from .models import Order


class OrderViewSetTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="lucy",
            password="senha-segura",
        )
        self.category = Category.objects.create(
            title="Backend",
            slug="backend",
        )
        self.product = Product.objects.create(
            title="Django",
            description="Livro sobre Django",
            price=100,
        )
        self.product.category.add(self.category)

    def test_order_viewset_supports_crud(self):
        create_response = self.client.post(
            reverse("order-list"),
            {
                "user": self.user.pk,
                "product_ids": [self.product.pk],
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        order_id = create_response.data["id"]
        detail_url = reverse("order-detail", args=[order_id])

        retrieve_response = self.client.get(detail_url)
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["user"], self.user.pk)
        self.assertEqual(retrieve_response.data["total"], 100)

        second_product = Product.objects.create(
            title="APIs REST",
            description="Livro sobre APIs",
            price=80,
        )
        second_product.category.add(self.category)

        update_response = self.client.patch(
            detail_url,
            {"product_ids": [self.product.pk, second_product.pk]},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["total"], 180)

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=order_id).exists())

    def test_order_routes_are_available(self):
        response = self.client.get(reverse("order-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
