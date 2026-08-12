import os
import time
import requests

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

if __name__ == "__main__":
    html = fetch_and_cache("https://books.toscrape.com/catalogue/page-1.html", "catalogue-page-1.html")
    print(f"Content length: {len(html)}")
