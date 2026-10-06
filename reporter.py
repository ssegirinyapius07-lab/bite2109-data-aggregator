import json


def save_report(report, filename="report.json"):
    """Save the analysis report as a JSON file."""

    data = {
        "total_products_analyzed": report["total_products"],
        "average_price_by_category": report[
            "average_price_by_category"
        ],
        "top_products": [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "category": product.category,
                "average_review_score": product.avg_score,
                "review_count": product.review_count,
            }
            for product in report["top_products"]
        ],
    }

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)