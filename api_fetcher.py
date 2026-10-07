import requests
from functools import lru_cache

from config import API_URL, REQUEST_TIMEOUT, MAX_PRODUCTS
from data_models import Product


def create_products(product_data):
    """Convert valid raw product dictionaries into Product objects."""
    products = []

    for item in product_data:
        try:
            products.append(
                Product(
                    id=int(item["id"]),
                    name=item["title"],
                    price=float(item["price"]),
                    category=item["category"],
                )
            )
        except (KeyError, TypeError, ValueError) as error:
            print(f"Skipping invalid product data: {error}")

    return products


@lru_cache(maxsize=32)
def fetch_product_data():
    """Fetch product data; return data only when the API responds with HTTP 200."""

    try:
        response = requests.get(
            API_URL,
            params={"limit": MAX_PRODUCTS},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout as error:
        print(f"API request timed out after {REQUEST_TIMEOUT}s: {error}")
        return []
    except requests.exceptions.ConnectionError as error:
        print(f"Could not connect to API: {error}")
        return []
    except requests.exceptions.RequestException as error:
        print(f"API request failed: {error}")
        return []

    if response.status_code != 200:
        if response.status_code == 404:
            print("API returned HTTP 404 (Not Found). No product data returned.")
        elif response.status_code == 500:
            print("API returned HTTP 500 (Server Error). No product data returned.")
        else:
            print(
                f"API returned HTTP {response.status_code}. "
                "No product data returned."
            )
        return []

    try:
        data = response.json()
        product_data = data.get("products", [])

        if not isinstance(product_data, list):
            print("API returned an invalid products field. No product data returned.")
            return []

        return create_products(product_data)

    except (AttributeError, TypeError, ValueError) as error:
        print(f"Invalid API response data: {error}")
        return []
