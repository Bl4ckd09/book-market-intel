# Book Market Intelligence Pipeline

End-to-end data pipeline demo: **scrape → clean → enrich → report**. Built as
a work sample; the same pattern delivers product catalogues, price monitoring,
directory extraction and lead enrichment.

Target is [books.toscrape.com](https://books.toscrape.com) — a public sandbox
site built for scraping practice, so the demo is 100% terms-compliant.

## Pipeline

| Stage | Script | Output |
|---|---|---|
| 1. Scrape | `scrape.py` | `data/books_raw.csv` — 1,000 books, 50 categories |
| 2. Clean | `clean.py` | `data/books_clean.csv` + `data/market_report.xlsx` + `data/cleaning_report.md` |
| 3. Enrich | `enrich.py` | `data/books_enriched_sample.csv` — merged with Open Library API |

## Run it

Requires [uv](https://docs.astral.sh/uv/) only — dependencies are declared
inline and resolve automatically:

```bash
uv run scrape.py   # ~3 min, polite rate-limiting
uv run clean.py
uv run enrich.py   # top-20 sample, free Open Library API
```

## What it demonstrates

- **Resilient scraping** — sequential + rate-limited by design, custom
  User-Agent, retries with exponential backoff, category-walk strategy that
  avoids 1,000 unnecessary product-page requests
- **Real-world data cleaning** — handles the site's mis-declared charset
  (mojibake-safe price parsing), word-ratings → integers, free-text
  availability → booleans, deduplication, and a written report of every
  transformation
- **API integration** — third-party REST enrichment with title
  normalization, match-rate reporting, and graceful handling of misses
- **Client-ready delivery** — typed CSV, multi-sheet Excel with a category
  pivot, and a cleaning report so nothing changes silently
