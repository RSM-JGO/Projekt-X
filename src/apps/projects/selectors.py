"""Lesende Abfragen. Zugriff und Sichtbarkeit von Projekten werden ausschließlich hier bestimmt.

Entscheidung 004: Alle Angemeldeten sehen in der Übersicht alle Projekte, fremde aber nur mit
Eckdaten (Name, Zeitraum, Projektleitung). Öffnen dürfen nur aktive Mitglieder und Administratoren.
"""

from typing import NamedTuple

from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import Http404

from . import policies
from .models import Project, ProjectMembership, ProjectRole, ProjectRoleAssignment

KEIN_ZUGRIFF = "Kein Zugriff auf dieses Projekt"


class ProjectAccessDenied(PermissionDenied):
    """Projekt existiert, die Person ist aber kein aktives Mitglied (403)."""


class LeadInfo(NamedTuple):
    """Nur Anzeigename der Projektleitung für Projekte ohne Zugriff."""

    pk: int
    display_name: str


def _active_account(user):
    return bool(user and user.is_authenticated and user.is_active)


def accessible_projects(user):
    """Projekte, die die Person öffnen darf: aktive Mitgliedschaft; Administrator alle."""
    if not _active_account(user):
        return Project.objects.none()
    if user.is_admin:
        return Project.objects.all()
    return Project.objects.filter(
        memberships__user=user, memberships__ended_at__isnull=True
    ).distinct()


def get_accessible_project(user, public_id):
    """Unbekannte ID: 404. Bekanntes Projekt ohne Zugriff: 403 (ohne Projektdaten)."""
    project = Project.objects.filter(public_id=public_id).first()
    if project is None:
        raise Http404("Projekt nicht gefunden")
    if not policies.can_view_project(user, project):
        raise ProjectAccessDenied(KEIN_ZUGRIFF)
    return project


def _active_roles_prefetch():
    return Prefetch(
        "role_assignments",
        queryset=ProjectRoleAssignment.objects.filter(ended_at__isnull=True).order_by("role"),
        to_attr="active_role_list",
    )


def active_memberships(project):
    return (
        ProjectMembership.objects.filter(project=project, ended_at__isnull=True)
        .select_related("user")
        .prefetch_related(_active_roles_prefetch())
        .order_by("user__display_name", "user__email")
    )


def get_active_membership_or_404(project, membership_id):
    try:
        return active_memberships(project).get(pk=membership_id)
    except ProjectMembership.DoesNotExist:
        raise Http404("Mitgliedschaft nicht gefunden") from None


def membership_rows(project):
    """Aktive Mitglieder mit Rollen (Werte und Beschriftungen) für die Anzeige."""
    rows = []
    for membership in active_memberships(project):
        roles = [a.role for a in membership.active_role_list]
        rows.append(
            {
                "membership": membership,
                "user": membership.user,
                "roles": [ProjectRole(r) for r in roles],
                "is_lead": ProjectRole.PROJEKTLEITER in roles,
            }
        )
    return rows


def _leads_by_project(project_ids):
    leads = {}
    rows = (
        ProjectRoleAssignment.objects.filter(
            membership__project_id__in=project_ids,
            membership__ended_at__isnull=True,
            role=ProjectRole.PROJEKTLEITER,
            ended_at__isnull=True,
        )
        .order_by("membership__user__display_name")
        .values_list(
            "membership__project_id", "membership__user_id", "membership__user__display_name"
        )
    )
    for project_id, user_id, display_name in rows:
        leads.setdefault(project_id, []).append(LeadInfo(user_id, display_name))
    return leads


def project_overview(user):
    """Projektübersicht, getrennt nach Projekten mit Zugriff und weiteren Projekten.

    Für weitere Projekte werden nur Name, Zeitraum und Projektleitung geladen; weder das
    Projektobjekt noch Beschreibung, öffentliche ID oder Mitglieder gelangen ins Template.
    """
    if not _active_account(user):
        return {"accessible": [], "others": []}
    accessible = accessible_projects(user).prefetch_related(
        Prefetch(
            "memberships",
            queryset=ProjectMembership.objects.filter(ended_at__isnull=True)
            .select_related("user")
            .prefetch_related(_active_roles_prefetch())
            .order_by("user__display_name"),
            to_attr="active_membership_list",
        )
    )
    accessible_rows = []
    for project in accessible:
        leads, my_roles = [], []
        for membership in project.active_membership_list:
            roles = [a.role for a in membership.active_role_list]
            if ProjectRole.PROJEKTLEITER in roles:
                leads.append(membership.user)
            if membership.user_id == user.pk:
                my_roles = [ProjectRole(r) for r in roles]
        accessible_rows.append({"project": project, "leads": leads, "my_roles": my_roles})

    others = list(
        Project.objects.exclude(pk__in=accessible.values("pk"))
        .order_by("name", "id")
        .values("pk", "name", "start_date", "end_date")
    )
    leads = _leads_by_project([p["pk"] for p in others])
    other_rows = [
        {
            "name": p["name"],
            "start_date": p["start_date"],
            "end_date": p["end_date"],
            "leads": leads.get(p["pk"], []),
        }
        for p in others
    ]
    return {"accessible": accessible_rows, "others": other_rows}
