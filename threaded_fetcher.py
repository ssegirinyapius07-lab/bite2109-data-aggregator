from concurrent.futures import ThreadPoolExecutor

from api_fetcher import fetch_product_data
from scraper import scrape_product_review


def fetch_all_threaded():
    """Fetch API products and scrape their review pages concurrently."""

    products = fetch_product_data()

    with ThreadPoolExecutor(max_workers=10) as executor:
        reviewed_products = list(
            executor.map(scrape_product_review, products)
        )

    return reviewed_products
