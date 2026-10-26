import argparse
import csv
import re
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
CSV_FILE = Path("prices.csv")
FIELDS = ["timestamp", "title", "price", "url", "availability"]
HEADERS = {"User-Agent": "price-monitor-practice/1.0"}


def fetch(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response.text


def parse_price(text):
    match = re.search(r"\d+(?:\.\d+)?", text)
    if not match:
        raise ValueError(f"No price found in {text!r}")
    return Decimal(match.group())


def is_in_stock(availability_text):
    return "in stock" in availability_text.lower()


def parse_products(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    products = []
    for card in soup.select("article.product_pod"):
        link = card.select_one("h3 a")
        price_tag = card.select_one("p.price_color")
        stock_tag = card.select_one("p.availability")
        if link is None or price_tag is None:
            continue
        products.append({
            "title": link["title"],
            "price": parse_price(price_tag.get_text()),
            "availability": stock_tag.get_text(strip=True) if stock_tag else "Unknown",
            "url": urljoin(page_url, link["href"]),
        })
    return products


def load_last_records():
    if not CSV_FILE.exists():
        return {}
    last = {}
    with CSV_FILE.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            last[row["url"]] = {
                "price": Decimal(row["price"]),
                "availability": row.get("availability"),
            }
    return last


def append_prices(products):
    is_new_file = not CSV_FILE.exists()
    now = datetime.now().isoformat(timespec="seconds")
    with CSV_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new_file:
            writer.writeheader()
        for p in products:
            writer.writerow({"timestamp": now, **p})


def list_available_products(products):
    return [p for p in products if is_in_stock(p["availability"])]


def report_changes(products, last_records):
    changes = 0
    for p in products:
        old = last_records.get(p["url"])
        if old is None:
            continue
        if old["price"] != p["price"]:
            print(f"PRICE CHANGED: {p['title']}: {old['price']} -> {p['price']}")
            changes += 1
        old_stock = old["availability"]
        if old_stock and old_stock != p["availability"]:
            print(f"STOCK CHANGED: {p['title']}: {old_stock} -> {p['availability']}")
            changes += 1
    return changes


def main():
    parser = argparse.ArgumentParser(description="Monitor book prices & list available books")
    parser.add_argument("--pages", type=int, default=1, help="pages to scrape")
    args = parser.parse_args()

    last_records = load_last_records()
    products = []
    for page in range(1, args.pages + 1):
        url = BASE_URL.format(page)
        try:
            products.extend(parse_products(fetch(url), url))
        except requests.RequestException as err:
            print(f"Skipping page {page}: {err}")
        time.sleep(1)  # be polite: pause between requests

    if not products:
        print("No products scraped.")
        return

    available_products = list_available_products(products)
    for p in available_products:
        print(f"Title: {p['title']} - Price: {p['price']} - {p['availability']} - URL: {p['url']}")

    changes = report_changes(products, last_records)
    append_prices(products)
    print(
        f"Scraped {len(products)} products, {len(available_products)} in stock, "
        f"{changes} price/stock change(s)."
    )


if __name__ == "__main__":
    main()