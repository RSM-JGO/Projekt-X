"""Zentrale Rechteprüfung für Projekte.

Jede Funktion ist einzeln testbar und wird sowohl von Views als auch von den
schreibenden Services aufgerufen. Die Oberfläche blendet Schaltflächen nur zusätzlich aus.
"""

from .models import ProjectRole, ProjectRoleAssignment


def _is_active_account(user):
    return bool(user and user.is_authenticated and user.is_active)


def active_roles(user, project):
    """Aktive Projektrollen der Person im Projekt (Menge von ProjectRole-Werten)."""
    if not _is_active_account(user) or project is None or project.pk is None:
        return set()
    return set(
        ProjectRoleAssignment.objects.filter(
            membership__project=project,
            membership__user=user,
            membership__ended_at__isnull=True,
            ended_at__isnull=True,
        ).values_list("role", flat=True)
    )


def is_active_member(user, project):
    if not _is_active_account(user):
        return False
    return project.memberships.filter(user=user, ended_at__isnull=True).exists()


def can_view_project(user, project):
    """Projekt öffnen (Detail und Unterseiten): aktive Mitglieder jeder Rolle und Administrator.

    Die Projektübersicht zeigt allen Angemeldeten Eckdaten aller Projekte; das ist kein Öffnen.
    """
    if not _is_active_account(user):
        return False
    return user.is_admin or is_active_member(user, project)


def can_create_project(user):
    if not _is_active_account(user):
        return False
    return user.is_admin or user.can_create_projects


def can_edit_project(user, project):
    """Projektleiter des Projekts; der Administrator darf alles (Entscheidung 004)."""
    if not _is_active_account(user):
        return False
    return user.is_admin or ProjectRole.PROJEKTLEITER in active_roles(user, project)


def can_manage_members(user, project):
    if not _is_active_account(user):
        return False
    return user.is_admin or ProjectRole.PROJEKTLEITER in active_roles(user, project)


def acts_as_admin(user, project):
    """True, wenn die Person nur über die Administratorbefugnis handelt (wird protokolliert)."""
    return bool(
        _is_active_account(user)
        and user.is_admin
        and ProjectRole.PROJEKTLEITER not in active_roles(user, project)
    )
