# Multi-Threaded Data Aggregator

## 1. Project Overview

This BITE 2109 project is a Python command-line data aggregator for market research. It retrieves product data from a REST API, scrapes review information from a simulated static website, processes the combined data, and generates a structured JSON report.

The application demonstrates REST API interaction, web scraping, custom data structures, functional programming, multithreading, asynchronous programming, testing, error handling, and performance profiling.

## 2. Architecture and Design

The application uses a modular design:

* `config.py` — stores API, scraper, timeout, and product-limit constants.
* `api_fetcher.py` — retrieves product data using `requests`, with caching and error handling.
* `offline_data.py` — provides backup product data when the external API is unavailable.
* `scraper.py` — uses BeautifulSoup to extract review scores and review counts.
* `data_models.py` — defines the custom `Product` data model.
* `threaded_fetcher.py` — performs review requests concurrently using `ThreadPoolExecutor`.
* `async_fetcher.py` — performs API and review requests asynchronously using `asyncio` and `aiohttp`.
* `analyzer.py` — performs filtering and analysis.
* `reporter.py` — generates JSON reports.
* `main.py` — controls the application and provides the two execution modes.

This separation keeps data collection, processing, concurrency, and reporting independent and easier to maintain.

## 3. Data Model and Processing

Products are represented by a custom dataclass:

`Product(id, name, price, category, avg_score, review_count)`

The class uses `@dataclass(slots=True)`, providing `__slots__` behaviour. This restricts objects to the required attributes and reduces memory overhead compared with a normal instance dictionary.

The analyzer uses the required functional programming techniques:

* `filter()` removes products with no reviews.
* `map()` extracts product categories.
* `reduce()` combines product prices to calculate category totals.

The analyzer then calculates the average price per category and identifies the five highest-rated products.

## 4. API and Web Scraping

`api_fetcher.py` uses the `requests` library to obtain product ID, name, price, and category from the REST API. It uses `functools.lru_cache` to cache the API-fetch operation.

Error handling covers request failures, timeouts, unsuccessful HTTP responses, and invalid API data. If the external API is unavailable, prepared offline data can be used so the application can continue operating.

For each product, `scraper.py` requests the corresponding simulated review page. BeautifulSoup extracts the average review score and review count. Missing review pages, request failures, and invalid review data are handled without terminating the complete aggregation.

## 5. Concurrency Approaches

### ThreadPoolExecutor

The `threads` mode uses `ThreadPoolExecutor` to concurrently scrape product review pages. This is appropriate for I/O-bound network operations.

Run:

`python main.py --mode threads`

Latest measured aggregation time:

**1.1465 seconds**

### Asyncio + aiohttp

The `async` mode uses `asyncio` and `aiohttp` to asynchronously fetch API data and review pages.

Run:

`python main.py --mode async`

Latest measured aggregation time:

**1.3674 seconds**

Both approaches processed the same 20 products and produced the same analysis results. The difference in execution time demonstrates that concurrency performance depends on network and runtime overhead; neither approach is guaranteed to be faster in every environment.

## 6. Performance Profiling

`cProfile` was used to identify where execution time is spent.

The earlier profiled threaded run recorded **472,613 function calls** and **3.218 seconds** total profiled time. Significant cumulative time occurred in `requests` and `urllib3`, showing the effect of network I/O.

The asynchronous profile recorded **433,506 function calls** and **3.169 seconds** total profiled time. Significant activity occurred in the `asyncio` event loop and Windows asynchronous I/O operations.

The cProfile totals include program startup and profiling overhead, so the direct performance comparison uses the measured aggregation times above.

## 7. Testing

The project contains five unit tests. They verify:

1. Products without reviews are excluded.
2. Category average prices are calculated correctly.
3. The five highest-rated products are identified.
4. The `Product` class uses `__slots__`.
5. API data can be processed using `unittest.mock.patch` to simulate a network response.

The test suite passed with:

**5 tests passed, 0 failed.**

Run tests with:

`python -m pytest -v`

## 8. Reporting and Usage

The application displays the collected products, average price by category, and Top 5 highest-rated products on the console. It also creates:

* `report_threads.json`
* `report_async.json`

Each JSON report contains the total products analyzed, category averages, and Top 5 product details.

Install dependencies:

`python -m pip install -r requirements.txt`

Start the simulated review website in a separate terminal:

`python mock_review_server.py`

Run the two modes:

`python main.py --mode threads`

`python main.py --mode async`

Profile the applications:

`python -m cProfile -o profile_threads.prof main.py --mode threads`

`python -m cProfile -o profile_async.prof main.py --mode async`

## 9. Conclusion

The project demonstrates a complete data-aggregation pipeline combining REST API retrieval, web scraping, custom data modelling, functional programming, concurrent processing, asynchronous processing, error handling, automated testing, JSON reporting, and performance profiling. The two concurrency approaches provide alternative solutions for handling I/O-bound operations while producing the same analytical results.
