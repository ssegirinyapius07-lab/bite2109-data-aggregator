import unittest
from unittest.mock import Mock, patch

import requests

from analyzer import analyze_products
from api_fetcher import fetch_product_data
from data_models import Product
from scraper import scrape_product_review


class TestProject(unittest.TestCase):

    def setUp(self):
        fetch_product_data.cache_clear()

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
        mock_response.status_code = 200
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

        products = fetch_product_data()

        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Test Product")
        self.assertEqual(products[0].price, 25.50)
        self.assertEqual(products[0].category, "test")

        mock_get.assert_called_once()

        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs["timeout"], 10)

    @patch("api_fetcher.requests.get")
    def test_api_rejects_404_and_500_without_returning_data(self, mock_get):
        for status_code in (404, 500):
            with self.subTest(status_code=status_code):
                fetch_product_data.cache_clear()

                mock_response = Mock()
                mock_response.status_code = status_code
                mock_get.return_value = mock_response

                products = fetch_product_data()

                self.assertEqual(products, [])
                mock_response.json.assert_not_called()

    @patch(
        "api_fetcher.requests.get",
        side_effect=requests.exceptions.Timeout("timed out"),
    )
    def test_api_timeout_returns_no_data(self, mock_get):
        products = fetch_product_data()

        self.assertEqual(products, [])
        mock_get.assert_called_once()

    @patch(
        "api_fetcher.requests.get",
        side_effect=requests.exceptions.ConnectionError("offline"),
    )
    def test_api_connection_failure_returns_no_data(self, mock_get):
        products = fetch_product_data()

        self.assertEqual(products, [])
        mock_get.assert_called_once()

    @patch("scraper.requests.get")
    def test_scraper_rejects_404_and_500_without_fabricating_reviews(
        self,
        mock_get,
    ):
        product = self.products[0]

        for status_code in (404, 500):
            with self.subTest(status_code=status_code):
                response = Mock()
                response.status_code = status_code
                mock_get.return_value = response

                result = scrape_product_review(product)

                self.assertIsNone(result)
                response.raise_for_status.assert_not_called()

    @patch(
        "scraper.requests.get",
        side_effect=requests.exceptions.Timeout("timed out"),
    )
    def test_scraper_timeout_returns_no_data(self, mock_get):
        result = scrape_product_review(self.products[0])

        self.assertIsNone(result)
        mock_get.assert_called_once()

    @patch("scraper.requests.get")
    def test_scraper_accepts_only_http_200(self, mock_get):
        response = Mock()
        response.status_code = 200
        response.text = """
        <html>
            <span class="average-score">4.7</span>
            <span class="review-count">25</span>
        </html>
        """
        mock_get.return_value = response

        result = scrape_product_review(self.products[0])

        self.assertIsNotNone(result)
        self.assertEqual(result.avg_score, 4.7)
        self.assertEqual(result.review_count, 25)

        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs["timeout"], 10)


if __name__ == "__main__":
    unittest.main()
