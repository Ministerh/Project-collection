from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from tracker.models import Job

JOBS_URL = "https://realpython.github.io/fake-jobs/"
HEADERS = {"User-Agent": "job-tracker-practice/1.0"}
DATE_FORMATS = ("%Y-%m-%d", "%B %d, %Y")


def parse_date(text):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def fetch():
    response = requests.get(JOBS_URL,headers=HEADERS, timeout=10)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return response.text

def fetch_listings():
    soup = BeautifulSoup(fetch(), "html.parser")
    container = soup.find(id="ResultsContainer")
    if container is None:
        raise ValueError("Could not find the results container on the page.")

    job_listings = []
    for card in container.select("div.card"):
        title = card.select_one("h2.title.is-5")
        company = card.select_one("h3.subtitle.is-6.company")
        location = card.select_one("p.location")
        apply_link = card.select_one("footer > a:nth-of-type(2)")
        posted = card.select_one("time")

        if title is None or apply_link is None:
            continue

        date_text = ""
        if posted:
            date_text = posted.get("datetime") or posted.get_text(strip=True)

        job_listings.append({
            "title": title.get_text(strip=True),
            "company": company.get_text(strip=True) if company else "",
            "location": location.get_text(strip=True) if location else "",
            "url": urljoin(JOBS_URL, apply_link["href"]),
            "posted_date": parse_date(date_text),
        })
    return job_listings


def save_listings(listings):
    new_count = 0
    now = timezone.now()
    for item in listings:
        _, created = Job.objects.update_or_create(
            url=item["url"],
            defaults={
                "title": item["title"],
                "company": item["company"],
                "location": item["location"],
                "posted_date": item["posted_date"],
                "last_seen": now,
            },
        )
        if created:
            new_count += 1
    return new_count

class Command(BaseCommand):
    help = "Scrape job listings from the practice job board and save them."

    def handle(self, *args, **options):
        try:
            listings = fetch_listings()
        except (requests.RequestException, ValueError) as err:
            raise CommandError(f"Import failed: {err}")

        if not listings:
            self.stdout.write(self.style.WARNING("No listings found."))
            return

        new_count = save_listings(listings)
        existing = len(listings) - new_count
        self.stdout.write(self.style.SUCCESS(
            f"Scraped {len(listings)} listings: {new_count} new, {existing} already stored."
        ))
