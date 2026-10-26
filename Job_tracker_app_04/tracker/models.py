from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.conf import settings

class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    posted_date = models.DateField(null=True, blank=True)
    url = models.URLField(max_length=500, unique=True)
    first_seen = models.DateField(auto_now_add=True)
    last_seen = models.DateField(default=timezone.now)

    class Meta:
        ordering = ('-posted_date','title', 'company')

    def __str__(self):
        return f'{self.title} at {self.company}'

class Application(models.Model):
    class Status(models.TextChoices):
        SAVED = "saved", "Saved"
        APPLIED = "applied", "Applied"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",)
    job = models.ForeignKey(
        Job,
        on_delete=models.PROTECT,
        related_name="applications",)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SAVED
    )
    applied_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    updated_date = models.DateField(auto_now=True)

    class Meta:
        ordering = ["-updated_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "job"],
                name="unique_application_per_user_job",)]

    def __str__(self):
        return f'{self.user} - {self.job} ({self.get_status_display()})'



