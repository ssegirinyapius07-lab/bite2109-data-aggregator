import asyncio

import aiohttp
from bs4 import BeautifulSoup

from config import API_URL, REQUEST_TIMEOUT, MAX_PRODUCTS, SCRAPE_URL
from data_models import Product


async def fetch_api_products(session):
    """Asynchronously fetch products from the API."""

    try:
        async with session.get(
            API_URL,
            params={"limit": MAX_PRODUCTS},
        ) as response:
            response.raise_for_status()
            data = await response.json()

            return [
                Product(
                    id=int(item["id"]),
                    name=item["title"],
                    price=float(item["price"]),
                    category=item["category"],
                )
                for item in data.get("products", [])
            ]

    except (aiohttp.ClientError, asyncio.TimeoutError) as error:
        print(f"Async API request failed: {error}")
        return []

    except (KeyError, TypeError, ValueError) as error:
        print(f"Invalid API data: {error}")
        return []


async def scrape_review(session, product):
    """Asynchronously scrape one product review page."""

    review_url = f"{SCRAPE_URL.rstrip('/')}/{product.id}"

    try:
        async with session.get(review_url) as response:
            if response.status == 404:
                return Product(
                    id=product.id,
                    name=product.name,
                    price=product.price,
                    category=product.category,
                )

            response.raise_for_status()

            html = await response.text()

            soup = BeautifulSoup(html, "html.parser")

            score_element = soup.select_one(".average-score")
            count_element = soup.select_one(".review-count")

            avg_score = (
                float(score_element.get_text(strip=True))
                if score_element
                else 0.0
            )

            review_count = (
                int(count_element.get_text(strip=True))
                if count_element
                else 0
            )

            return Product(
                id=product.id,
                name=product.name,
                price=product.price,
                category=product.category,
                avg_score=avg_score,
                review_count=review_count,
            )

    except (aiohttp.ClientError, asyncio.TimeoutError) as error:
        print(
            f"Async review request failed for product "
            f"{product.id}: {error}"
        )

        return Product(
            id=product.id,
            name=product.name,
            price=product.price,
            category=product.category,
        )

    except (TypeError, ValueError) as error:
        print(
            f"Invalid review data for product "
            f"{product.id}: {error}"
        )

        return Product(
            id=product.id,
            name=product.name,
            price=product.price,
            category=product.category,
        )


async def fetch_all_async():
    """Fetch API data and review pages asynchronously."""

    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        products = await fetch_api_products(session)

        tasks = [
            scrape_review(session, product)
            for product in products
        ]

        return await asyncio.gather(*tasks)