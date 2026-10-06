import requests
from bs4 import BeautifulSoup

from config import SCRAPE_URL, REQUEST_TIMEOUT
from data_models import Product


def scrape_product_review(product):
    """Scrape review information for one product."""

    review_url = f"{SCRAPE_URL.rstrip('/')}/{product.id}"

    try:
        response = requests.get(
            review_url,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 404:
            return Product(
                id=product.id,
                name=product.name,
                price=product.price,
                category=product.category,
                avg_score=0.0,
                review_count=0,
            )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

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

    except requests.exceptions.RequestException as error:
        print(
            f"Review request failed for product "
            f"{product.id}: {error}"
        )

        return Product(
            id=product.id,
            name=product.name,
            price=product.price,
            category=product.category,
            avg_score=0.0,
            review_count=0,
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
            avg_score=0.0,
            review_count=0,
        )