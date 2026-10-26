# Web Scraper Price Monitor

A command-line tool that scrapes book prices and stock status from an online
catalogue, logs every run to a CSV file, lists the books currently in stock,
and reports which prices or stock statuses changed since the previous run.

## Target site

[books.toscrape.com](https://books.toscrape.com), a practice bookstore built
for scraping. Catalogue pages follow `catalogue/page-N.html`, with 20 books
per page.

## Features

- Scrapes title, price, availability, and product URL for every book.
- Lists the books that are currently in stock.
- Appends a timestamped row per book to `prices.csv` (full history, including
  out-of-stock books).
- Detects and reports **price changes** and **stock changes** against the
  previous run.
- Scrapes as many catalogue pages as you ask for.

## Setup

```
python -m venv venv
venv\Scripts\activate
pip install requests beautifulsoup4
```

## Usage

```
python price_monitor.py --pages 3
```

`--pages` sets how many catalogue pages to scrape (default: 1).

## Example output

```
Title: A Light in the Attic - Price: 51.77 - In stock - URL: https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
Title: Tipping the Velvet - Price: 53.74 - In stock - URL: https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
PRICE CHANGED: A Light in the Attic: 51.77 -> 49.99
STOCK CHANGED: Soumission: Out of stock -> In stock
Scraped 60 products, 58 in stock, 2 price/stock change(s).
```

## Data: `prices.csv`

| column       | example                                  |
|--------------|------------------------------------------|
| timestamp    | 2026-10-16T09:30:00                      |
| title        | A Light in the Attic                     |
| price        | 51.77                                    |
| url          | https://books.toscrape.com/catalogue/... |
| availability | In stock                                 |

The file is an append-only history: one row per product per run, and earlier
rows are never overwritten.

> If you have a `prices.csv` from an older version without the `availability`
> column, delete it before the first run so the columns line up.

## How it behaves

- **Polite:** sends a User-Agent, uses a request timeout, and pauses between
  requests.
- **Resilient:** a failed page is skipped with a message and never crashes the
  run. If nothing could be scraped, it says so and stops.
- **Exact prices:** stored as decimals, not floats, with the currency symbol
  stripped.
- **Stock detection:** a book counts as in stock when its availability text
  contains "in stock" (case-insensitive). A missing availability tag is
  recorded as `Unknown`.
- **Change detection:** compares each book with its most recent recorded row,
  and a run never compares data with itself.
- **First run:** works with no existing file, and the CSV header is written
  once.

## Tech

Python 3, `requests`, `beautifulsoup4`, and the standard library (`csv`, `re`,
`decimal`, `argparse`, `datetime`, `pathlib`, `urllib.parse`).

## Limitations

- Targets one site's HTML structure, so a redesign would break the selectors.
- Stock changes are only detected for books that already have a recorded
  availability.
- Compares against the previous run only, with no long-term trend analysis.

## Ideas for next steps

- Follow the site's "next" link instead of using a fixed page count.
- Report price drops only.
- Schedule daily runs (Windows Task Scheduler).
- Chart a book's price history.

## What I learned

(Fill this in after building it.)
