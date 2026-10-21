"""Änderungen an Konten und Befugnissen.

Alle Wege (Django-Admin, spätere Administrationsoberfläche, Befehle) sollen diese Funktionen
nutzen, damit die Projektleiterregel greift und jede Befugnisänderung protokolliert wird.
"""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Exists, OuterRef

from apps.audit.services import record

ACCOUNT_FLAGS = (
    "is_active",
    "is_admin",
    "can_create_projects",
    "can_delete_projects",
    "is_staff",
    "is_superuser",
)


def _project_models():
    # Später Import, damit accounts beim Laden nicht von projects abhängt
    from apps.projects.models import Project, ProjectRole, ProjectRoleAssignment

    return Project, ProjectRole, ProjectRoleAssignment


def _lead_projects(user):
    Project, ProjectRole, ProjectRoleAssignment = _project_models()
    lead_project_ids = ProjectRoleAssignment.objects.filter(
        membership__user=user,
        membership__ended_at__isnull=True,
        ended_at__isnull=True,
        role=ProjectRole.PROJEKTLEITER,
    ).values("membership__project_id")
    return Project.objects.filter(pk__in=lead_project_ids)


def sole_lead_projects(user):
    """Projekte, in denen die Person der einzige aktive Projektleiter mit aktivem Konto ist."""
    Project, ProjectRole, ProjectRoleAssignment = _project_models()
    other_leads = ProjectRoleAssignment.objects.filter(
        membership__project=OuterRef("pk"),
        membership__ended_at__isnull=True,
        membership__user__is_active=True,
        ended_at__isnull=True,
        role=ProjectRole.PROJEKTLEITER,
    ).exclude(membership__user=user)
    return list(_lead_projects(user).exclude(Exists(other_leads)).order_by("name"))


def ensure_can_deactivate(user, *, lock=False):
    """Lehnt die Deaktivierung ab, wenn die Person einziger aktiver Projektleiter ist.

    Mit lock=True werden die betroffenen Projektzeilen gesperrt (innerhalb einer Transaktion),
    damit eine gleichzeitige Mitgliederänderung die Regel nicht umgehen kann; die
    Projekt-Services sperren dieselben Zeilen.
    """
    if lock:
        list(_lead_projects(user).select_for_update().order_by("pk").values_list("pk", flat=True))
    projects = sole_lead_projects(user)
    if projects:
        names = ", ".join(f"„{p.name}“" for p in projects)
        raise ValidationError(
            f"Das Konto kann nicht deaktiviert werden: Die Person ist einziger aktiver "
            f"Projektleiter in {names}. Bitte zuerst eine weitere Person als Projektleiter "
            f"eintragen.",
            code="sole_project_lead",
        )


def account_snapshot(user):
    return {field: getattr(user, field) for field in ACCOUNT_FLAGS}


def record_account_changes(*, actor, user, old):
    """Protokolliert geänderte Befugnisse (old=None: Konto neu angelegt)."""
    new = account_snapshot(user)
    if old is None:
        return record(actor=actor, action="account.created", obj=user, new=new)
    changed = [f for f in ACCOUNT_FLAGS if old[f] != new[f]]
    if not changed:
        return None
    return record(
        actor=actor,
        action="account.flags_changed",
        obj=user,
        old={f: old[f] for f in changed},
        new={f: new[f] for f in changed},
    )


def _may_manage_accounts(actor):
    return bool(
        actor
        and actor.is_authenticated
        and actor.is_active
        and (actor.is_admin or actor.is_superuser)
    )


@transaction.atomic
def update_account_flags(*, actor, user, **changes):
    """Ändert Befugnisse eines Kontos mit Regelprüfung und Protokoll."""
    if not _may_manage_accounts(actor):
        raise PermissionDenied("Keine Befugnis zur Kontoverwaltung.")
    unknown = set(changes) - set(ACCOUNT_FLAGS)
    if unknown:
        raise ValueError(f"Nicht änderbare Felder: {sorted(unknown)}")
    user = type(user).objects.select_for_update().get(pk=user.pk)
    old = account_snapshot(user)
    if old["is_active"] and changes.get("is_active") is False:
        ensure_can_deactivate(user, lock=True)
    for field, value in changes.items():
        setattr(user, field, value)
    user.save(update_fields=list(changes) or None)
    record_account_changes(actor=actor, user=user, old=old)
    return user
