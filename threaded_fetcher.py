from concurrent.futures import ThreadPoolExecutor

from api_fetcher import fetch_product_data
from scraper import scrape_product_review


def fetch_all_threaded():
    """Fetch API products and scrape successful review pages concurrently."""

    products = fetch_product_data()

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(scrape_product_review, products)
        reviewed_products = [product for product in results if product is not None]

    return reviewed_products
