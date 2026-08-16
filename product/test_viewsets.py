from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


class ProductViewSetTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            title="Programação",
            slug="programacao",
            description="Livros de desenvolvimento",
        )

    def test_category_viewset_supports_crud(self):
        create_response = self.client.post(
            reverse("category-list"),
            {
                "title": "Banco de Dados",
                "slug": "banco-de-dados",
                "description": "Conteúdo sobre bancos de dados",
                "active": True,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        category_id = create_response.data["id"]
        detail_url = reverse("category-detail", args=[category_id])

        retrieve_response = self.client.get(detail_url)
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["slug"], "banco-de-dados")

        update_response = self.client.patch(
            detail_url,
            {"title": "Dados"},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["title"], "Dados")

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=category_id).exists())

    def test_product_viewset_supports_crud(self):
        create_response = self.client.post(
            reverse("product-list"),
            {
                "title": "Django REST Framework",
                "description": "Livro sobre APIs com Django",
                "price": 120,
                "active": True,
                "category_ids": [self.category.pk],
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        product_id = create_response.data["id"]
        detail_url = reverse("product-detail", args=[product_id])

        retrieve_response = self.client.get(detail_url)
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["title"], "Django REST Framework")
        self.assertEqual(retrieve_response.data["category"][0]["id"], self.category.pk)

        update_response = self.client.patch(
            detail_url,
            {"price": 150},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["price"], 150)

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(pk=product_id).exists())

    def test_product_routes_are_available(self):
        category_response = self.client.get(reverse("category-list"))
        product_response = self.client.get(reverse("product-list"))

        self.assertEqual(category_response.status_code, status.HTTP_200_OK)
        self.assertEqual(product_response.status_code, status.HTTP_200_OK)
