import unittest
from unittest.mock import patch, Mock

from analyzer import analyze_products
from api_fetcher import fetch_product_data
from data_models import Product


class TestProject(unittest.TestCase):

    def setUp(self):
        self.products = [
            Product(1, "Product A", 10.0, "books", 4.2, 10),
            Product(2, "Product B", 30.0, "books", 4.8, 20),
            Product(3, "Product C", 20.0, "food", 4.5, 15),
            Product(4, "Product D", 40.0, "food", 4.9, 25),
            Product(5, "Product E", 50.0, "books", 4.7, 5),
            Product(6, "No Reviews", 100.0, "books", 0.0, 0),
        ]

    def test_product_count_excludes_products_without_reviews(self):
        result = analyze_products(self.products)

        self.assertEqual(result["total_products"], 5)

    def test_average_price_by_category(self):
        result = analyze_products(self.products)

        self.assertEqual(
            result["average_price_by_category"]["books"],
            30.0,
        )

        self.assertEqual(
            result["average_price_by_category"]["food"],
            30.0,
        )

    def test_top_five_highest_rated_products(self):
        result = analyze_products(self.products)

        top_products = result["top_products"]

        self.assertEqual(len(top_products), 5)
        self.assertEqual(top_products[0].name, "Product D")
        self.assertEqual(top_products[0].avg_score, 4.9)

    def test_product_uses_slots(self):
        self.assertTrue(hasattr(Product, "__slots__"))
        self.assertFalse(hasattr(self.products[0], "__dict__"))

    @patch("api_fetcher.requests.get")
    def test_api_fetcher_with_mock_network_call(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "products": [
                {
                    "id": 1,
                    "title": "Test Product",
                    "price": 25.50,
                    "category": "test",
                }
            ]
        }

        mock_get.return_value = mock_response

        fetch_product_data.cache_clear()

        products = fetch_product_data()

        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Test Product")
        self.assertEqual(products[0].price, 25.50)
        self.assertEqual(products[0].category, "test")

        mock_get.assert_called_once()


if __name__ == "__main__":
    unittest.main()