from functools import reduce


def analyze_products(products):
    """Analyze products using map, filter, and reduce."""

    reviewed_products = list(
        filter(
            lambda product: product.review_count > 0,
            products,
        )
    )

    categories = set(
        map(
            lambda product: product.category,
            reviewed_products,
        )
    )

    average_price_by_category = {}

    for category in categories:
        category_products = list(
            filter(
                lambda product: product.category == category,
                reviewed_products,
            )
        )

        total_price = reduce(
            lambda total, product: total + product.price,
            category_products,
            0.0,
        )

        average_price_by_category[category] = (
            total_price / len(category_products)
            if category_products
            else 0.0
        )

    top_products = sorted(
        reviewed_products,
        key=lambda product: product.avg_score,
        reverse=True,
    )[:5]

    return {
        "total_products": len(reviewed_products),
        "average_price_by_category": average_price_by_category,
        "top_products": top_products,
    }