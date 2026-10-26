import requests
from bs4 import BeautifulSoup
from django.template.defaulttags import url
from pip._internal import locations
from pathlib import Path

JOBS_URL = "https://realpython.github.io/fake-jobs/"
HEADERS = {"User-Agent": "job-tracker-practice/1.0"}


# response = requests.get(JOBS_URL, headers=HEADERS, timeout=10)
# response.raise_for_status()
# response.encoding = "utf-8"
# with open("fake-jobs.json", "w") as f:
#     f.write(response.text)
html = Path('fake-jobs.json').read_text()

soup = BeautifulSoup(html, "html.parser")
for tag in soup.select('div.card'):
    result = []
    title = tag.select_one('h2.title.is-5')
    company = tag.select_one('h3.subtitle.is-6.company')
    location = tag.select_one('p.location')
    urls = tag.select_one('footer > a:nth-of-type(2)')['href']
    posted_date = tag.select_one('span.date')
    posted_date = tag.select_one('time')

    result.append({
        "title": title.get_text(strip=True),
        "company": company.get_text(strip=True),
        "location": location.get_text(strip=True),
        "urls": urls,
        "posted_date": posted_date.get_text(strip=True),
    })
    print(result)



