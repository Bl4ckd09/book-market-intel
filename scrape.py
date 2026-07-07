# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["requests", "beautifulsoup4"]
# ///
"""Scrape the full catalogue of books.toscrape.com (a public scraping sandbox).

Walks every category page so each record carries its category without
visiting 1,000 individual product pages. Polite by design: sequential
requests with a fixed delay, custom User-Agent, retries with backoff.

Output: data/books_raw.csv  (one row per book, fields as-scraped)
"""

import csv
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://books.toscrape.com/"
DELAY_S = 0.25
HEADERS = {"User-Agent": "portfolio-demo-scraper/1.0 (contact: sunjoohwang.sh@gmail.com)"}

session = requests.Session()
session.headers.update(HEADERS)


def get(url: str, tries: int = 3) -> BeautifulSoup:
    for attempt in range(tries):
        try:
            resp = session.get(url, timeout=20)
            resp.raise_for_status()
            resp.encoding = "utf-8"  # server mis-declares latin-1; £ mojibakes without this
            time.sleep(DELAY_S)
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as e:
            if attempt == tries - 1:
                raise
            wait = 2**attempt
            print(f"  retry {attempt + 1} for {url} after {wait}s ({e})", file=sys.stderr)
            time.sleep(wait)


def scrape_category(name: str, url: str) -> list[dict]:
    rows = []
    page_url = url
    while True:
        soup = get(page_url)
        for card in soup.select("article.product_pod"):
            rows.append(
                {
                    "title": card.h3.a["title"],
                    "category": name,
                    "price": card.select_one(".price_color").text,
                    "rating": card.select_one(".star-rating")["class"][1],
                    "availability": card.select_one(".availability").text.strip(),
                    "product_url": urljoin(page_url, card.h3.a["href"]),
                }
            )
        nxt = soup.select_one("li.next a")
        if not nxt:
            return rows
        page_url = urljoin(page_url, nxt["href"])


def main() -> None:
    out_dir = Path(__file__).parent / "data"
    out_dir.mkdir(exist_ok=True)

    home = get(BASE)
    categories = [
        (a.text.strip(), urljoin(BASE, a["href"]))
        for a in home.select(".side_categories ul ul a")
    ]
    print(f"{len(categories)} categories found")

    all_rows: list[dict] = []
    for i, (name, url) in enumerate(categories, 1):
        rows = scrape_category(name, url)
        all_rows.extend(rows)
        print(f"[{i:2}/{len(categories)}] {name}: {len(rows)} books")

    out_path = out_dir / "books_raw.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\nWrote {len(all_rows)} rows -> {out_path}")


if __name__ == "__main__":
    main()
