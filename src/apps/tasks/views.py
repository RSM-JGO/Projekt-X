"""Seiten für Aufgaben, Buckets und Mein Arbeitsplatz.

Projektaufgaben: unbekannt 404, kein Mitglied 403 („Kein Zugriff“), Aktion nicht erlaubt 403.
Persönliche Aufgaben anderer: 404 (außer Administrator). Die Services prüfen zusätzlich.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from apps.projects import selectors as project_selectors
from apps.projects.views import _add_service_errors

from . import policies, selectors, services
from .forms import BucketForm, TaskForm
from .models import Bucket, TaskEventKind


def _require(allowed):
    if not allowed:
        raise PermissionDenied


def _task_url(task):
    return redirect("tasks:detail", public_id=task.public_id)


# ---------- Mein Arbeitsplatz ----------


@login_required
@require_http_methods(["GET"])
def workplace(request):
    return render(
        request, "tasks/workplace.html", {"workplace": selectors.my_workplace(request.user)}
    )


@login_required
@require_http_methods(["GET", "POST"])
def personal_task_create(request):
    _require(policies.can_create_personal_task(request.user))
    form = TaskForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = {k: v for k, v in form.cleaned_data.items() if k != "version"}
        try:
            task = services.create_personal_task(actor=request.user, **data)
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, "Persönliche Aufgabe angelegt.")
            return _task_url(task)
    return render(request, "tasks/task_form.html", {"form": form, "project": None, "task": None})


# ---------- Projektaufgaben ----------


@login_required
@require_http_methods(["GET", "POST"])
def project_task_create(request, public_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_create_project_task(request.user, project))
    if not selectors.active_buckets(project).exists():
        messages.error(request, "Bitte zuerst einen Bucket anlegen.")
        if policies.can_manage_buckets(request.user, project):
            return redirect("tasks:buckets", public_id=project.public_id)
        return redirect("projects:detail", public_id=project.public_id)
    can_assign = policies.can_manage_assignees(request.user, project)
    initial = {}
    if policies.is_assignable(request.user, project):
        initial["assignees"] = [request.user.pk]
    form = TaskForm(request.POST or None, project=project, initial=initial, can_assign=can_assign)
    if request.method == "POST" and form.is_valid():
        data = {k: v for k, v in form.cleaned_data.items() if k != "version"}
        if not can_assign:
            data["assignees"] = [request.user]  # Mitarbeiter: fest sich selbst zugewiesen
        try:
            task = services.create_project_task(actor=request.user, project=project, **data)
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, "Aufgabe angelegt.")
            return _task_url(task)
    return render(
        request,
        "tasks/task_form.html",
        {
            "form": form,
            "project": project,
            "task": None,
            "fixed_assignees": None if can_assign else [request.user],
            "acts_as_admin": policies.acts_as_admin(
                policies.can_create_project_task, request.user, project
            ),
        },
    )


@login_required
@require_http_methods(["GET"])
def task_detail(request, public_id):
    task = selectors.get_task_for_user(request.user, public_id)
    user = request.user
    return render(
        request,
        "tasks/task_detail.html",
        {
            "task": task,
            "assignees": [a.user for a in task.active_assignments],
            "events": selectors.events(task),
            "overdue": selectors.is_overdue(task),
            "tone": selectors.due_tone(task),
            "is_today": not task.is_done and task.due_date == selectors.today(),
            "can_edit": policies.can_edit_task(user, task),
            "can_complete": policies.can_complete_task(user, task),
            "can_reopen": policies.can_reopen_task(user, task),
            "admin_view": user.is_admin and not policies.can_view_task(user, task, use_admin=False),
            "kinds": TaskEventKind,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def task_edit(request, public_id):
    task = selectors.get_task_for_user(request.user, public_id)
    _require(policies.can_edit_task(request.user, task))
    initial = {
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date,
        "version": task.version,
    }
    if not task.is_personal:
        initial["bucket"] = task.bucket_id
        initial["assignees"] = [a.user_id for a in task.active_assignments]
    can_assign = task.is_personal or policies.can_manage_assignees(request.user, task.project)
    form = TaskForm(
        request.POST or None, project=task.project, initial=initial, can_assign=can_assign
    )
    if request.method == "POST" and form.is_valid():
        data = dict(form.cleaned_data)
        version = data.pop("version")
        assignees = data.pop("assignees", None)
        try:
            services.update_task(
                actor=request.user,
                task=task,
                expected_version=version,
                assignees=assignees,
                **data,
            )
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, "Aufgabe gespeichert.")
            return _task_url(task)
    return render(
        request,
        "tasks/task_form.html",
        {
            "form": form,
            "project": task.project,
            "task": task,
            "fixed_assignees": None if can_assign else [a.user for a in task.active_assignments],
            "acts_as_admin": policies.acts_as_admin(policies.can_edit_task, request.user, task),
        },
    )


@login_required
@require_POST
def task_complete(request, public_id):
    task = selectors.get_task_for_user(request.user, public_id)
    _require(policies.can_complete_task(request.user, task))
    try:
        services.complete_task(actor=request.user, task=task)
    except ValidationError as exc:
        messages.info(request, " ".join(exc.messages))
    else:
        messages.success(request, "Aufgabe abgeschlossen – für alle Zuständigen erledigt.")
    return _task_url(task)


@login_required
@require_POST
def task_reopen(request, public_id):
    task = selectors.get_task_for_user(request.user, public_id)
    _require(policies.can_reopen_task(request.user, task))
    try:
        services.reopen_task(actor=request.user, task=task)
    except ValidationError as exc:
        messages.info(request, " ".join(exc.messages))
    else:
        messages.success(
            request, "Aufgabe wiedergeöffnet. Der frühere Abschluss bleibt im Verlauf."
        )
    return _task_url(task)


# ---------- Buckets ----------


@login_required
@require_http_methods(["GET", "POST"])
def buckets(request, public_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage_buckets(request.user, project))
    form = BucketForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            services.create_bucket(
                actor=request.user, project=project, name=form.cleaned_data["name"]
            )
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, "Bucket angelegt.")
            return redirect("tasks:buckets", public_id=project.public_id)
    return render(
        request,
        "tasks/buckets.html",
        {
            "project": project,
            "buckets": selectors.active_buckets(project),
            "form": form,
            "acts_as_admin": policies.acts_as_admin(
                policies.can_manage_buckets, request.user, project
            ),
        },
    )


@login_required
@require_POST
def bucket_update(request, public_id, bucket_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage_buckets(request.user, project))
    bucket = get_object_or_404(Bucket, pk=bucket_id, project=project, is_archived=False)
    try:
        if request.POST.get("move") in ("up", "down"):
            services.move_bucket(actor=request.user, bucket=bucket, direction=request.POST["move"])
        else:
            services.rename_bucket(actor=request.user, bucket=bucket, name=request.POST.get("name"))
            messages.success(request, "Bucket umbenannt.")
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    return redirect("tasks:buckets", public_id=project.public_id)
