from django.test import TestCase

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategorySerializerTests(TestCase):
    def test_accepts_valid_data_and_creates_category(self):
        serializer = CategorySerializer(
            data={
                "title": "Livros",
                "slug": "livros",
                "description": "Livros físicos e digitais",
                "active": True,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        category = serializer.save()
        self.assertEqual(category.title, "Livros")
        self.assertEqual(Category.objects.count(), 1)

    def test_requires_title_and_slug(self):
        serializer = CategorySerializer(data={"description": "Sem identificação"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
        self.assertIn("slug", serializer.errors)

    def test_rejects_duplicate_slug(self):
        Category.objects.create(title="Livros", slug="livros")
        serializer = CategorySerializer(data={"title": "Outros", "slug": "livros"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("slug", serializer.errors)

    def test_returns_expected_fields(self):
        category = Category.objects.create(title="Tecnologia", slug="tecnologia")

        self.assertEqual(
            set(CategorySerializer(category).data),
            {"id", "title", "slug", "description", "active"},
        )


class ProductSerializerTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Python", slug="python")

    def valid_data(self):
        return {
            "title": "Django para APIs",
            "description": "Guia de desenvolvimento com Django REST Framework",
            "price": 120,
            "active": True,
            "category_ids": [self.category.pk],
        }

    def test_accepts_valid_data(self):
        serializer = ProductSerializer(data=self.valid_data())

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_requires_title_price_and_categories(self):
        serializer = ProductSerializer(data={"description": "Dados incompletos"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
        self.assertIn("price", serializer.errors)
        self.assertIn("category_ids", serializer.errors)

    def test_rejects_zero_price(self):
        data = self.valid_data()
        data["price"] = 0
        serializer = ProductSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_rejects_unknown_category(self):
        data = self.valid_data()
        data["category_ids"] = [9999]
        serializer = ProductSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("category_ids", serializer.errors)

    def test_creates_product_with_category_relationship(self):
        serializer = ProductSerializer(data=self.valid_data())
        self.assertTrue(serializer.is_valid(), serializer.errors)

        product = serializer.save()

        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(list(product.category.all()), [self.category])

    def test_represents_category_as_nested_data(self):
        product = Product.objects.create(title="Django", price=90)
        product.category.add(self.category)
        data = ProductSerializer(product).data

        self.assertEqual(
            set(data),
            {"id", "title", "description", "price", "active", "category"},
        )
        self.assertEqual(data["category"][0]["slug"], "python")
        self.assertNotIn("category_ids", data)
