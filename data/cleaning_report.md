# Cleaning report — book catalogue scrape

| Step | Result |
|---|---|
| Rows scraped | 1000 |
| Duplicate title+category rows removed | 1 |
| Final rows | 999 |
| Categories | 50 |
| Price range | £10.00 – £59.99 (mean £35.07) |
| Mean rating | 2.92 / 5 |
| In stock | 999 (100%) |

## Transformations
- `price` "£51.77" → numeric `price_gbp` (float) — regex extraction, robust to
  the source's encoding mojibake ("Â£…") from a mis-declared charset header
- `rating` "Three" → integer 1–5
- `availability` free text → boolean `in_stock`
- Deduplicated on (title, category)

## Data issues found
- None — all rows parsed cleanly

## Deliverables
- `books_clean.csv` — typed, deduplicated dataset
- `market_report.xlsx` — full data + per-category pivot (count, avg price, avg rating, stock)
