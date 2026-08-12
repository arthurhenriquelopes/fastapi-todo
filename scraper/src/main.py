import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/arthurhenriquelopes/fastapi-todo)"

def fetch_and_cache(url: str, filename: str) -> str:
    cache_path = os.path.join(CACHE_DIR, filename)
    if os.path.exists(cache_path):
        print(f"CACHE HIT: {url}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
            
    print(f"FETCH: {url}")
    time.sleep(0.5)
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        html = response.text
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(html)
        return html
    else:
        raise Exception(f"Failed to fetch {url}, status: {response.status_code}")

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
        links = get_book_links(html, url)
        all_book_links.extend(links)
        
    unique_links = list(set(all_book_links))
    print(f"catalogue_pages=3, discovered={len(all_book_links)}, unique_urls={len(unique_links)}")
    return unique_links

if __name__ == "__main__":
    unique_links = discover_all_books()
