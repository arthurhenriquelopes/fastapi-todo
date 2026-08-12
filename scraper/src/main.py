import os
import time
import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
from pydantic import BaseModel, HttpUrl, ValidationError

CACHE_DIR = "cache"
OUTPUT_DIR = "output"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/arthurhenriquelopes/fastapi-todo)"

class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: HttpUrl
    fetched_at: str

def fetch_and_cache(url: str, filename: str) -> str:
    cache_path = os.path.join(CACHE_DIR, filename)
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
            
    time.sleep(0.5)
    headers = {"User-Agent": USER_AGENT}
    
    for attempt in range(2):
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            html = response.text
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html)
            return html
        elif response.status_code in [404, 403]:
            print(f"Skipping {url} due to {response.status_code}")
            return None
        elif response.status_code >= 500:
            print(f"Server error {response.status_code} on {url}, retrying...")
            time.sleep(1)
        else:
            raise Exception(f"Failed to fetch {url}, status: {response.status_code}")
            
    return None

def get_book_links(html: str, base_url: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for h3 in soup.find_all("h3"):
        a_tag = h3.find("a")
        if a_tag and "href" in a_tag.attrs:
            links.append(urljoin(base_url, a_tag["href"]))
    return links

def discover_all_books():
    all_book_links = []
    base_catalogue_url = "https://books.toscrape.com/catalogue/"
    
    for page_num in range(1, 4):
        url = f"{base_catalogue_url}page-{page_num}.html"
        html = fetch_and_cache(url, f"catalogue-page-{page_num}.html")
        if html:
            links = get_book_links(html, url)
            all_book_links.extend(links)
        
    return list(set(all_book_links))

def extract_book_details(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("h1").text if soup.find("h1") else None
    
    price_text = None
    price_gbp = 0.0
    price_p = soup.find("p", class_="price_color")
    if price_p:
        price_text = price_p.text
        match = re.search(r"[\d\.]+", price_text)
        if match:
            price_gbp = float(match.group())
        
    availability_text = None
    avail_p = soup.find("p", class_="availability")
    if avail_p:
        availability_text = avail_p.text.strip()
        
    rating_text = None
    rating_p = soup.find("p", class_="star-rating")
    if rating_p:
        classes = rating_p.get("class", [])
        if len(classes) > 1:
            rating_text = classes[1]
            
    description = None
    desc_div = soup.find("div", id="product_description")
    if desc_div:
        desc_p = desc_div.find_next_sibling("p")
        if desc_p:
            description = desc_p.text
            
    return {
        "title": title,
        "product_url": url,
        "price_text": price_text,
        "price_gbp": price_gbp,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": url,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

if __name__ == "__main__":
    start_time = time.time()
    
    unique_links = discover_all_books()
    unique_links.append("https://books.toscrape.com/catalogue/this-book-does-not-exist_9999/index.html")
    
    valid_records = []
    errors = []
    failed_pages = 0
    pages_fetched = 0
    
    for i, url in enumerate(unique_links):
        html = fetch_and_cache(url, f"book-{i}.html")
        if not html:
            failed_pages += 1
            continue
            
        pages_fetched += 1
        record_raw = extract_book_details(html, url)
        try:
            record_validated = BookRecord(**record_raw)
            valid_records.append(record_validated.model_dump(mode='json'))
        except ValidationError as e:
            errors.append({"url": url, "error": e.errors()})
            
    with open(os.path.join(OUTPUT_DIR, "books.json"), "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2)
        
    with open(os.path.join(OUTPUT_DIR, "errors.json"), "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2)
        
    duration = time.time() - start_time
    
    run_report = {
        "start_time": datetime.fromtimestamp(start_time, timezone.utc).isoformat(),
        "duration_seconds": round(duration, 2),
        "pages_fetched": pages_fetched,
        "valid_records": len(valid_records),
        "invalid_records": len(errors),
        "failed_pages": failed_pages
    }
    
    with open(os.path.join(OUTPUT_DIR, "run-report.json"), "w", encoding="utf-8") as f:
        json.dump(run_report, f, indent=2)
        
    print(f"Validated records: {len(valid_records)}, Errors: {len(errors)}, Failed pages: {failed_pages}")
