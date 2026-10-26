from django.contrib import admin

from .models import Application, Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "posted_date", "last_seen")
    search_fields = ("title", "company")
    readonly_fields = ("first_seen",)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "status", "applied_date", "updated_date")
    list_filter = ("status",)