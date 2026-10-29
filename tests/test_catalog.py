from django.test import TestCase
from rest_framework.test import APIClient

from ecommerce.models import Category, Product


class PublicCatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Review connectors", slug="review-connectors")
        cls.product = Product.objects.create(
            name="Synthetic connector", description="Local test record",
            price="125000.00", category=cls.category,
        )

    def setUp(self):
        self.client = APIClient()

    def test_anonymous_reader_can_browse_catalog(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["name"], self.product.name)
        categories = self.client.get("/api/categories/", {"slug": self.category.slug})
        self.assertEqual(categories.status_code, 200)
        self.assertEqual(categories.json()[0]["id"], self.category.id)

    def test_invalid_category_filter_has_no_results(self):
        response = self.client.get("/api/products/", {"category_id": "invalid"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_anonymous_reader_cannot_create_catalog_records(self):
        product = self.client.post("/api/products/", {
            "name": "Unauthorized connector", "description": "must not persist",
            "price": "1.00", "category_id": self.category.id,
        }, format="json")
        category = self.client.post("/api/categories/", {"name": "Unauthorized category"}, format="json")
        self.assertEqual(product.status_code, 403)
        self.assertEqual(category.status_code, 403)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Category.objects.count(), 1)
