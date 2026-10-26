# Job Tracker (Django)

A web app that collects job listings in one place, lets you search them, and
tracks every application through its stages, so nothing gets lost.

## Screenshots

| Job list | My applications | Dashboard |
|----------|-----------------|-----------|
| ![Job list](screenshots/jobs.png) | ![My applications](screenshots/applications.png) | ![Dashboard](screenshots/dashboard.png) |

## Features

- **Accounts:** register, log in, and log out. Each user sees only their own
  applications.
- **Job import:** a management command scrapes listings from a practice job
  board into the database without creating duplicates.
- **Job list:** search by keyword (title or company), filter by location, and
  paginate. Search terms survive page changes.
- **Job detail:** full listing details, a link to the original, and a
  "Track this job" button.
- **Application tracker:** status (Saved, Applied, Interview, Offer, Rejected),
  applied date, and notes. Edit, filter by status, and delete.
- **Dashboard:** application counts per status and recent activity.
- **Admin:** manage jobs and applications from Django's admin site.

## Setup

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py import_jobs
python manage.py runserver
```

Then open http://127.0.0.1:8000/ and register an account.

## Importing jobs

```
python manage.py import_jobs
```

Example output:

```
Scraped 100 listings: 100 new, 0 already stored.
```

Running it again adds nothing and reports 0 new. Listings are identified by
their URL, which the database enforces as unique. The data comes from
[realpython.github.io/fake-jobs](https://realpython.github.io/fake-jobs/), a
practice site built for scraping.

## Pages

| URL | Purpose |
|-----|---------|
| `/` | Search, filter, and paginate jobs |
| `/jobs/<id>/` | Job detail and "Track this job" |
| `/applications/` | Your applications, filterable by status |
| `/applications/<id>/` | Edit status, date, and notes |
| `/dashboard/` | Totals per status and recent activity |
| `/register/`, `/accounts/login/` | Account access |
| `/admin/` | Django admin |

## Data models

- **Job:** title, company, location, posted date, unique URL, `first_seen`,
  `last_seen`.
- **Application:** user, job, status (limited to five choices), applied date,
  notes, `updated_at`. A user can track a given job only once, enforced by a
  database constraint.

## Security notes

- Every application lookup is scoped to the logged-in user, so another user's
  record returns a 404.
- Pages that change data require login. Deletes and tracking are POST-only and
  CSRF-protected.
- The status filter ignores values that aren't valid choices.

## Tests

```
python manage.py test
```

Automated tests cover import deduplication, keyword search, one-application-
per-user-per-job, access control between two users, and status validation.

## Project structure

```
Job_tracker_app_04/
├── manage.py
├── jobber/        project settings and root URLs
├── tracker/       models, views, forms, tests, and the import command
├── templates/     base, login/register, and tracker pages
└── requirements.txt
```

## Tech

Python 3, Django, `requests`, `beautifulsoup4`, SQLite for development, and
Django's built-in authentication.

## Limitations

- Imports from one practice site, so a real job board would need its own
  parser (and permission to scrape it).
- The import runs manually and isn't scheduled.
- SQLite is used for development, and production would need PostgreSQL and
  proper settings.

## Ideas for next steps

- Scheduled imports (Celery or Task Scheduler).
- Export applications to CSV.
- A status-history timeline per application.
- A read-only REST endpoint for applications.

## What I learned

(Fill this in after building it.)
