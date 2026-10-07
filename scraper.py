import requests
from bs4 import BeautifulSoup

from config import SCRAPE_URL, REQUEST_TIMEOUT
from data_models import Product


def scrape_product_review(product):
    """Scrape review information; return no product when the review request fails."""

    review_url = f"{SCRAPE_URL.rstrip('/')}/{product.id}"

    try:
        response = requests.get(
            review_url,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.Timeout as error:
        print(
            f"Review request timed out after {REQUEST_TIMEOUT}s "
            f"for product {product.id}: {error}"
        )
        return None
    except requests.exceptions.ConnectionError as error:
        print(
            f"Could not connect to review service for product "
            f"{product.id}: {error}"
        )
        return None
    except requests.exceptions.RequestException as error:
        print(
            f"Review request failed for product "
            f"{product.id}: {error}"
        )
        return None

    if response.status_code != 200:
        if response.status_code == 404:
            print(
                f"Review page for product {product.id} returned HTTP 404. "
                "No review data returned."
            )
        elif response.status_code == 500:
            print(
                f"Review service returned HTTP 500 for product {product.id}. "
                "No review data returned."
            )
        else:
            print(
                f"Review page for product {product.id} returned "
                f"HTTP {response.status_code}. No review data returned."
            )
        return None

    try:
        soup = BeautifulSoup(response.text, "html.parser")

        score_element = soup.select_one(".average-score")
        count_element = soup.select_one(".review-count")

        if score_element is None or count_element is None:
            print(
                f"Review page for product {product.id} is missing "
                "required review fields. No review data returned."
            )
            return None

        avg_score = float(score_element.get_text(strip=True))
        review_count = int(count_element.get_text(strip=True))

        return Product(
            id=product.id,
            name=product.name,
            price=product.price,
            category=product.category,
            avg_score=avg_score,
            review_count=review_count,
        )

    except (TypeError, ValueError, AttributeError) as error:
        print(
            f"Invalid review data for product "
            f"{product.id}: {error}"
        )
        return None
