from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Product


class ProductAPITests(TestCase):
    fixtures = ["products.json"]

    def test_list_returns_all_original_products_in_order(self):
        response = self.client.get(reverse("products:product-list"), HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 200)
        products = response.json()
        self.assertEqual(len(products), 20)
        self.assertEqual([product["id"] for product in products], list(range(1, 21)))
        self.assertEqual(products[0], {
            "id": 1, "name": "Wireless Mouse", "category": "Electronics",
            "description": "A compact wireless mouse for everyday computer use.",
            "price": "399.00", "stock": 25,
        })

    def test_detail_and_missing_product(self):
        response = self.client.get(reverse("products:product-detail", args=[20]))
        self.assertEqual(response.json()["name"], "Wired Earphones")
        response = self.client.get(reverse("products:product-detail", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_browsable_api_and_json_format(self):
        url = reverse("products:product-list")
        response = self.client.get(url, HTTP_ACCEPT="text/html")
        self.assertContains(response, "Wireless Mouse")
        self.assertContains(response, "rest_framework/css/bootstrap.min.css")
        self.assertEqual(self.client.get(url + "?format=json").headers["Content-Type"], "application/json")

    def test_api_is_read_only_even_for_admin(self):
        admin = User.objects.create_superuser(username="tester", password="TestOnly!Pass123")
        for user in [None, admin]:
            if user:
                self.client.force_login(user)
            for name, args in [("product-list", []), ("product-detail", [1])]:
                url = reverse(f"products:{name}", args=args)
                for method in ["post", "put", "patch", "delete"]:
                    with self.subTest(user=user, url=url, method=method):
                        response = getattr(self.client, method)(url, {}, content_type="application/json")
                        self.assertEqual(response.status_code, 405)
        self.assertEqual(Product.objects.count(), 20)

    def test_admin_can_manage_products(self):
        self.client.force_login(User.objects.create_superuser(username="staff"))
        response = self.client.get(reverse("admin:products_product_changelist"))
        self.assertContains(response, "Wireless Mouse")
        response = self.client.post(reverse("admin:products_product_add"), {
            "name": "Sample", "category": "Test", "description": "New product",
            "price": "10.00", "stock": 2, "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name="Sample").exists())


class SeedProductsTests(TestCase):
    def test_seed_is_repeatable_and_preserves_edits(self):
        call_command("seed_products", stdout=StringIO())
        Product.objects.filter(pk=1).update(name="Edited product")
        call_command("seed_products", stdout=StringIO())
        self.assertEqual(Product.objects.count(), 20)
        self.assertEqual(Product.objects.get(pk=1).name, "Edited product")
