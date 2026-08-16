from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from product.models import Category, Product

from .models import Order


class OrderViewSetTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="lucy",
            password="senha-segura",
        )
        self.token = Token.objects.create(user=self.user)
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

    def authenticate(self, token=None):
        token = token or self.token
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_order_list_requires_token_authentication(self):
        response = self.client.get(reverse("order-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_viewset_supports_crud_with_token(self):
        self.authenticate()

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

    def test_user_can_only_list_own_orders(self):
        own_order = Order.objects.create(user=self.user)
        own_order.product.add(self.product)

        other_user = get_user_model().objects.create_user(
            username="outro-usuario",
            password="outra-senha",
        )
        other_order = Order.objects.create(user=other_user)
        other_order.product.add(self.product)

        self.authenticate()
        response = self.client.get(reverse("order-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(returned_ids, {own_order.pk})
        self.assertNotIn(other_order.pk, returned_ids)

    def test_user_cannot_retrieve_another_users_order(self):
        other_user = get_user_model().objects.create_user(
            username="maria",
            password="outra-senha",
        )
        other_token = Token.objects.create(user=other_user)
        order = Order.objects.create(user=self.user)
        order.product.add(self.product)

        self.authenticate(other_token)
        response = self.client.get(reverse("order-detail", args=[order.pk]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_order_routes_are_available(self):
        self.authenticate()
        response = self.client.get(reverse("order-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
