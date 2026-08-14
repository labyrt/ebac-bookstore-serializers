from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


class PaginationTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            title="Backend",
            slug="backend-pagination",
            description="Categoria usada nos testes de paginação",
        )

        for index in range(7):
            product = Product.objects.create(
                title=f"Livro {index + 1}",
                description="Produto para validar a paginação da API",
                price=50 + index,
                active=True,
            )
            product.category.add(self.category)

    def test_product_list_is_paginated(self):
        response = self.client.get(reverse("product-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 7)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_second_page_returns_remaining_products(self):
        response = self.client.get(reverse("product-list"), {"page": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 7)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_debug_toolbar_is_configured_for_local_development(self):
        self.assertIn("debug_toolbar", settings.INSTALLED_APPS)
        self.assertIn(
            "debug_toolbar.middleware.DebugToolbarMiddleware",
            settings.MIDDLEWARE,
        )
        self.assertIn("127.0.0.1", settings.INTERNAL_IPS)
