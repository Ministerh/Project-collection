from django.urls import path

from . import views

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("register/", views.register, name="register"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),
    path("jobs/<int:job_id>/track/", views.track_job, name="track_job"),
    path("applications/", views.application_list, name="application_list"),
    path("applications/<int:pk>/", views.application_edit, name="application_edit"),
    path("applications/<int:pk>/delete/", views.application_delete, name="application_delete"),
    path("dashboard/", views.dashboard, name="dashboard"),
]