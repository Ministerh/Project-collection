from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from tracker.forms import ApplicationForm
from tracker.management.commands.import_jobs import save_listings
from tracker.models import Application, Job

User = get_user_model()


def make_job(title="Python Developer", company="Acme", n=1):
    return Job.objects.create(
        title=title,
        company=company,
        location="Remote",
        url=f"https://example.com/jobs/{n}",
    )


class ImportTests(TestCase):
    def test_saving_same_listing_twice_creates_one_job(self):
        listings = [{
            "title": "Python Developer",
            "company": "Acme",
            "location": "Remote",
            "posted_date": date(2021, 4, 8),
            "url": "https://example.com/jobs/1",
        }]
        self.assertEqual(save_listings(listings), 1)

        job = Job.objects.get()
        first_seen, last_seen = job.first_seen, job.last_seen

        self.assertEqual(save_listings(listings), 0)
        self.assertEqual(Job.objects.count(), 1)

        job.refresh_from_db()
        self.assertEqual(job.first_seen, first_seen)
        self.assertGreaterEqual(job.last_seen, last_seen)


class JobSearchTests(TestCase):
    def test_search_matches_title_or_company_only(self):
        make_job("Python Developer", "Acme", n=1)
        make_job("Java Engineer", "Beta", n=2)
        make_job("Data Scientist", "Python Labs", n=3)

        response = self.client.get(reverse("job_list"), {"q": "python"})

        self.assertContains(response, "Python Developer")
        self.assertContains(response, "Data Scientist")
        self.assertNotContains(response, "Java Engineer")


class TrackingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="pass12345")
        self.job = make_job()

    def test_database_blocks_duplicate_application(self):
        Application.objects.create(user=self.user, job=self.job)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Application.objects.create(user=self.user, job=self.job)

    def test_tracking_twice_creates_one_application(self):
        self.client.force_login(self.user)
        url = reverse("track_job", args=[self.job.pk])
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(
            Application.objects.filter(user=self.user, job=self.job).count(), 1
        )


class AccessControlTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        self.job = make_job()
        self.app = Application.objects.create(user=self.alice, job=self.job)

    def test_owner_can_open_their_application(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("application_edit", args=[self.app.pk]))
        self.assertEqual(response.status_code, 200)

    def test_other_user_gets_404_on_edit(self):
        self.client.force_login(self.bob)
        response = self.client.get(reverse("application_edit", args=[self.app.pk]))
        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_delete(self):
        self.client.force_login(self.bob)
        response = self.client.post(reverse("application_delete", args=[self.app.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Application.objects.filter(pk=self.app.pk).exists())

    def test_other_user_does_not_see_application_in_list(self):
        self.client.force_login(self.bob)
        response = self.client.get(reverse("application_list"))
        self.assertNotContains(response, self.job.title)

    def test_anonymous_user_is_redirected_to_login(self):
        url = reverse("application_list")
        response = self.client.get(url)
        self.assertRedirects(
            response, f"{reverse('login')}?next={url}", fetch_redirect_response=False
        )


class StatusValidationTests(TestCase):
    def test_invalid_status_is_rejected_by_form(self):
        form = ApplicationForm(data={"status": "banana", "applied_date": "", "notes": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("status", form.errors)

    def test_valid_status_is_accepted_by_form(self):
        form = ApplicationForm(data={"status": "applied", "applied_date": "", "notes": ""})
        self.assertTrue(form.is_valid())

    def test_invalid_status_does_not_change_application(self):
        user = User.objects.create_user("alice", password="pass12345")
        app = Application.objects.create(user=user, job=make_job())
        self.client.force_login(user)

        self.client.post(
            reverse("application_edit", args=[app.pk]),
            {"status": "banana", "applied_date": "", "notes": ""},
        )

        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.SAVED)