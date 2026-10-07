import asyncio

import aiohttp
from bs4 import BeautifulSoup

from config import API_URL, REQUEST_TIMEOUT, MAX_PRODUCTS, SCRAPE_URL
from data_models import Product


async def fetch_api_products(session):
    """Asynchronously fetch products; only HTTP 200 may produce data."""

    try:
        async with session.get(
            API_URL,
            params={"limit": MAX_PRODUCTS},
        ) as response:
            if response.status != 200:
                if response.status == 404:
                    print("Async API returned HTTP 404. No product data returned.")
                elif response.status == 500:
                    print("Async API returned HTTP 500. No product data returned.")
                else:
                    print(
                        f"Async API returned HTTP {response.status}. "
                        "No product data returned."
                    )
                return []

            try:
                data = await response.json()
            except (aiohttp.ContentTypeError, ValueError) as error:
                print(f"Invalid async API response data: {error}")
                return []

            product_data = data.get("products", [])

            if not isinstance(product_data, list):
                print(
                    "Async API returned an invalid products field. "
                    "No product data returned."
                )
                return []

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
                    print(f"Skipping invalid async product data: {error}")

            return products

    except asyncio.TimeoutError as error:
        print(f"Async API request timed out after {REQUEST_TIMEOUT}s: {error}")
        return []
    except aiohttp.ClientConnectionError as error:
        print(f"Could not connect to async API: {error}")
        return []
    except aiohttp.ClientError as error:
        print(f"Async API request failed: {error}")
        return []


async def scrape_review(session, product):
    """Asynchronously scrape one review page; return no data on failure."""

    review_url = f"{SCRAPE_URL.rstrip('/')}/{product.id}"

    try:
        async with session.get(review_url) as response:
            if response.status != 200:
                if response.status == 404:
                    print(
                        f"Async review page for product {product.id} "
                        "returned HTTP 404. No review data returned."
                    )
                elif response.status == 500:
                    print(
                        f"Async review service returned HTTP 500 for "
                        f"product {product.id}. No review data returned."
                    )
                else:
                    print(
                        f"Async review page for product {product.id} "
                        f"returned HTTP {response.status}. "
                        "No review data returned."
                    )
                return None

            try:
                html = await response.text()
            except UnicodeError as error:
                print(
                    f"Invalid review response encoding for product "
                    f"{product.id}: {error}"
                )
                return None

            soup = BeautifulSoup(html, "html.parser")

            score_element = soup.select_one(".average-score")
            count_element = soup.select_one(".review-count")

            if score_element is None or count_element is None:
                print(
                    f"Review page for product {product.id} is missing "
                    "required review fields. No review data returned."
                )
                return None

            try:
                avg_score = float(score_element.get_text(strip=True))
                review_count = int(count_element.get_text(strip=True))
            except (TypeError, ValueError, AttributeError) as error:
                print(
                    f"Invalid review data for product "
                    f"{product.id}: {error}"
                )
                return None

            return Product(
                id=product.id,
                name=product.name,
                price=product.price,
                category=product.category,
                avg_score=avg_score,
                review_count=review_count,
            )

    except asyncio.TimeoutError as error:
        print(
            f"Async review request timed out after {REQUEST_TIMEOUT}s "
            f"for product {product.id}: {error}"
        )
        return None
    except aiohttp.ClientConnectionError as error:
        print(
            f"Could not connect to async review service for product "
            f"{product.id}: {error}"
        )
        return None
    except aiohttp.ClientError as error:
        print(
            f"Async review request failed for product "
            f"{product.id}: {error}"
        )
        return None


async def fetch_all_async():
    """Fetch API data and successful review pages asynchronously."""

    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        products = await fetch_api_products(session)

        tasks = [
            scrape_review(session, product)
            for product in products
        ]

        results = await asyncio.gather(*tasks)

        return [product for product in results if product is not None]
