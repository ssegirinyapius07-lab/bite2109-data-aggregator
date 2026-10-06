import argparse
import asyncio
import time

from analyzer import analyze_products
from async_fetcher import fetch_all_async
from reporter import save_report
from threaded_fetcher import fetch_all_threaded


def run_threads():
    """Run the ThreadPoolExecutor approach."""
    start_time = time.perf_counter()

    products = fetch_all_threaded()

    elapsed = time.perf_counter() - start_time

    return products, elapsed


def run_async():
    """Run the asyncio + aiohttp approach."""
    start_time = time.perf_counter()

    products = asyncio.run(fetch_all_async())

    elapsed = time.perf_counter() - start_time

    return products, elapsed


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Threaded Data Aggregator"
    )

    parser.add_argument(
        "--mode",
        choices=["threads", "async"],
        required=True,
        help="Choose the data aggregation approach.",
    )

    args = parser.parse_args()

    if args.mode == "threads":
        print("Starting ThreadPoolExecutor aggregation...")
        products, elapsed = run_threads()
        mode_name = "ThreadPoolExecutor"

    else:
        print("Starting asyncio + aiohttp aggregation...")
        products, elapsed = run_async()
        mode_name = "Asyncio + aiohttp"

    report = analyze_products(products)

    print("\nData aggregation completed.")
    print(f"Mode: {mode_name}")
    print(f"Products analyzed: {report['total_products']}")
    print(f"Execution time: {elapsed:.4f} seconds")

    print("\nProducts collected:")

    for number, product in enumerate(
        sorted(products, key=lambda p: p.id),
        start=1,
    ):
        print(f"\nProduct {number}")
        print(f"  ID: {product.id}")
        print(f"  Name: {product.name}")
        print(f"  Price: ${product.price:.2f}")
        print(f"  Category: {product.category}")
        print(f"  Average Score: {product.avg_score:.1f}")
        print(f"  Review Count: {product.review_count}")

    print("\nAverage price by category:")

    for category, average in report[
        "average_price_by_category"
    ].items():
        print(f"  {category}: {average:.2f}")

    print("\nTop 5 highest-rated products:")

    for number, product in enumerate(
        report["top_products"],
        start=1,
    ):
        print(f"\nTop Product {number}")
        print(f"  ID: {product.id}")
        print(f"  Name: {product.name}")
        print(f"  Price: ${product.price:.2f}")
        print(f"  Category: {product.category}")
        print(f"  Average Score: {product.avg_score:.1f}")
        print(f"  Review Count: {product.review_count}")

    save_report(
        report,
        filename=f"report_{args.mode}.json",
    )

    print(
        f"\nReport saved to report_{args.mode}.json"
    )


if __name__ == "__main__":
    main()