"""Schreibende Fachfunktionen für Projekte und Mitgliedschaften.

Jede Funktion prüft die Rechte selbst (nicht nur die View), arbeitet in einer
Transaktion und schreibt den Protokolleintrag in derselben Transaktion. Bei einem
Regelverstoß wird die gesamte Änderung zurückgerollt.
"""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.audit.services import record
from apps.milestones import services as milestone_services
from apps.tasks import services as task_services

from . import policies
from .models import Project, ProjectMembership, ProjectRole, ProjectRoleAssignment

PROJECT_FIELDS = ("name", "description", "start_date", "end_date")

WRITE_ROLES = {ProjectRole.PROJEKTLEITER, ProjectRole.MITARBEITER}

FEHLER_LETZTER_PL = (
    "Das Projekt braucht mindestens einen aktiven Projektleiter mit aktivem Konto. "
    "Bitte zuerst eine weitere Person als Projektleiter eintragen."
)


def _normalize_roles(roles):
    values = set()
    for role in roles or ():
        if role not in ProjectRole.values:
            raise ValidationError(f"Unbekannte Projektrolle: {role}")
        values.add(ProjectRole(role))
    if not values:
        raise ValidationError(
            "Eine Mitgliedschaft braucht mindestens eine Rolle. "
            "Zum Entfernen bitte „Mitglied entfernen“ verwenden."
        )
    return values


def _sorted_roles(roles):
    order = list(ProjectRole.values)
    return sorted((str(r) for r in roles), key=order.index)


def _lock_project(project):
    """Sperrt die Projektzeile, damit parallele Änderungen die Projektleiterregel nicht umgehen."""
    return Project.objects.select_for_update().get(pk=project.pk)


def _ensure_active_lead(project):
    has_lead = ProjectRoleAssignment.objects.filter(
        membership__project=project,
        membership__ended_at__isnull=True,
        membership__user__is_active=True,
        role=ProjectRole.PROJEKTLEITER,
        ended_at__isnull=True,
    ).exists()
    if not has_lead:
        raise ValidationError(FEHLER_LETZTER_PL)


def _active_role_assignments(membership):
    return membership.role_assignments.filter(ended_at__isnull=True)


def _check_membership(project, membership):
    if membership.project_id != project.pk or not membership.is_active:
        raise ValidationError("Die Mitgliedschaft gehört nicht zu diesem Projekt oder ist beendet.")


def _project_snapshot(project):
    return {field: getattr(project, field) for field in PROJECT_FIELDS}


@transaction.atomic
def create_project(*, actor, name, description="", start_date, end_date):
    """Legt ein Projekt an; die anlegende Person wird automatisch Projektleiter."""
    if not policies.can_create_project(actor):
        raise PermissionDenied("Keine Befugnis zum Anlegen von Projekten.")
    project = Project(
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        created_by=actor,
    )
    project.full_clean()
    project.save()
    record(
        actor=actor,
        action="project.created",
        obj=project,
        project=project,
        new=_project_snapshot(project),
    )
    membership = ProjectMembership.objects.create(project=project, user=actor)
    ProjectRoleAssignment.objects.create(
        membership=membership, role=ProjectRole.PROJEKTLEITER, assigned_by=actor
    )
    record(
        actor=actor,
        action="membership.added",
        obj=membership,
        project=project,
        new={"user": actor.email, "roles": [ProjectRole.PROJEKTLEITER.value]},
    )
    # Etappe 4a: M0–M5 mit Standard-Lieferobjekten und Planversion 1 als Entwurf
    milestone_services.initialize_project(project=project, actor=actor)
    return project


@transaction.atomic
def update_project(*, actor, project, **changes):
    project = _lock_project(project)
    if not policies.can_edit_project(actor, project):
        raise PermissionDenied("Keine Befugnis zum Bearbeiten dieses Projekts.")
    unknown = set(changes) - set(PROJECT_FIELDS)
    if unknown:
        raise ValueError(f"Nicht änderbare Felder: {sorted(unknown)}")
    old = _project_snapshot(project)
    for field, value in changes.items():
        setattr(project, field, value)
    project.full_clean()
    new = _project_snapshot(project)
    changed = [f for f in PROJECT_FIELDS if old[f] != new[f]]
    if not changed:
        return project
    period_changed = "start_date" in changed or "end_date" in changed
    if period_changed and milestone_services.period_locked(project):
        # Nach der ersten Genehmigung nur noch über Planversionen (Abnahmekriterium 11)
        raise ValidationError({"start_date": milestone_services.ZEITRAUM_GESPERRT})
    project.save()
    if period_changed:
        synced = milestone_services.sync_draft_period(project, old["start_date"], old["end_date"])
        # Hinweis für die Oberfläche: bearbeiteter Planentwurf wurde nicht überschrieben
        project.draft_period_kept = not synced
    record(
        actor=actor,
        action="project.updated",
        obj=project,
        project=project,
        old={f: old[f] for f in changed},
        new={f: new[f] for f in changed},
        as_admin=policies.acts_as_admin(actor, project),
    )
    return project


@transaction.atomic
def add_member(*, actor, project, user, roles):
    project = _lock_project(project)  # zuerst sperren, dann Rechte und Regeln prüfen
    if not policies.can_manage_members(actor, project):
        raise PermissionDenied("Keine Befugnis zur Verwaltung der Mitglieder.")
    as_admin = policies.acts_as_admin(actor, project)
    roles = _normalize_roles(roles)
    if not user.is_active:
        raise ValidationError("Deaktivierte Konten können nicht hinzugefügt werden.")
    if ProjectMembership.objects.filter(project=project, user=user, ended_at__isnull=True).exists():
        raise ValidationError("Die Person ist bereits Mitglied dieses Projekts.")
    membership = ProjectMembership.objects.create(project=project, user=user)
    for role in roles:
        ProjectRoleAssignment.objects.create(membership=membership, role=role, assigned_by=actor)
    record(
        actor=actor,
        action="membership.added",
        obj=membership,
        project=project,
        new={"user": user.email, "roles": _sorted_roles(roles)},
        as_admin=as_admin,
    )
    return membership


@transaction.atomic
def change_roles(*, actor, project, membership, roles):
    project = _lock_project(project)  # zuerst sperren, dann Rechte und Regeln prüfen
    if not policies.can_manage_members(actor, project):
        raise PermissionDenied("Keine Befugnis zur Verwaltung der Mitglieder.")
    as_admin = policies.acts_as_admin(actor, project)
    roles = _normalize_roles(roles)
    membership = ProjectMembership.objects.get(pk=membership.pk)
    _check_membership(project, membership)
    now = timezone.now()
    current = {a.role: a for a in _active_role_assignments(membership)}
    old_roles = set(current)
    if old_roles == roles:
        return membership
    for role in old_roles - roles:
        assignment = current[role]
        assignment.ended_at = now
        assignment.ended_by = actor
        assignment.save(update_fields=["ended_at", "ended_by"])
    for role in roles - old_roles:
        ProjectRoleAssignment.objects.create(
            membership=membership, role=role, assigned_by=actor, assigned_at=now
        )
    _ensure_active_lead(project)
    if not roles & WRITE_ROLES:
        # Keine Schreibrolle mehr: Zuweisungen in offenen Aufgaben enden (V07b-Review)
        task_services.end_assignments_after_role_loss(
            actor=actor, project=project, user=membership.user, as_admin=as_admin
        )
    record(
        actor=actor,
        action="membership.roles_changed",
        obj=membership,
        project=project,
        old={"user": membership.user.email, "roles": _sorted_roles(old_roles)},
        new={"user": membership.user.email, "roles": _sorted_roles(roles)},
        as_admin=as_admin,
    )
    return membership


@transaction.atomic
def remove_member(*, actor, project, membership):
    """Beendet die Mitgliedschaft und alle ihre Rollen; der Verlauf bleibt erhalten."""
    project = _lock_project(project)  # zuerst sperren, dann Rechte und Regeln prüfen
    if not policies.can_manage_members(actor, project):
        raise PermissionDenied("Keine Befugnis zur Verwaltung der Mitglieder.")
    as_admin = policies.acts_as_admin(actor, project)
    membership = ProjectMembership.objects.get(pk=membership.pk)
    _check_membership(project, membership)
    now = timezone.now()
    old_roles = set()
    for assignment in _active_role_assignments(membership):
        old_roles.add(assignment.role)
        assignment.ended_at = now
        assignment.ended_by = actor
        assignment.save(update_fields=["ended_at", "ended_by"])
    membership.ended_at = now
    membership.save(update_fields=["ended_at"])
    _ensure_active_lead(project)
    task_services.end_assignments_after_role_loss(
        actor=actor, project=project, user=membership.user, as_admin=as_admin
    )
    record(
        actor=actor,
        action="membership.ended",
        obj=membership,
        project=project,
        old={"user": membership.user.email, "roles": _sorted_roles(old_roles)},
        as_admin=as_admin,
    )
    return membership
