# Polite Scraper for Books to Scrape

This project is a web scraper built to collect data from a practice sandbox safely and politely.

## Target Classification
- **Target Site:** `https://books.toscrape.com`
- **Why:** It's a public sandbox built explicitly for people to practice scraping.
- **Scope:** First 3 catalogue pages and their 60 corresponding book detail pages.
- **Data Collected:** Book title, price, availability, rating, and description.
- **Appropriateness:** It is appropriate because the site is designed to be scraped for educational purposes.

**Robots.txt Check:** No robots file found (`https://books.toscrape.com/robots.txt` returned a 404 Not Found). This means there are no explicit machine-readable rules, but we still apply ethical scraping standards.

*I will not reuse this code on another site without checking its rules and terms first.*

## How to Install & Run

This project uses Python 3.10+.
1. Install dependencies:
   ```bash
   pip install requests beautifulsoup4 pydantic
   ```
2. Run the scraper:
   ```bash
   python src/main.py
   ```
3. Check the `output/` directory for `books.json` and `run-report.json`.

## Record Schema
Every parsed record is validated against this strict schema using Pydantic:
- `title` (string)
- `product_url` (absolute URL)
- `price_text` (string, e.g. "£51.77")
- `price_gbp` (float, e.g. 51.77)
- `availability_text` (string)
- `rating_text` (string)
- `description` (string or null)
- `source_page` (absolute URL)
- `fetched_at` (ISO timestamp)

## Politeness Rules Followed
- **User-Agent:** Honest identity (`FlyRankInternship-A9/1.0 (+https://github.com/arthurhenriquelopes/fastapi-todo)`).
- **Delay:** 0.5s mandatory sleep between requests to avoid overloading.
- **Timeout:** 10s maximum wait.
- **Cache:** Every page is saved to `cache/` locally. If run again, the script skips the network request and reads from disk.

## Limitations
*Honest limitation:* The crawler only goes exactly 3 pages deep based on hardcoded limits. It doesn't dynamically discover all 50 pages of the website.

## Run Report Evidence

```json
{
  "start_time": "2026-08-12T20:58:30+00:00",
  "duration_seconds": 38.64,
  "pages_fetched": 60,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}
```

*Note: Why no browser automation (like Selenium or Playwright)? Because all the raw data is already baked right into the static HTML served by `books.toscrape.com`. Using a full browser would just waste memory and network resources for zero extra value.*

---

**Ethics Note:** Always check for an official API before resorting to web scraping. Never scrape behind logins, never bypass paywalls, and collect only what is strictly necessary to solve your problem.
