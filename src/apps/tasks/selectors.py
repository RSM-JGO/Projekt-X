"""Lesende Abfragen für Aufgaben: Zugriff, Board, Mein Arbeitsplatz, Fälligkeit."""

import datetime

from django.db.models import Prefetch, Q
from django.http import Http404
from django.utils import timezone

from apps.projects.models import ProjectRole
from apps.projects.selectors import KEIN_ZUGRIFF, ProjectAccessDenied

from . import policies
from .models import Bucket, Task, TaskAssignment, TaskEvent, TaskEventKind, TaskStatus

FILTERS = {"offen": "Offen", "erledigt": "Erledigt", "alle": "Alle"}
KUERZLICH_ERLEDIGT_TAGE = 14


# ---------- Fälligkeit (Zeitzone Europe/Berlin aus TIME_ZONE) ----------


def today(now=None):
    """Heutiges Datum in der Ortszeit (Europe/Berlin), nicht in UTC."""
    return timezone.localdate(now)


def is_overdue(task, on=None):
    """Überfällig sind nur offene Aufgaben mit Fälligkeit vor heute."""
    on = on or today()
    return task.status == TaskStatus.OFFEN and task.due_date is not None and task.due_date < on


def due_group(task, on=None):
    """Gruppe für Mein Arbeitsplatz: ueberfaellig, heute, demnaechst, ohne."""
    on = on or today()
    if task.due_date is None:
        return "ohne"
    if task.due_date < on:
        return "ueberfaellig"
    if task.due_date == on:
        return "heute"
    return "demnaechst"


def due_tone(task, on=None):
    """Statusfarbe: rot überfällig, orange heute fällig, grün erledigt, sonst keine."""
    on = on or today()
    if task.status == TaskStatus.ERLEDIGT:
        return "mint"
    if is_overdue(task, on):
        return "rose"
    if task.due_date == on:
        return "peach"
    return ""


# ---------- Zugriff ----------


def _assignments_prefetch():
    return Prefetch(
        "assignments",
        queryset=TaskAssignment.objects.filter(ended_at__isnull=True)
        .select_related("user")
        .order_by("user__display_name"),
        to_attr="active_assignments",
    )


def task_queryset():
    return Task.objects.select_related(
        "project", "bucket", "owner", "completed_by", "created_by"
    ).prefetch_related(_assignments_prefetch())


def get_task_for_user(user, public_id):
    """Unbekannt oder fremde persönliche Aufgabe: 404. Projektaufgabe ohne Mitgliedschaft: 403."""
    task = task_queryset().filter(public_id=public_id).first()
    if task is None:
        raise Http404("Aufgabe nicht gefunden")
    if policies.can_view_task(user, task):
        return task
    if task.is_personal:
        raise Http404("Aufgabe nicht gefunden")
    raise ProjectAccessDenied(KEIN_ZUGRIFF)


FIELD_LABELS = {
    "title": "Titel",
    "description": "Beschreibung",
    "due_date": "Fälligkeit",
    "bucket": "Bucket",
}


def _display(value):
    if value in (None, ""):
        return "–"
    if isinstance(value, dict):
        return value.get("name") or "–"
    if isinstance(value, str) and len(value) == 10 and value[4] == "-" and value[7] == "-":
        try:
            return datetime.date.fromisoformat(value).strftime("%d.%m.%Y")
        except ValueError:
            return value
    return str(value)


def events(task):
    """Verlauf, ältester Eintrag zuerst; Änderungen mit deutschem Feldnamen und alt -> neu."""
    rows = list(
        TaskEvent.objects.filter(task=task).select_related("actor").order_by("created_at", "id")
    )
    for event in rows:
        event.changes = []
        if event.kind == TaskEventKind.UPDATED:
            old, new = event.old_values or {}, event.new_values or {}
            event.changes = [
                (FIELD_LABELS.get(f, f), _display(old.get(f)), _display(new.get(f))) for f in new
            ]
    return rows


def last_completion(task):
    return (
        TaskEvent.objects.filter(task=task, kind=TaskEventKind.COMPLETED)
        .select_related("actor")
        .order_by("-created_at", "-id")
        .first()
    )


# ---------- Projektboard ----------


def active_buckets(project):
    return Bucket.objects.filter(project=project, is_archived=False).order_by("position", "id")


def project_board(project, filter_key="offen"):
    if filter_key not in FILTERS:
        filter_key = "offen"
    tasks = list(task_queryset().filter(project=project).order_by("due_date", "id"))
    counts = {
        "offen": sum(1 for t in tasks if t.status == TaskStatus.OFFEN),
        "erledigt": sum(1 for t in tasks if t.status == TaskStatus.ERLEDIGT),
        "alle": len(tasks),
    }
    if filter_key == "offen":
        tasks = [t for t in tasks if t.status == TaskStatus.OFFEN]
    elif filter_key == "erledigt":
        tasks = [t for t in tasks if t.status == TaskStatus.ERLEDIGT]
    on = today()
    columns = []
    for bucket in active_buckets(project):
        in_bucket = [t for t in tasks if t.bucket_id == bucket.pk]
        columns.append({"bucket": bucket, "tasks": [_card(t, on) for t in in_bucket]})
    return {
        "filter": filter_key,
        "filters": [{"key": k, "label": v, "count": counts[k]} for k, v in FILTERS.items()],
        "columns": columns,
        "visible_count": len(tasks),
    }


def _card(task, on):
    return {
        "task": task,
        "assignees": [a.user for a in task.active_assignments],
        "overdue": is_overdue(task, on),
        "tone": due_tone(task, on),
        "is_today": task.status == TaskStatus.OFFEN and task.due_date == on,
    }


# ---------- Mein Arbeitsplatz ----------


def _my_task_filter(user):
    """Persönlich, mir zugewiesen (in Projekten mit aktiver Mitgliedschaft), geleitete Projekte."""
    member_projects = user.project_memberships.filter(ended_at__isnull=True).values("project_id")
    led_projects = user.project_memberships.filter(
        ended_at__isnull=True,
        role_assignments__role=ProjectRole.PROJEKTLEITER,
        role_assignments__ended_at__isnull=True,
    ).values("project_id")
    assigned = TaskAssignment.objects.filter(user=user, ended_at__isnull=True).values("task_id")
    return (
        Q(owner=user)
        | Q(pk__in=assigned, project_id__in=member_projects)
        | Q(project_id__in=led_projects)
    )


def _origin(task, user, assigned_ids):
    if task.is_personal:
        return "persoenlich"
    if task.pk in assigned_ids:
        return "zugewiesen"
    return "geleitet"


def my_workplace(user, now=None):
    on = today(now)
    qs = task_queryset().filter(_my_task_filter(user)).distinct()
    assigned_ids = set(
        TaskAssignment.objects.filter(user=user, ended_at__isnull=True).values_list(
            "task_id", flat=True
        )
    )
    groups = {"ueberfaellig": [], "heute": [], "demnaechst": [], "ohne": []}
    for task in qs.filter(status=TaskStatus.OFFEN).order_by("due_date", "id"):
        row = _card(task, on) | {"origin": _origin(task, user, assigned_ids)}
        groups[due_group(task, on)].append(row)
    since = timezone.now() - datetime.timedelta(days=KUERZLICH_ERLEDIGT_TAGE)
    done = [
        _card(t, on) | {"origin": _origin(t, user, assigned_ids)}
        for t in qs.filter(status=TaskStatus.ERLEDIGT, completed_at__gte=since).order_by(
            "-completed_at"
        )[:20]
    ]
    return {
        "today": on,
        "groups": [
            {"key": "ueberfaellig", "title": "Überfällig", "rows": groups["ueberfaellig"]},
            {"key": "heute", "title": "Heute fällig", "rows": groups["heute"]},
            {"key": "demnaechst", "title": "Demnächst", "rows": groups["demnaechst"]},
            {"key": "ohne", "title": "Ohne Fälligkeit", "rows": groups["ohne"]},
        ],
        "open_count": sum(len(v) for v in groups.values()),
        "done": done,
    }
