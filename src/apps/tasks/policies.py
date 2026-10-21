"""Zentrale Rechteprüfung für Aufgaben und Buckets.

Jede Regel ist als Funktion mit Schalter use_admin geschrieben: Mit use_admin=False wird
geprüft, ob die Person auch ohne Administratorbefugnis dürfte. So lässt sich genau
bestimmen, wann eine Aktion als Administratoraktion zu kennzeichnen ist (Entscheidung 004).
"""

from apps.projects import policies as project_policies
from apps.projects.models import ProjectRole

from .models import TaskAssignment

SCHREIBROLLEN = {ProjectRole.PROJEKTLEITER, ProjectRole.MITARBEITER}


def _active(user):
    return bool(user and user.is_authenticated and user.is_active)


def _admin(user, use_admin):
    return use_admin and user.is_admin


def _roles(user, project):
    return project_policies.active_roles(user, project)


def is_assigned(user, task):
    if not _active(user) or task.pk is None:
        return False
    return TaskAssignment.objects.filter(task=task, user=user, ended_at__isnull=True).exists()


def is_assignable(user, project):
    """Zuweisbar sind nur aktive Projektleiter oder Mitarbeiter mit aktivem Konto."""
    return _active(user) and bool(_roles(user, project) & SCHREIBROLLEN)


# ---------- Lesen ----------


def can_view_task(user, task, *, use_admin=True):
    if not _active(user):
        return False
    if _admin(user, use_admin):
        return True
    if task.is_personal:
        return task.owner_id == user.pk
    return project_policies.is_active_member(user, task.project)


# ---------- Anlegen ----------


def can_create_project_task(user, project, *, use_admin=True):
    if not _active(user):
        return False
    return _admin(user, use_admin) or bool(_roles(user, project) & SCHREIBROLLEN)


def can_create_personal_task(user):
    return _active(user)


# ---------- Ändern ----------


def can_edit_task(user, task, *, use_admin=True):
    """Persönlich: Eigentümer. Projekt: Projektleiter, zugewiesene Mitarbeiter."""
    if not _active(user):
        return False
    if _admin(user, use_admin):
        return True
    if task.is_personal:
        return task.owner_id == user.pk
    roles = _roles(user, task.project)
    if ProjectRole.PROJEKTLEITER in roles:
        return True
    return ProjectRole.MITARBEITER in roles and is_assigned(user, task)


def can_complete_task(user, task, *, use_admin=True):
    """Persönlich: Eigentümer. Projekt: Projektleiter und zugewiesene Personen mit Schreibrolle."""
    if not _active(user):
        return False
    if _admin(user, use_admin):
        return True
    if task.is_personal:
        return task.owner_id == user.pk
    roles = _roles(user, task.project)
    if ProjectRole.PROJEKTLEITER in roles:
        return True
    return bool(roles & SCHREIBROLLEN) and is_assigned(user, task)


def can_reopen_task(user, task, *, use_admin=True):
    """Persönlich: Eigentümer. Projekt: nur Projektleiter (Mitarbeiter nicht)."""
    if not _active(user):
        return False
    if _admin(user, use_admin):
        return True
    if task.is_personal:
        return task.owner_id == user.pk
    return ProjectRole.PROJEKTLEITER in _roles(user, task.project)


def can_manage_assignees(user, project, *, use_admin=True):
    """Zuständige hinzufügen oder entfernen: nur Projektleiter des Projekts und Administrator."""
    if not _active(user):
        return False
    return _admin(user, use_admin) or ProjectRole.PROJEKTLEITER in _roles(user, project)


def can_manage_buckets(user, project, *, use_admin=True):
    if not _active(user):
        return False
    return _admin(user, use_admin) or ProjectRole.PROJEKTLEITER in _roles(user, project)


def acts_as_admin(check, user, *args):
    """True, wenn die Aktion nur dank Administratorbefugnis erlaubt ist."""
    return bool(
        _active(user)
        and user.is_admin
        and check(user, *args)
        and not check(user, *args, use_admin=False)
    )
