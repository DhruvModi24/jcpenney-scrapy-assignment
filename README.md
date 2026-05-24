# JCPenney Product Scraper

## Objective

Develop a robust and scalable web scraper to extract product information from JCPenney using a configurable search term.

This scraper demonstrates:

- API-based product discovery
- Scrapy production architecture
- Pagination handling
- Data extraction from product detail pages
- Error handling and retry mechanisms
- Middleware and pipeline usage
- Respectful crawling practices
- Structured JSON and CSV export

---

# Search Term Configuration

The scraper uses a dynamic search term variable.

Example:

```python
SEARCH_TERM = "tshirt"
```

If a new keyword needs to be scraped, simply change the variable value.

The backend API URLs are automatically generated using this search term, making the scraper reusable and flexible.

---

# Backend API Discovery

Instead of scraping product listing HTML pages directly, the scraper uses JCPenney's internal backend search API discovered through browser network inspection.

Example API:

```text
https://search-api.jcpenney.com/v1/search-service/s
```

Reason for using API approach:

- Product listing pages do not load all data reliably in HTML
- API provides structured JSON responses
- Faster and more stable extraction
- Cleaner pagination handling
- Reduced DOM dependency
- Better scalability for large crawls

This demonstrates real-world scraping methodology where backend APIs are preferred whenever available.

---

# Pagination Handling

The scraper currently crawls:

- Page 1
- Page 2

using backend API pagination parameters.

Pagination is implemented dynamically.

Currently, a condition is added in code to limit scraping to only 2 pages for assessment purposes.

If the limit condition is removed, the scraper can automatically crawl all available pages for any search term.

This makes the implementation dynamic rather than static.

---

# Product URL Extraction

The scraper extracts product URLs directly from API JSON responses.

Features:

- Deduplicates URLs using Python `set()`
- Prevents duplicate crawling
- Stores stable listing data from API
- Passes metadata between Scrapy requests using `meta`
- Efficient request scheduling using `yield`

---

# Product Detail Extraction

Each extracted product URL is visited individually.

The scraper extracts:

- url
- Product Name
- Current Price
- Original Price
- Discount
- Features
- Descriptions
- Image URLs
- Ratings
- Review Count
- Sizes
- Colors

Extraction includes:

- Exception handling
- Safe fallback extraction
- Logging support
- Missing field handling
- Structured output formatting

---

# Tech Stack

- Python 3.11.x
- Scrapy 2.11.2

---

# Features

- Scrapy spider architecture
- Item pipelines
- Downloader middleware
- Windows User-Agent rotation
- AutoThrottle support
- Retry handling
- Respectful crawling delays
- robots.txt compliance
- Structured logging
- JSON export
- CSV export
- Dynamic pagination
- API-based crawling
- Deduplicated URL handling
- Modular code organization

---

# Project Structure

```text
jcpenney_scraper/
│
├── scrapy.cfg
├── requirements.txt
├── README.md
│
└── jcpenney_scraper/
    ├── items.py
    ├── middlewares.py
    ├── pipelines.py
    ├── settings.py
    │
    └── spiders/
        └── jcpenney_spider.py
```

---

# Installation

## 1. Clone Repository

```bash
git clone <repository-url>
```

---

## 2. Move Into Project Folder

```bash
cd jcpenney-scrapy-assignment
```

---

## 3. Create Virtual Environment

### Windows PowerShell

```powershell
python -m venv venv
```

Activate environment:

```powershell
.\venv\Scripts\Activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Python Version

Tested on:

```text
Python 3.11.x
```

---

# How To Run

IMPORTANT:

Run the command from the folder containing:

```text
scrapy.cfg
```

Run spider:

```bash
scrapy crawl jcpenney_spider
```

---

# Output

The scraper exports structured data into:

```text
jcpenney_products.json
```

and

```text
jcpenney_products.csv
```

---

# Architecture

The scraper follows standard Scrapy architecture:

## Spider

Responsible for:

- Calling backend search API
- Handling pagination
- Scheduling product detail requests

---

## Items

Defines structured product schema.

---

## Middleware

Handles:

- User-Agent rotation
- Request customization

---

## Pipelines

Responsible for:

- Cleaning data
- Formatting output
- Exporting JSON/CSV

---

# Notes

- Selectors may change if JCPenney updates frontend structure
- Backend APIs are more stable than HTML listing pages
- Product detail pages are still parsed using HTML extraction
- The scraper currently limits crawling to 2 pages intentionally for assessment scope

---

# Potential Improvements

- Proxy rotation
- Database integration
- Docker support
- Scrapyd deployment
- Cloud execution
- Monitoring and alerting
- Distributed crawling

---

# Key Engineering Decisions

## Why Scrapy?

Scrapy provides:

- Asynchronous crawling
- Built-in retry support
- Middleware architecture
- Pipeline architecture
- Auto throttling
- Scalable crawling system

---

## Why Backend API Instead of HTML Listing Pages?

Using backend API provides:

- Cleaner structured data
- Better performance
- Stable pagination
- Reduced parsing complexity
- Lower dependency on frontend DOM

This approach reflects real-world production scraping practices.

---

# Conclusion

This project demonstrates:

- Production-grade Scrapy architecture
- Backend API reverse engineering
- Robust crawling workflow
- Structured extraction pipelines
- Fault-tolerant scraping
- Scalable scraper design
- Maintainable code organization