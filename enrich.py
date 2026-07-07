# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["requests", "pandas"]
# ///
"""API-enrichment demo: merge scraped data with a third-party REST API.

Takes the 20 highest-rated books from the cleaned dataset and looks each
title up in the Open Library search API (free, no key), pulling author,
first-publish year and ISBN when a match exists. Shows the integration
pattern clients ask for: scraped data + external API -> one merged file.

Output: data/books_enriched_sample.csv
"""

import re
import time
from pathlib import Path

import pandas as pd
import requests

DATA = Path(__file__).parent / "data"
API = "https://openlibrary.org/search.json"
HEADERS = {"User-Agent": "portfolio-demo-enricher/1.0 (contact: sunjoohwang.sh@gmail.com)"}


def normalize(title: str) -> str:
    """Strip series suffixes '(Series #2)' and subtitles — they sink match rates."""
    title = re.sub(r"\s*\([^)]*\)\s*$", "", title)
    return title.split(":")[0].strip()


def lookup(title: str) -> dict:
    title = normalize(title)
    try:
        resp = requests.get(
            API, params={"title": title, "limit": 1}, headers=HEADERS, timeout=15
        )
        resp.raise_for_status()
        docs = resp.json().get("docs", [])
    except requests.RequestException:
        docs = []
    if not docs:
        return {"author": None, "first_publish_year": None, "isbn": None, "api_match": False}
    doc = docs[0]
    return {
        "author": (doc.get("author_name") or [None])[0],
        "first_publish_year": doc.get("first_publish_year"),
        "isbn": (doc.get("isbn") or [None])[0],
        "api_match": True,
    }


def main() -> None:
    df = pd.read_csv(DATA / "books_clean.csv")
    sample = df.sort_values(["rating", "price_gbp"], ascending=[False, True]).head(20)

    enriched = []
    for _, row in sample.iterrows():
        info = lookup(row["title"])
        enriched.append({**row.to_dict(), **info})
        print(f"{'✓' if info['api_match'] else '✗'} {row['title'][:60]}")
        time.sleep(0.5)

    out = pd.DataFrame(enriched)
    out.to_csv(DATA / "books_enriched_sample.csv", index=False)
    matched = int(out["api_match"].sum())
    print(f"\nEnriched {matched}/{len(out)} titles via Open Library -> books_enriched_sample.csv")


if __name__ == "__main__":
    main()
