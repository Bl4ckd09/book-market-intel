# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["pandas", "openpyxl"]
# ///
"""Clean the raw scrape into analysis-ready data and a client-style Excel report.

Raw scraped fields are strings ("£51.77", "Three", "In stock"); this converts
them to typed columns, flags duplicates, and writes:
  data/books_clean.csv     - typed, deduplicated dataset
  data/market_report.xlsx  - Books sheet + Category Summary pivot
  data/cleaning_report.md  - what was done, row counts, issues found
"""

from pathlib import Path

import pandas as pd

DATA = Path(__file__).parent / "data"
RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def main() -> None:
    raw = pd.read_csv(DATA / "books_raw.csv")
    n_raw = len(raw)

    df = raw.copy()
    # extract the number rather than stripping "£": survives the mojibake
    # ("Â£45.17") the source emits when its encoding header is trusted
    df["price_gbp"] = df["price"].str.extract(r"(\d+\.\d+)").astype(float)
    df["rating"] = df["rating"].map(RATING_WORDS).astype("Int64")
    df["in_stock"] = df["availability"].str.contains("In stock")
    df = df.drop(columns=["price", "availability"])

    dupes = df.duplicated(subset=["title", "category"]).sum()
    df = df.drop_duplicates(subset=["title", "category"])

    issues = []
    if df["price_gbp"].isna().any():
        issues.append(f"{df['price_gbp'].isna().sum()} rows with unparseable price")
    if df["rating"].isna().any():
        issues.append(f"{df['rating'].isna().sum()} rows with unrecognised rating")

    df.to_csv(DATA / "books_clean.csv", index=False)

    summary = (
        df.groupby("category")
        .agg(
            books=("title", "count"),
            avg_price_gbp=("price_gbp", "mean"),
            avg_rating=("rating", "mean"),
            in_stock=("in_stock", "sum"),
        )
        .round(2)
        .sort_values("books", ascending=False)
        .reset_index()
    )

    with pd.ExcelWriter(DATA / "market_report.xlsx", engine="openpyxl") as xl:
        df.to_excel(xl, sheet_name="Books", index=False)
        summary.to_excel(xl, sheet_name="Category Summary", index=False)

    report = f"""# Cleaning report — book catalogue scrape

| Step | Result |
|---|---|
| Rows scraped | {n_raw} |
| Duplicate title+category rows removed | {dupes} |
| Final rows | {len(df)} |
| Categories | {df["category"].nunique()} |
| Price range | £{df["price_gbp"].min():.2f} – £{df["price_gbp"].max():.2f} (mean £{df["price_gbp"].mean():.2f}) |
| Mean rating | {df["rating"].mean():.2f} / 5 |
| In stock | {int(df["in_stock"].sum())} ({df["in_stock"].mean():.0%}) |

## Transformations
- `price` "£51.77" → numeric `price_gbp` (float) — regex extraction, robust to
  the source's encoding mojibake ("Â£…") from a mis-declared charset header
- `rating` "Three" → integer 1–5
- `availability` free text → boolean `in_stock`
- Deduplicated on (title, category)

## Data issues found
{chr(10).join("- " + i for i in issues) if issues else "- None — all rows parsed cleanly"}

## Deliverables
- `books_clean.csv` — typed, deduplicated dataset
- `market_report.xlsx` — full data + per-category pivot (count, avg price, avg rating, stock)
"""
    (DATA / "cleaning_report.md").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
