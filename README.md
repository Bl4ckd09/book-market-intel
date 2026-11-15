# Book Market Intelligence Pipeline

This end-to-end demo follows **scrape → clean → enrich → report**. As a work
sample, it illustrates a pattern for product catalogues, price monitoring,
directory extraction, and lead enrichment.

The target is [books.toscrape.com](https://books.toscrape.com), a public
sandbox built for scraping practice.

## Pipeline

| Stage | Script | Output |
|---|---|---|
| 1. Scrape | `scrape.py` | `data/books_raw.csv` — 1,000 books, 50 categories |
| 2. Clean | `clean.py` | `data/books_clean.csv` + `data/market_report.xlsx` + `data/cleaning_report.md` |
| 3. Enrich | `enrich.py` | `data/books_enriched_sample.csv` — top-20 sample enriched via the free Open Library API |

## Project layout

- `scrape.py` — scrapes books into `data/books_raw.csv`.
- `clean.py` — cleans the data and produces `data/books_clean.csv`, `data/market_report.xlsx`, and `data/cleaning_report.md`.
- `enrich.py` — calls the free Open Library API for a top-20 sample, producing `data/books_enriched_sample.csv`.
- `data/` — pipeline outputs: raw and cleaned CSVs, the enriched sample, the Excel report, and the cleaning report.

## Run it

Uses [uv](https://docs.astral.sh/uv/); dependencies are declared inline and
resolved automatically:

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
