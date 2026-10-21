"""Schreibende Fachfunktionen für Aufgaben und Buckets.

Jede Funktion prüft die Rechte selbst, sperrt die betroffene Zeile (select_for_update),
schreibt den Verlauf in derselben Transaktion und kennzeichnet Administratoraktionen.
"""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Max
from django.db.models.functions import Lower
from django.utils import timezone

from apps.projects.models import Project

from . import policies
from .models import Bucket, Task, TaskAssignment, TaskEvent, TaskEventKind, TaskStatus

EDITABLE_FIELDS = ("title", "description", "due_date", "bucket")
FEHLER_VERSION = (
    "Die Aufgabe wurde inzwischen von einer anderen Person geändert. "
    "Bitte die Seite neu laden und die Änderung erneut eintragen."
)


class TaskConflictError(ValidationError):
    """Versionskonflikt: Die Aufgabe wurde seit dem Laden des Formulars geändert."""


def _event(task, actor, kind, *, old=None, new=None, as_admin=False):
    return TaskEvent.objects.create(
        task=task, actor=actor, kind=kind, old_values=old, new_values=new, as_admin=as_admin
    )


def _lock_task(task):
    return (
        Task.objects.select_for_update(of=("self",))
        .select_related("project", "bucket")
        .get(pk=task.pk)
    )


def _lock_project(project):
    # Gleiche Sperre wie die Mitgliedschafts-Services: Zuweisung und Rollenentzug serialisiert
    return Project.objects.select_for_update().get(pk=project.pk)


def _person(user):
    """Personennennung im Verlauf: ID und Anzeigename zum Zeitpunkt des Ereignisses."""
    return {"user_id": user.pk, "user": user.display_name}


def _lock_task_and_project(task):
    """Sperrreihenfolge wie bei den Mitgliedschafts-Services: erst Projekt, dann Aufgabe."""
    if task.project_id:
        Project.objects.select_for_update().get(pk=task.project_id)
    return _lock_task(task)


def _snapshot(task):
    return {
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date,
        "bucket": {"id": task.bucket_id, "name": task.bucket.name} if task.bucket_id else None,
    }


def _check_bucket(project, bucket):
    if bucket is None or bucket.project_id != project.pk or bucket.is_archived:
        raise ValidationError({"bucket": "Bitte einen aktiven Bucket dieses Projekts wählen."})


def _active_assignees(task):
    return {a.user_id: a for a in TaskAssignment.objects.filter(task=task, ended_at__isnull=True)}


def _set_assignees(task, actor, users, *, as_admin, now):
    """Gleicht Zuweisungen ab und schreibt je Änderung ein Ereignis."""
    users = {u.pk: u for u in users or ()}
    for user in users.values():
        if not policies.is_assignable(user, task.project):
            raise ValidationError(
                {
                    "assignees": f"{user.display_name} ist kein aktiver Projektleiter oder "
                    f"Mitarbeiter dieses Projekts."
                }
            )
    current = _active_assignees(task)
    changed = False
    for user_id, assignment in current.items():
        if user_id not in users:
            assignment.ended_at = now
            assignment.ended_by = actor
            assignment.save(update_fields=["ended_at", "ended_by"])
            _event(
                task,
                actor,
                TaskEventKind.UNASSIGNED,
                old=_person(assignment.user),
                as_admin=as_admin,
            )
            changed = True
    for user_id, user in users.items():
        if user_id not in current:
            TaskAssignment.objects.create(task=task, user=user, assigned_by=actor, assigned_at=now)
            _event(task, actor, TaskEventKind.ASSIGNED, new=_person(user), as_admin=as_admin)
            changed = True
    return changed


# ---------- Anlegen ----------


@transaction.atomic
def create_project_task(
    *, actor, project, bucket, title, description="", due_date=None, assignees=()
):
    project = _lock_project(project)
    if not policies.can_create_project_task(actor, project):
        raise PermissionDenied("Keine Befugnis, in diesem Projekt Aufgaben anzulegen.")
    as_admin = policies.acts_as_admin(policies.can_create_project_task, actor, project)
    _check_bucket(project, bucket)
    if not policies.can_manage_assignees(actor, project) and {u.pk for u in assignees or ()} != {
        actor.pk
    }:
        # Mitarbeiter legen nur Aufgaben an, die ihnen selbst zugewiesen sind
        raise PermissionDenied("Zuständige festlegen dürfen nur Projektleiter und Administrator.")
    task = Task(
        project=project,
        bucket=bucket,
        title=title,
        description=description,
        due_date=due_date,
        created_by=actor,
    )
    task.full_clean()
    task.save()
    _event(task, actor, TaskEventKind.CREATED, new=_snapshot(task), as_admin=as_admin)
    _set_assignees(task, actor, assignees, as_admin=as_admin, now=task.created_at)
    return task


@transaction.atomic
def create_personal_task(*, actor, title, description="", due_date=None):
    if not policies.can_create_personal_task(actor):
        raise PermissionDenied("Keine Befugnis.")
    task = Task(
        owner=actor, title=title, description=description, due_date=due_date, created_by=actor
    )
    task.full_clean()
    task.save()
    _event(task, actor, TaskEventKind.CREATED, new=_snapshot(task))
    return task


# ---------- Ändern ----------


@transaction.atomic
def update_task(*, actor, task, expected_version, assignees=None, **changes):
    """Ändert Felder und (bei Projektaufgaben) Zuweisungen; lehnt veraltete Stände ab."""
    task = _lock_task_and_project(task)
    if not policies.can_edit_task(actor, task):
        raise PermissionDenied("Keine Befugnis, diese Aufgabe zu bearbeiten.")
    as_admin = policies.acts_as_admin(policies.can_edit_task, actor, task)
    unknown = set(changes) - set(EDITABLE_FIELDS)
    if unknown:
        raise ValueError(f"Nicht änderbare Felder: {sorted(unknown)}")
    if expected_version != task.version:
        raise TaskConflictError(FEHLER_VERSION, code="version_conflict")
    if task.is_personal and (changes.get("bucket") or assignees):
        raise ValidationError("Persönliche Aufgaben haben keinen Bucket und keine Zuweisungen.")
    if not task.is_personal and "bucket" in changes:
        _check_bucket(task.project, changes["bucket"])
    if (
        assignees is not None
        and not task.is_personal
        and {u.pk for u in assignees} != set(_active_assignees(task))
        and not policies.can_manage_assignees(actor, task.project)
    ):
        raise PermissionDenied("Zuständige ändern dürfen nur Projektleiter und Administrator.")

    old = _snapshot(task)
    for field, value in changes.items():
        setattr(task, field, value)
    task.full_clean()
    new = _snapshot(task)
    diff = [f for f in old if old[f] != new[f]]
    now = timezone.now()
    if diff:
        _event(
            task,
            actor,
            TaskEventKind.UPDATED,
            old={f: old[f] for f in diff},
            new={f: new[f] for f in diff},
            as_admin=as_admin,
        )
    assignment_changed = False
    if assignees is not None and not task.is_personal:
        assignment_changed = _set_assignees(task, actor, assignees, as_admin=as_admin, now=now)
    if diff or assignment_changed:
        task.version += 1
        task.save()
    return task


@transaction.atomic
def complete_task(*, actor, task):
    """Schließt für alle ab. Die Zeilensperre sorgt bei gleichzeitigen Klicks für genau
    ein Abschlussereignis; der zweite Aufruf erhält eine verständliche Ablehnung."""
    task = _lock_task_and_project(task)
    if not policies.can_complete_task(actor, task):
        raise PermissionDenied("Keine Befugnis, diese Aufgabe abzuschließen.")
    if task.status == TaskStatus.ERLEDIGT:
        raise ValidationError("Die Aufgabe ist bereits erledigt.", code="already_done")
    now = timezone.now()
    task.status = TaskStatus.ERLEDIGT
    task.completed_at = now
    task.completed_by = actor
    task.version += 1
    task.save()
    _event(
        task,
        actor,
        TaskEventKind.COMPLETED,
        as_admin=policies.acts_as_admin(policies.can_complete_task, actor, task),
    )
    return task


@transaction.atomic
def reopen_task(*, actor, task):
    """Öffnet wieder; der frühere Abschluss bleibt im Verlauf (alter Wert im Ereignis)."""
    task = _lock_task_and_project(task)
    if not policies.can_reopen_task(actor, task):
        raise PermissionDenied("Keine Befugnis, diese Aufgabe wiederzuöffnen.")
    if task.status == TaskStatus.OFFEN:
        raise ValidationError("Die Aufgabe ist bereits offen.", code="already_open")
    old = {
        "completed_at": task.completed_at,
        "completed_by_id": task.completed_by_id,
        "completed_by": task.completed_by.display_name,
    }
    task.status = TaskStatus.OFFEN
    task.completed_at = None
    task.completed_by = None
    task.version += 1
    task.save()
    _event(
        task,
        actor,
        TaskEventKind.REOPENED,
        old=old,
        as_admin=policies.acts_as_admin(policies.can_reopen_task, actor, task),
    )
    return task


# ---------- Buckets ----------


def _bucket_audit(actor, bucket, action, old=None, new=None):
    from apps.audit.services import record
    from apps.projects import policies as project_policies

    record(
        actor=actor,
        action=action,
        obj=bucket,
        project=bucket.project,
        old=old,
        new=new,
        as_admin=project_policies.acts_as_admin(actor, bucket.project),
    )


def _check_bucket_name(project, name, exclude_pk=None):
    name = (name or "").strip()
    if not name:
        raise ValidationError({"name": "Bitte einen Namen eingeben."})
    qs = Bucket.objects.annotate(lname=Lower("name")).filter(
        project=project, is_archived=False, lname=name.lower()
    )
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    if qs.exists():
        raise ValidationError({"name": "Diesen Bucket-Namen gibt es im Projekt bereits."})
    return name


@transaction.atomic
def create_bucket(*, actor, project, name):
    project = _lock_project(project)
    if not policies.can_manage_buckets(actor, project):
        raise PermissionDenied("Keine Befugnis, Buckets zu verwalten.")
    name = _check_bucket_name(project, name)
    top = Bucket.objects.filter(project=project).aggregate(m=Max("position"))["m"]
    bucket = Bucket.objects.create(project=project, name=name, position=(top or 0) + 1)
    _bucket_audit(actor, bucket, "bucket.created", new={"name": name})
    return bucket


@transaction.atomic
def rename_bucket(*, actor, bucket, name):
    project = _lock_project(bucket.project)
    if not policies.can_manage_buckets(actor, project):
        raise PermissionDenied("Keine Befugnis, Buckets zu verwalten.")
    bucket = Bucket.objects.get(pk=bucket.pk)
    name = _check_bucket_name(project, name, exclude_pk=bucket.pk)
    if name == bucket.name:
        return bucket
    old = bucket.name
    bucket.name = name
    bucket.save(update_fields=["name"])
    _bucket_audit(actor, bucket, "bucket.renamed", old={"name": old}, new={"name": name})
    return bucket


@transaction.atomic
def move_bucket(*, actor, bucket, direction):
    """Verschiebt einen Bucket um eine Stelle nach links ("up") oder rechts ("down")."""
    project = _lock_project(bucket.project)
    if not policies.can_manage_buckets(actor, project):
        raise PermissionDenied("Keine Befugnis, Buckets zu verwalten.")
    buckets = list(
        Bucket.objects.filter(project=project, is_archived=False).order_by("position", "id")
    )
    index = next(i for i, b in enumerate(buckets) if b.pk == bucket.pk)
    target = index - 1 if direction == "up" else index + 1
    if target < 0 or target >= len(buckets):
        return bucket
    buckets[index], buckets[target] = buckets[target], buckets[index]
    for position, item in enumerate(buckets, start=1):
        if item.position != position:
            item.position = position
            item.save(update_fields=["position"])
    _bucket_audit(actor, buckets[target], "bucket.moved", new={"order": [b.name for b in buckets]})
    return buckets[target]


# ---------- Ausscheiden und Rollenwechsel ----------

GRUND_AUSSCHEIDEN = "wegen Ausscheiden/Rollenwechsel"


def end_assignments_after_role_loss(*, actor, project, user, as_admin=False):
    """Beendet Zuweisungen einer Person in offenen Aufgaben des Projekts.

    Aufruf aus den Mitgliedschafts-Services (Projektzeile ist dort bereits gesperrt), wenn
    die Mitgliedschaft endet oder keine Rolle Projektleiter/Mitarbeiter mehr aktiv ist.
    Erledigte Aufgaben behalten ihre Zuweisungen als historische Zuständigkeit.
    """
    now = timezone.now()
    assignments = (
        TaskAssignment.objects.select_for_update(of=("self",))
        .select_related("task", "user")
        .filter(
            task__project=project,
            task__status=TaskStatus.OFFEN,
            user=user,
            ended_at__isnull=True,
        )
        .order_by("task_id")
    )
    count = 0
    for assignment in assignments:
        task = _lock_task(assignment.task)
        assignment.ended_at = now
        assignment.ended_by = actor
        assignment.save(update_fields=["ended_at", "ended_by"])
        _event(
            task,
            actor,
            TaskEventKind.UNASSIGNED,
            old=_person(user),
            new={"reason": GRUND_AUSSCHEIDEN},
            as_admin=as_admin,
        )
        task.version += 1
        task.save(update_fields=["version", "updated_at"])
        count += 1
    return count
