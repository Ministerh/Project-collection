from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Application, Job
from .forms import ApplicationForm



def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user =form.save()
            login(request, user)
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def job_list(request):
    q = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()

    jobs = Job.objects.all()
    if q:
        jobs = jobs.filter(Q(title__icontains=q) | Q(company__icontains=q))
    if location:
        jobs = jobs.filter(location__icontains=location)

    paginator = Paginator(jobs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    return render(request, "tracker/job_list.html", {
        "page_obj": page_obj,
        "q": q,
        "location": location,
        "query_string": params.urlencode(),
    })

def job_detail(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    application = None
    if request.user.is_authenticated:
        application = Application.objects.filter(user=request.user, job=job).first()
    return render(request, "tracker/job_detail.html", {
        'job': job,
        'application': application})

@login_required
@require_POST
def track_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    Application.objects.get_or_create(user=request.user, job=job)
    return redirect('job_detail', job_id=job.pk)


@login_required
def application_list(request):
    applications = Application.objects.filter(user=request.user).select_related("job")
    status = request.GET.get("status", "")
    if status in Application.Status.values:
        applications = applications.filter(status=status)
    else:
        status = ""
    return render(request, "tracker/application_list.html", {
        "applications": applications,
        "status": status,
        "status_choices": Application.Status.choices,
    })


@login_required
def application_edit(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == "POST":
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect("application_list")
    else:
        form = ApplicationForm(instance=application)
    return render(request, "tracker/application_form.html", {
        "form": form,
        "application": application,
    })


@login_required
@require_POST
def application_delete(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    application.delete()
    return redirect("application_list")

@login_required
def dashboard(request):
    applications = Application.objects.filter(user=request.user)

    rows = applications.values("status").annotate(total=Count("id"))
    counts = {row["status"]: row["total"] for row in rows}
    status_counts = [
        (value, label, counts.get(value, 0))
        for value, label in Application.Status.choices
    ]

    return render(request, "tracker/dashboard.html", {
        "status_counts": status_counts,
        "total": applications.count(),
        "recent": applications.select_related("job")[:5],
    })