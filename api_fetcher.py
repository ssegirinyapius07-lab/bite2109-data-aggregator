import requests
from functools import lru_cache

from config import API_URL, REQUEST_TIMEOUT, MAX_PRODUCTS
from data_models import Product
from offline_data import OFFLINE_PRODUCTS


def create_products(product_data):
    """Convert raw product dictionaries into Product objects."""
    return [
        Product(
            id=int(item["id"]),
            name=item["title"],
            price=float(item["price"]),
            category=item["category"],
        )
        for item in product_data
    ]


@lru_cache(maxsize=32)
def fetch_product_data():
    """Fetch product data from the API with an offline fallback."""

    try:
        response = requests.get(
            API_URL,
            params={"limit": MAX_PRODUCTS},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        data = response.json()

        return create_products(data.get("products", []))

    except (
        requests.exceptions.RequestException,
        requests.exceptions.Timeout,
    ) as error:
        print(f"API unavailable. Using offline data: {error}")

        return create_products(OFFLINE_PRODUCTS[:MAX_PRODUCTS])

    except (KeyError, TypeError, ValueError) as error:
        print(f"Invalid API data. Using offline data: {error}")

        return create_products(OFFLINE_PRODUCTS[:MAX_PRODUCTS])