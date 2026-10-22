"""Schreibende Fachfunktionen für Meilensteine, Lieferobjekte, Freigaben, Planversionen und Termine.

Wie in apps.projects.services: Jede Funktion prüft die Rechte selbst, arbeitet in einer
Transaktion und schreibt den Protokolleintrag in derselben Transaktion. Administratoraktionen
werden gekennzeichnet (as_admin).
"""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.audit.services import record
from apps.projects import policies as project_policies
from apps.projects.models import Project

from . import catalog, policies
from .models import (
    Approval,
    ApprovalLight,
    ApprovalParticipant,
    Area,
    DateChange,
    DateKind,
    DatePoint,
    Deliverable,
    DeliverableStatus,
    Milestone,
    MilestoneTemplate,
    PlanEntry,
    PlanEntryKind,
    PlanStatus,
    PlanVersion,
)

KEINE_BEFUGNIS = "Nur Projektleitung und Administrator dürfen das ändern."
WARNUNG_FEHLEND = (
    "Es fehlen Pflichtdokumente. Bitte die Warnung ausdrücklich bestätigen, um trotzdem "
    "freizugeben."
)
WARNUNG_GEAENDERT = (
    "Die fehlenden Pflichtdokumente haben sich seit dem Öffnen des Formulars geändert. "
    "Bitte die aktuelle Liste prüfen und erneut bestätigen."
)
GUELTIG_NUR_KORREKTUR = (
    "Für diesen Meilenstein gibt es eine gültige Freigabe. Eine neue Entscheidung ist nur als "
    "Korrektur der aktuellen Freigabe möglich."
)
ZEITRAUM_GESPERRT = (
    "Der Projektzeitraum ist durch eine genehmigte Planversion festgelegt und ändert sich nur "
    "noch über eine neue Planversion (Termine & Zeitstrahl)."
)


def today():
    return timezone.localdate()


def _lock_project(project):
    return Project.objects.select_for_update().get(pk=project.pk)


def _require_manage(actor, project):
    """Prüft das Schreibrecht und liefert, ob es eine Administratoraktion ist."""
    if not policies.can_manage(actor, project):
        raise PermissionDenied(KEINE_BEFUGNIS)
    return policies.acts_as_admin(policies.can_manage, actor, project)


def _same_project(obj, project, label):
    if obj.project_id != project.pk:
        raise ValidationError(f"{label} gehört nicht zu diesem Projekt.")


def _text(value):
    return (value or "").strip()


# ---------- Projekt anlegen ----------

_MODELS = {
    "MilestoneTemplate": MilestoneTemplate,
    "Milestone": Milestone,
    "Deliverable": Deliverable,
    "PlanVersion": PlanVersion,
    "PlanEntry": PlanEntry,
}


def initialize_project(*, project, actor):
    """Kopiert M0–M5 mit Standard-Lieferobjekten und legt Planversion 1 als Entwurf an.

    Aufruf nur aus apps.projects.services.create_project (prüft dort die Befugnis) in derselben
    Transaktion. Kein eigener Protokolleintrag: Der Eintrag project.created deckt das Anlegen ab.
    """
    if not MilestoneTemplate.objects.exists():
        raise ValidationError("Der Standardkatalog fehlt. Bitte die Migrationen ausführen.")
    catalog.copy_catalog_to_project(_MODELS, project, actor.pk, catalog.PLAN_V1_REASON)


# ---------- Planstände: Abfragen, die auch Services brauchen ----------


def approved_version(project):
    return PlanVersion.objects.filter(project=project, status=PlanStatus.GENEHMIGT).first()


def draft_version(project):
    return PlanVersion.objects.filter(project=project, status=PlanStatus.ENTWURF).first()


def period_locked(project):
    """Nach der ersten Genehmigung ändert sich der Projektzeitraum nur über Planversionen."""
    return PlanVersion.objects.filter(
        project=project, status__in=[PlanStatus.GENEHMIGT, PlanStatus.ABGELOEST]
    ).exists()


def sync_draft_period(project, old_start, old_end):
    """Vor der ersten Genehmigung: Projektzeitraum in den Planentwurf übernehmen.

    Aufruf aus apps.projects.services.update_project in derselben Transaktion. Übernommen wird
    nur, wenn der Entwurfszeitraum noch dem bisherigen Projektzeitraum entspricht; ein bereits
    bearbeiteter Entwurf wird nicht still überschrieben. Rückgabe: True, wenn übernommen.
    """
    if period_locked(project):
        raise ValidationError({"start_date": ZEITRAUM_GESPERRT})
    draft = draft_version(project)
    if draft is None:
        return True
    entry = draft.entries.filter(kind=PlanEntryKind.ZEITRAUM).first()
    if entry is None:
        entry = PlanEntry(project=project, plan_version=draft, kind=PlanEntryKind.ZEITRAUM)
    elif (entry.start_date, entry.end_date) != (old_start, old_end):
        return False
    entry.start_date, entry.end_date = project.start_date, project.end_date
    entry.save()
    return True


# ---------- Meilensteine ----------


@transaction.atomic
def add_milestone(*, actor, project, code, phase_name, title, goal="", after=None):
    """Ergänzt einen eigenen Meilenstein hinter after (sonst am Ende)."""
    project = _lock_project(project)
    as_admin = _require_manage(actor, project)
    code, phase_name, title = _text(code), _text(phase_name), _text(title)
    if not code or not title:
        raise ValidationError("Kürzel und Titel sind erforderlich.")
    if Milestone.objects.filter(project=project, code__iexact=code).exists():
        raise ValidationError({"code": "Dieses Kürzel gibt es im Projekt bereits."})
    ordered = list(Milestone.objects.filter(project=project).order_by("position", "id"))
    insert_at = len(ordered)
    if after is not None:
        _same_project(after, project, "Der Meilenstein")
        insert_at = next(i for i, m in enumerate(ordered) if m.pk == after.pk) + 1
    milestone = Milestone(
        project=project, code=code, phase_name=phase_name, title=title, goal=_text(goal)
    )
    milestone.full_clean(exclude=["position"])
    milestone.save()
    ordered.insert(insert_at, milestone)
    for position, m in enumerate(ordered):
        if m.position != position:
            Milestone.objects.filter(pk=m.pk).update(position=position)
    milestone.refresh_from_db()
    record(
        actor=actor,
        action="milestone.added",
        obj=milestone,
        project=project,
        new={"code": code, "phase_name": phase_name, "title": title, "position": insert_at},
        as_admin=as_admin,
    )
    return milestone


@transaction.atomic
def set_milestone_hidden(*, actor, project, milestone, hidden):
    """Ausblenden statt Löschen: Freigaben und Planstände bleiben erhalten."""
    project = _lock_project(project)
    as_admin = _require_manage(actor, project)
    milestone = Milestone.objects.select_for_update().get(pk=milestone.pk)
    _same_project(milestone, project, "Der Meilenstein")
    hidden = bool(hidden)
    if milestone.is_hidden == hidden:
        return milestone
    milestone.is_hidden = hidden
    milestone.save(update_fields=["is_hidden"])
    record(
        actor=actor,
        action="milestone.hidden" if hidden else "milestone.shown",
        obj=milestone,
        project=project,
        old={"is_hidden": not hidden},
        new={"is_hidden": hidden},
        as_admin=as_admin,
    )
    return milestone


# ---------- Lieferobjekte ----------

DELIVERABLE_FIELDS = ("title", "required", "area", "responsible", "note", "status")


def _deliverable_snapshot(d):
    return {
        "title": d.title,
        "required": d.required,
        "area": d.area,
        "responsible": d.responsible.email if d.responsible_id else None,
        "note": d.note,
        "status": d.status,
    }


def _check_responsible(project, user):
    if user is not None and not policies.can_be_responsible(user, project):
        raise ValidationError(
            {
                "responsible": (
                    "Verantwortlich kann nur ein aktiver Projektleiter oder Mitarbeiter sein."
                )
            }
        )


def _check_choice(value, choices, field):
    if value not in choices.values:
        raise ValidationError({field: "Ungültiger Wert."})


@transaction.atomic
def add_deliverable(
    *,
    actor,
    project,
    milestone,
    title,
    area,
    required=False,
    responsible=None,
    note="",
    status=DeliverableStatus.FEHLT,
):
    project = _lock_project(project)
    as_admin = _require_manage(actor, project)
    _same_project(milestone, project, "Der Meilenstein")
    _check_choice(area, Area, "area")
    _check_choice(status, DeliverableStatus, "status")
    _check_responsible(project, responsible)
    last = milestone.deliverables.order_by("-position").values_list("position", flat=True).first()
    deliverable = Deliverable(
        project=project,
        milestone=milestone,
        title=_text(title),
        required=bool(required),
        area=area,
        responsible=responsible,
        note=_text(note),
        status=status,
        position=(last + 1) if last is not None else 0,
    )
    deliverable.full_clean()
    deliverable.save()
    record(
        actor=actor,
        action="deliverable.added",
        obj=deliverable,
        project=project,
        new={"milestone": milestone.code} | _deliverable_snapshot(deliverable),
        as_admin=as_admin,
    )
    return deliverable


@transaction.atomic
def update_deliverable(*, actor, project, deliverable, **changes):
    project = _lock_project(project)
    as_admin = _require_manage(actor, project)
    unknown = set(changes) - set(DELIVERABLE_FIELDS)
    if unknown:
        raise ValueError(f"Nicht änderbare Felder: {sorted(unknown)}")
    deliverable = Deliverable.objects.select_for_update().get(pk=deliverable.pk)
    _same_project(deliverable, project, "Das Lieferobjekt")
    old = _deliverable_snapshot(deliverable)
    if "area" in changes:
        _check_choice(changes["area"], Area, "area")
    if "status" in changes:
        _check_choice(changes["status"], DeliverableStatus, "status")
    if "responsible" in changes:
        new_resp = changes["responsible"]
        if (new_resp.pk if new_resp else None) != deliverable.responsible_id:
            _check_responsible(project, new_resp)
    for field, value in changes.items():
        if field in ("title", "note"):
            value = _text(value)
        setattr(deliverable, field, value)
    deliverable.full_clean()
    new = _deliverable_snapshot(deliverable)
    changed = [f for f in DELIVERABLE_FIELDS if old[f] != new[f]]
    if not changed:
        return deliverable
    deliverable.save()
    record(
        actor=actor,
        action="deliverable.updated",
        obj=deliverable,
        project=project,
        old={f: old[f] for f in changed},
        new={f: new[f] for f in changed},
        as_admin=as_admin,
    )
    return deliverable


@transaction.atomic
def set_deliverable_status(*, actor, project, deliverable, status):
    """Projektleitung und Admin; außerdem die verantwortliche Person (PL/MA) beim eigenen."""
    project = _lock_project(project)
    deliverable = (
        Deliverable.objects.select_for_update().select_related("project").get(pk=deliverable.pk)
    )
    _same_project(deliverable, project, "Das Lieferobjekt")
    if not policies.can_set_deliverable_status(actor, deliverable):
        raise PermissionDenied("Keine Befugnis, den Status dieses Lieferobjekts zu ändern.")
    as_admin = policies.acts_as_admin(policies.can_set_deliverable_status, actor, deliverable)
    _check_choice(status, DeliverableStatus, "status")
    if deliverable.status == status:
        return deliverable
    old = deliverable.status
    deliverable.status = status
    deliverable.save(update_fields=["status", "updated_at"])
    record(
        actor=actor,
        action="deliverable.status_changed",
        obj=deliverable,
        project=project,
        old={"status": old},
        new={"status": status},
        as_admin=as_admin,
    )
    return deliverable


# ---------- Freigaben ----------


def missing_required(milestone):
    """Pflicht-Lieferobjekte, die noch nicht vorhanden sind (für Warnung und Schnappschuss)."""
    return [
        {"id": d.pk, "title": d.title, "status": d.status}
        for d in milestone.deliverables.filter(required=True)
        .exclude(status=DeliverableStatus.VORHANDEN)
        .order_by("position", "id")
    ]


def current_approval(milestone):
    """Die zuletzt erfasste Freigabe gilt; frühere bleiben als Verlauf sichtbar."""
    return milestone.approvals.order_by("-id").first()


@transaction.atomic
def grant_approval(
    *,
    actor,
    project,
    milestone,
    light,
    decision,
    decided_on,
    participants=(),
    external_participants="",
    basis="",
    conditions="",
    valid_until=None,
    plan_version=None,
    replaces=None,
    confirmed_missing=None,
):
    """Erfasst eine unveränderliche Freigabe. Korrektur: replaces = aktuelle Freigabe.

    confirmed_missing: IDs der fehlenden Pflichtdokumente, deren Warnung bestätigt wurde. Bei
    Grün oder Orange mit fehlenden Pflichtdokumenten muss sie genau der aktuellen Liste
    entsprechen; die Liste wird als Schnappschuss an der Freigabe eingefroren.
    """
    project = _lock_project(project)  # Freigaben eines Projekts nacheinander
    as_admin = _require_manage(actor, project)
    milestone = Milestone.objects.get(pk=milestone.pk)
    _same_project(milestone, project, "Der Meilenstein")
    _check_choice(light, ApprovalLight, "light")
    decision, conditions = _text(decision), _text(conditions)
    errors = {}
    if not decision:
        errors["decision"] = "Bitte die Entscheidung beschreiben."
    if light == ApprovalLight.ORANGE and not conditions:
        errors["conditions"] = "Eine Freigabe unter Auflagen (Orange) verlangt Auflagen."
    if decided_on is None:
        errors["decided_on"] = "Bitte das Datum angeben."
    elif decided_on > today():
        errors["decided_on"] = "Das Datum der Entscheidung darf nicht in der Zukunft liegen."
    elif valid_until is not None and valid_until < decided_on:
        errors["valid_until"] = "„Gültig bis“ darf nicht vor dem Datum der Entscheidung liegen."
    if plan_version is not None and (
        plan_version.project_id != project.pk or plan_version.status == PlanStatus.ENTWURF
    ):
        errors["plan_version"] = "Nur genehmigte Planversionen dieses Projekts sind wählbar."
    if errors:
        raise ValidationError(errors)

    current = current_approval(milestone)
    if replaces is not None and (current is None or replaces.pk != current.pk):
        raise ValidationError(
            "Korrigiert werden kann nur die aktuelle Freigabe dieses Meilensteins."
        )
    if replaces is None and current is not None and current.is_valid_on(today()):
        # Entscheidung Projektleitung: Bei gültiger grüner/oranger Freigabe nur Korrektur
        raise ValidationError(GUELTIG_NUR_KORREKTUR, code="valid_approval_exists")

    participants = list({u.pk: u for u in participants}.values())
    for user in participants:
        if not project_policies.is_active_member(user, project):
            raise ValidationError(
                {"participants": "Beteiligte Konten müssen Projektmitglieder sein."}
            )

    missing = missing_required(milestone)
    warning_confirmed = False
    if missing and light != ApprovalLight.ROT:
        if confirmed_missing is None:
            raise ValidationError(WARNUNG_FEHLEND, code="missing_required")
        if {int(i) for i in confirmed_missing} != {m["id"] for m in missing}:
            raise ValidationError(WARNUNG_GEAENDERT, code="missing_required")
        warning_confirmed = True

    approval = Approval.objects.create(
        project=project,
        milestone=milestone,
        light=light,
        decision=decision,
        decided_on=decided_on,
        external_participants=_text(external_participants),
        basis=_text(basis),
        conditions=conditions,
        valid_until=valid_until,
        plan_version=plan_version,
        missing_required=missing,
        warning_confirmed=warning_confirmed,
        replaces=replaces,
        granted_by=actor,
        as_admin=as_admin,
    )
    for user in participants:
        ApprovalParticipant.objects.create(
            approval=approval, user=user, display_name=user.display_name
        )
    record(
        actor=actor,
        action="approval.corrected" if replaces else "approval.granted",
        obj=approval,
        project=project,
        new={
            "milestone": milestone.code,
            "light": light,
            "decision": decision,
            "decided_on": decided_on,
            "conditions": conditions,
            "valid_until": valid_until,
            "missing_required": [m["title"] for m in missing],
            "warning_confirmed": warning_confirmed,
            "replaces": replaces.pk if replaces else None,
        },
        as_admin=as_admin,
    )
    return approval


# ---------- Planversionen ----------


def _entries_snapshot(version):
    snap = {}
    for e in version.entries.select_related("milestone").order_by("id"):
        if e.kind == PlanEntryKind.ZEITRAUM:
            snap["Zeitraum"] = [e.start_date, e.end_date]
        else:
            snap[e.milestone.code] = e.date
    return snap


def _check_dates_in_period(start, end, milestone_dates):
    errors = []
    for milestone, date in milestone_dates:
        if date is not None and not (start <= date <= end):
            errors.append(f"{milestone.code}: Der Termin liegt außerhalb des Projektzeitraums.")
    if errors:
        raise ValidationError(errors)


@transaction.atomic
def create_plan_draft(*, actor, project, reason):
    """Neuer Entwurf als Kopie des genehmigten Plans (sonst aus dem Projektzeitraum)."""
    project = _lock_project(project)
    as_admin = _require_manage(actor, project)
    reason = _text(reason)
    if not reason:
        raise ValidationError({"reason": "Bitte den Anlass angeben."})
    if draft_version(project) is not None:
        raise ValidationError("Es gibt bereits einen Planentwurf. Bitte diesen bearbeiten.")
    last = PlanVersion.objects.filter(project=project).order_by("-number").first()
    version = PlanVersion.objects.create(
        project=project,
        number=(last.number + 1) if last else 1,
        reason=reason,
        created_by=actor,
    )
    base = approved_version(project)
    if base is not None:
        for e in base.entries.all():
            PlanEntry(
                project=project,
                plan_version=version,
                kind=e.kind,
                milestone_id=e.milestone_id,
                start_date=e.start_date,
                end_date=e.end_date,
                date=e.date,
            ).save()
    else:
        PlanEntry(
            project=project,
            plan_version=version,
            kind=PlanEntryKind.ZEITRAUM,
            start_date=project.start_date,
            end_date=project.end_date,
        ).save()
    record(
        actor=actor,
        action="plan.draft_created",
        obj=version,
        project=project,
        new={"number": version.number, "reason": reason, "based_on": base.number if base else None},
        as_admin=as_admin,
    )
    return version


def _locked_draft(project, version):
    version = PlanVersion.objects.select_for_update().get(pk=version.pk)
    _same_project(version, project, "Die Planversion")
    if version.status != PlanStatus.ENTWURF:
        raise ValidationError(
            "Nur ein Planentwurf kann bearbeitet werden. Genehmigte Versionen sind unveränderlich."
        )
    return version


@transaction.atomic
def update_plan_draft(
    *, actor, project, version, start_date, end_date, milestone_dates, reason=None
):
    """Setzt Projektzeitraum und Meilensteintermine des Entwurfs.

    milestone_dates: Liste von (Meilenstein, Datum oder None); None entfernt den Planeintrag.
    """
    project = _lock_project(project)
    as_admin = _require_manage(actor, project)
    version = _locked_draft(project, version)
    if start_date is None or end_date is None:
        raise ValidationError("Beginn und Ende des Projektzeitraums sind erforderlich.")
    if end_date < start_date:
        raise ValidationError({"end_date": "Das Ende darf nicht vor dem Beginn liegen."})
    milestone_dates = list(milestone_dates)
    for milestone, _date in milestone_dates:
        _same_project(milestone, project, "Der Meilenstein")
    _check_dates_in_period(start_date, end_date, milestone_dates)

    old = _entries_snapshot(version)
    period = version.entries.filter(kind=PlanEntryKind.ZEITRAUM).first() or PlanEntry(
        project=project, plan_version=version, kind=PlanEntryKind.ZEITRAUM
    )
    period.start_date, period.end_date = start_date, end_date
    period.save()
    existing = {e.milestone_id: e for e in version.entries.filter(kind=PlanEntryKind.MEILENSTEIN)}
    for milestone, date in milestone_dates:
        entry = existing.get(milestone.pk)
        if date is None:
            if entry is not None:
                entry.delete()
        elif entry is None:
            PlanEntry(
                project=project,
                plan_version=version,
                kind=PlanEntryKind.MEILENSTEIN,
                milestone=milestone,
                date=date,
            ).save()
        elif entry.date != date:
            entry.date = date
            entry.save()
    if reason is not None and _text(reason) != version.reason:
        version.reason = _text(reason)
        version.save(update_fields=["reason"])
    new = _entries_snapshot(version)
    if new != old:
        record(
            actor=actor,
            action="plan.draft_updated",
            obj=version,
            project=project,
            old=old,
            new=new,
            as_admin=as_admin,
        )
    return version


@transaction.atomic
def approve_plan_version(*, actor, project, version):
    """Genehmigt den Entwurf. Die bisher genehmigte Version wird „abgelöst“.

    Der Projektzeitraum wird dabei auf den genehmigten Zeitraum gesetzt (Synchronisation,
    Abnahmekriterium 11).
    """
    project = _lock_project(project)
    as_admin = _require_manage(actor, project)
    version = _locked_draft(project, version)
    period = version.entries.filter(kind=PlanEntryKind.ZEITRAUM).first()
    if period is None:
        raise ValidationError("Der Entwurf braucht einen Projektzeitraum.")
    _check_dates_in_period(
        period.start_date,
        period.end_date,
        [
            (e.milestone, e.date)
            for e in version.entries.filter(kind=PlanEntryKind.MEILENSTEIN).select_related(
                "milestone"
            )
        ],
    )
    previous = approved_version(project)
    if previous is not None:
        PlanVersion.objects.filter(pk=previous.pk).update(status=PlanStatus.ABGELOEST)
    version.status = PlanStatus.GENEHMIGT
    version.approved_by = actor
    version.approved_at = timezone.now()
    version.approved_as_admin = as_admin
    version.save()
    old_period = [project.start_date, project.end_date]
    project.start_date, project.end_date = period.start_date, period.end_date
    project.save(update_fields=["start_date", "end_date", "updated_at"])
    record(
        actor=actor,
        action="plan.approved",
        obj=version,
        project=project,
        old={
            "project_period": old_period,
            "approved_version": previous.number if previous else None,
        },
        new={
            "project_period": [period.start_date, period.end_date],
            "entries": _entries_snapshot(version),
        },
        as_admin=as_admin,
    )
    return version


# ---------- Prognose und Ist ----------

_PROJECT_FIELDS = {
    (DateKind.PROGNOSE, DatePoint.BEGINN): "forecast_start_date",
    (DateKind.PROGNOSE, DatePoint.ENDE): "forecast_end_date",
    (DateKind.IST, DatePoint.BEGINN): "actual_start_date",
    (DateKind.IST, DatePoint.ENDE): "actual_end_date",
}


@transaction.atomic
def change_date(*, actor, project, kind, value, reason, milestone=None, point=None):
    """Ändert Prognose oder Ist und schreibt einen Verlaufseintrag (alt, neu, Person, Begründung).

    Ohne Meilenstein betrifft die Änderung den Projektzeitraum (point = BEGINN oder ENDE).
    value None entfernt den Wert (ebenfalls mit Begründung).
    """
    project = _lock_project(project)
    as_admin = _require_manage(actor, project)
    _check_choice(kind, DateKind, "kind")
    reason = _text(reason)
    if not reason:
        raise ValidationError({"reason": "Bitte die Änderung begründen."})
    if milestone is not None:
        milestone = Milestone.objects.select_for_update().get(pk=milestone.pk)
        _same_project(milestone, project, "Der Meilenstein")
        point = DatePoint.TERMIN
        target = milestone
        field = "forecast_date" if kind == DateKind.PROGNOSE else "actual_date"
    else:
        if point not in (DatePoint.BEGINN, DatePoint.ENDE):
            raise ValidationError({"point": "Bitte Beginn oder Ende wählen."})
        target = project
        field = _PROJECT_FIELDS[(kind, point)]
    if kind == DateKind.IST and value is not None and value > today():
        raise ValidationError({"value": "Ein Ist-Termin kann nicht in der Zukunft liegen."})
    old = getattr(target, field)
    if old == value:
        raise ValidationError({"value": "Der Wert ist unverändert."})
    setattr(target, field, value)
    if milestone is None:
        prefix = "forecast" if kind == DateKind.PROGNOSE else "actual"
        start, end = (
            getattr(project, f"{prefix}_start_date"),
            getattr(project, f"{prefix}_end_date"),
        )
        if start and end and end < start:
            raise ValidationError({"value": "Das Ende darf nicht vor dem Beginn liegen."})
    target.save(update_fields=[field])
    change = DateChange.objects.create(
        project=project,
        milestone=milestone,
        point=point,
        kind=kind,
        old_value=old,
        new_value=value,
        reason=reason,
        actor=actor,
        as_admin=as_admin,
    )
    record(
        actor=actor,
        action="date.changed",
        obj=change,
        project=project,
        old={
            "target": milestone.code if milestone else "Projekt",
            "point": point,
            "kind": kind,
            "value": old,
        },
        new={"value": value, "reason": reason},
        as_admin=as_admin,
    )
    return change
