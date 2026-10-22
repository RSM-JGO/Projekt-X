"""Lesende Abfragen und abgeleiteter Status (berechnet, nicht gespeichert).

Regeln (docs/entwurf-datenmodell-projektbereich.md, Benutzerentscheidungen 22.10.2026):
- Aktueller Meilenstein = erster sichtbare ohne gültige grüne oder orange Freigabe. Rot oder
  abgelaufen („gültig bis“ vor heute) zählt als offen.
- Ein Meilenstein ohne Lieferobjekte oder ohne Termin ist „nicht bewertet“, nie erledigt/grün.
  Termin = genehmigter Plan, Prognose oder Ist (ein Entwurf ist noch kein Termin).
- Ursprünglicher Plan = erste genehmigte Planversion, die das Objekt enthält; genehmigter Plan
  = aktuell genehmigte Version.
"""

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

from apps.projects.models import ProjectRole
from apps.tasks.models import Task, TaskStatus

from .models import (
    Approval,
    ApprovalLight,
    DateChange,
    Deliverable,
    DeliverableStatus,
    Milestone,
    PlanEntry,
    PlanEntryKind,
    PlanStatus,
    PlanVersion,
)

# Status immer mit Symbol und Text; Farbe nur am Symbol (Styleguide)
RATING = {
    "done": {"icon": "✓", "label": "erledigt", "tone": "mint"},
    "partial": {"icon": "●", "label": "offen", "tone": "peach"},
    "todo": {"icon": "○", "label": "nicht begonnen", "tone": "neutral"},
    "unrated": {"icon": "–", "label": "nicht bewertet", "tone": "neutral"},
}
DELIVERABLE_MARKER = {
    DeliverableStatus.VORHANDEN: {"icon": "✓", "label": "vorhanden", "tone": "mint"},
    DeliverableStatus.IN_ARBEIT: {"icon": "●", "label": "in Arbeit", "tone": "peach"},
    DeliverableStatus.FEHLT: {"icon": "○", "label": "fehlt", "tone": "neutral"},
}
APPROVAL_MARKER = {
    ApprovalLight.GRUEN: {"icon": "✓", "label": "Freigabe erteilt", "tone": "mint"},
    ApprovalLight.ORANGE: {"icon": "!", "label": "unter Auflagen", "tone": "peach"},
    ApprovalLight.ROT: {"icon": "✕", "label": "keine Freigabe", "tone": "rose"},
    "open": {"icon": "○", "label": "Freigabe offen", "tone": "neutral"},
    "expired": {"icon": "○", "label": "Freigabe abgelaufen", "tone": "neutral"},
}

# Bereiche in der Reihenfolge aus Entscheidung 006; URL-Name None = folgt später
SECTIONS = (
    ("uebersicht", "Übersicht", "projects:detail"),
    ("steckbrief", "Steckbrief & Auftrag", None),
    ("kommunikation", "Kommunikation", None),
    ("termine", "Termine & Zeitstrahl", "milestones:schedule"),
    ("aufgaben", "Aufgaben", "tasks:board"),
    ("risiken", "Risiken & Chancen", None),
    ("aenderungen", "Änderungen & Entscheidungen", None),
    ("produkt", "Produkt & Pilot", None),
    ("berichte", "Berichte", None),
    ("dokumente", "Dokumente", None),
    ("abschluss", "Abschluss & Lessons Learned", None),
)
SECTION_URLS = {key: url for key, _label, url in SECTIONS}


def today():
    return timezone.localdate()


def rating(deliverables, has_date=True):
    """Abgeleiteter Status einer Menge von Lieferobjekten."""
    if not deliverables or not has_date:
        return RATING["unrated"]
    statuses = {d.status for d in deliverables}
    if statuses == {DeliverableStatus.VORHANDEN}:
        return RATING["done"]
    if statuses == {DeliverableStatus.FEHLT}:
        return RATING["todo"]
    return RATING["partial"]


def section_url(project, area):
    url_name = SECTION_URLS.get(area)
    return reverse(url_name, args=[project.public_id]) if url_name else None


# ---------- Planstände ----------


def plan_overview(project):
    """Ursprünglicher und genehmigter Plan je Meilenstein und für den Projektzeitraum."""
    entries = (
        PlanEntry.objects.filter(
            project=project, plan_version__status__in=[PlanStatus.GENEHMIGT, PlanStatus.ABGELOEST]
        )
        .select_related("plan_version")
        .order_by("plan_version__number", "id")
    )
    original, approved = {}, {}
    approved_version = None
    for e in entries:
        key = "period" if e.kind == PlanEntryKind.ZEITRAUM else e.milestone_id
        value = (e.start_date, e.end_date) if key == "period" else e.date
        original.setdefault(key, (value, e.plan_version.number))
        if e.plan_version.status == PlanStatus.GENEHMIGT:
            approved[key] = value
            approved_version = e.plan_version
    return {
        "original": original,
        "approved": approved,
        "approved_version": approved_version
        or PlanVersion.objects.filter(project=project, status=PlanStatus.GENEHMIGT).first(),
        "draft": PlanVersion.objects.filter(project=project, status=PlanStatus.ENTWURF).first(),
    }


# ---------- Meilensteinzustand ----------


def _milestones(project):
    return Milestone.objects.filter(project=project).prefetch_related(
        Prefetch(
            "deliverables",
            queryset=Deliverable.objects.select_related("responsible").order_by("position", "id"),
        ),
        Prefetch(
            "approvals",
            queryset=Approval.objects.select_related("granted_by", "plan_version")
            .prefetch_related("participant_links")
            .order_by("id"),
        ),
    )


def journey(project, on=None):
    """Zustand aller Meilensteine; sichtbare in Reihenfolge, aktueller Meilenstein markiert."""
    on = on or today()
    plans = plan_overview(project)
    states = []
    for m in _milestones(project).order_by("position", "id"):
        deliverables = list(m.deliverables.all())
        approvals = list(m.approvals.all())
        replaced_ids = {a.replaces_id for a in approvals if a.replaces_id}
        effective = approvals[-1] if approvals else None
        valid = bool(effective and effective.is_valid_on(on))
        if effective is None:
            approval_marker = APPROVAL_MARKER["open"]
        elif effective.is_positive and not valid:
            approval_marker = APPROVAL_MARKER["expired"]
        else:
            approval_marker = APPROVAL_MARKER[effective.light]
        planned = plans["approved"].get(m.pk)
        original = plans["original"].get(m.pk)
        has_date = bool(planned or m.forecast_date or m.actual_date)
        present = sum(1 for d in deliverables if d.is_present)
        total = len(deliverables)
        states.append(
            {
                "milestone": m,
                "deliverables": deliverables,
                "total": total,
                "present": present,
                "open": total - present,
                "percent": round(present * 100 / total) if total else 0,
                "required_missing": [d for d in deliverables if d.required and not d.is_present],
                "rating": rating(deliverables, has_date),
                "has_date": has_date,
                "approvals": [
                    {
                        "approval": a,
                        "replaced": a.pk in replaced_ids,
                        "marker": APPROVAL_MARKER[a.light],
                    }
                    for a in reversed(approvals)
                ],
                "approval": effective,
                "approval_valid": valid,
                "approval_expired": bool(effective and effective.is_positive and not valid),
                "approval_marker": approval_marker,
                "planned_date": planned,
                "original_date": original[0] if original else None,
                "original_version": original[1] if original else None,
                "forecast_date": m.forecast_date,
                "actual_date": m.actual_date,
                "date": m.actual_date or m.forecast_date or planned,
                "url": reverse("milestones:detail", args=[project.public_id, m.public_id]),
            }
        )
    visible = [s for s in states if not s["milestone"].is_hidden]
    current = next((s for s in visible if not s["approval_valid"]), None)
    current_index = visible.index(current) if current else len(visible)
    for i, s in enumerate(visible):
        s["index"] = i
        s["number"] = i + 1
        s["is_current"] = s is current
        s["is_past"] = i < current_index
        s["prev"] = visible[i - 1] if i > 0 else None
        s["next"] = visible[i + 1] if i + 1 < len(visible) else None
    return {
        "states": states,
        "visible": visible,
        "hidden": [s for s in states if s["milestone"].is_hidden],
        "current": current,
        "count": len(visible),
        "plans": plans,
        "today": on,
    }


def state_for(journey_data, milestone):
    return next(s for s in journey_data["states"] if s["milestone"].pk == milestone.pk)


def get_milestone_or_404(project, public_id):
    return get_object_or_404(Milestone, project=project, public_id=public_id)


def get_deliverable_or_404(project, public_id):
    """Lieferobjekte anderer Projekte sind über diese URL nicht erreichbar (404)."""
    return get_object_or_404(
        Deliverable.objects.select_related("milestone", "project", "responsible"),
        project=project,
        public_id=public_id,
    )


# ---------- Navigation ----------


def navigation(project, active, journey_data=None, selected=None):
    """Unterpunkte des geöffneten Projekts im Hauptmenü und Orientierungsleiste.

    Status je Bereich: Lieferobjekte dieses Bereichs im aktuellen Meilenstein, z. B. „M1: 2 offen“.
    """
    j = journey_data or journey(project)
    current = j["current"]
    sections = []
    for key, label, url_name in SECTIONS:
        marker, open_count = None, 0
        if key != "uebersicht" and current is not None:
            in_area = [d for d in current["deliverables"] if d.area == key]
            if in_area:
                # Ohne Termin nie ✓/grün: Bereich erbt „nicht bewertet“ (Kriterium 10)
                marker = rating(in_area, current["has_date"])
                open_count = sum(1 for d in in_area if not d.is_present)
        sections.append(
            {
                "key": key,
                "label": label,
                "url": reverse(url_name, args=[project.public_id]) if url_name else None,
                "marker": marker,
                "open_count": open_count,
                "active": key == active,
            }
        )
    selected_state = selected or current or (j["visible"][-1] if j["visible"] else None)
    active_label = next((s["label"] for s in sections if s["key"] == active), None)
    if active == "meilenstein" and selected_state:
        active_label = selected_state["milestone"].label
    return {
        "project": project,
        "sections": sections,
        "journey": j,
        "current": current,
        "selected": selected_state,
        "active": active,
        "active_label": active_label or project.name,
        "on_milestone": active == "meilenstein",
    }


# ---------- Übersicht (Cockpit) ----------


def team(project):
    from apps.projects.selectors import membership_rows

    return membership_rows(project)


def cockpit(project, journey_data):
    j = journey_data
    on = j["today"]
    current = j["current"]
    current_index = current["index"] if current else j["count"]
    steps = []
    for s in j["visible"][:current_index]:
        a = s["approval"]
        if a and s["approval_valid"] and a.light == ApprovalLight.ORANGE:
            steps.append(
                {
                    "title": f"Auflage aus {s['milestone'].label} erfüllen",
                    "text": a.conditions,
                    "url": s["url"],
                }
            )
    if current:
        open_items = sorted(
            (d for d in current["deliverables"] if not d.is_present),
            key=lambda d: (not d.required, d.position, d.pk),
        )
        for d in open_items:
            steps.append(
                {
                    "title": f"{d.title} ({DELIVERABLE_MARKER[d.status]['label']})",
                    "text": ("Pflicht" if d.required else "optional")
                    + f" für {current['milestone'].label}",
                    "url": current["url"],
                }
            )
    upcoming = sorted(
        (s for s in j["visible"] if not s["actual_date"] and s["date"] and s["date"] >= on),
        key=lambda s: s["date"],
    )[:3]
    open_approvals = [s for s in j["visible"] if not s["approval_valid"]]
    tasks = Task.objects.filter(project=project, status=TaskStatus.OFFEN)
    members = team(project)
    return {
        "steps": steps[:5],
        "steps_total": len(steps),
        "upcoming": upcoming,
        "open_approvals": open_approvals[:3],
        "open_approvals_count": len(open_approvals),
        "tasks_open": tasks.count(),
        "tasks_overdue": tasks.filter(due_date__lt=on).count(),
        "members": members,
        "leads": [m["user"] for m in members if ProjectRole.PROJEKTLEITER in m["roles"]],
    }


# ---------- Termine & Zeitstrahl ----------


def _deviation(planned, value):
    if not planned or not value:
        return None
    return (value - planned).days


def schedule(project, journey_data):
    j = journey_data
    plans = j["plans"]
    period_original = plans["original"].get("period")
    period_approved = plans["approved"].get("period")
    period_rows = []
    for label, idx, forecast, actual in (
        ("Beginn", 0, project.forecast_start_date, project.actual_start_date),
        ("Ende", 1, project.forecast_end_date, project.actual_end_date),
    ):
        planned = period_approved[idx] if period_approved else None
        period_rows.append(
            {
                "label": f"Projekt {label}",
                "original": period_original[0][idx] if period_original else None,
                "planned": planned,
                "forecast": forecast,
                "actual": actual,
                "deviation": _deviation(planned, actual or forecast),
            }
        )
    milestone_rows = [
        s | {"deviation": _deviation(s["planned_date"], s["actual_date"] or s["forecast_date"])}
        for s in j["visible"]
    ]

    # Zeitstrahl: Projektzeitraum, erweitert um Termine außerhalb
    dated = [s for s in j["visible"] if s["date"]]
    first = min([project.start_date] + [s["date"] for s in dated])
    last = max([project.end_date] + [s["date"] for s in dated])
    span = max((last - first).days, 1)

    def pos(day):
        return round(min(max((day - first).days / span, 0), 1) * 100, 1)

    points = [
        {
            "state": s,
            "left": pos(s["date"]),
            "kind": "Ist" if s["actual_date"] else ("Prognose" if s["forecast_date"] else "Plan"),
        }
        for s in dated
    ]
    on = j["today"]
    versions = list(
        PlanVersion.objects.filter(project=project)
        .select_related("created_by", "approved_by")
        .order_by("-number")
    )
    changes = list(
        DateChange.objects.filter(project=project)
        .select_related("milestone", "actor")
        .order_by("-created_at", "-id")
    )
    return {
        "period_rows": period_rows,
        "milestone_rows": milestone_rows,
        "undated": [s for s in j["visible"] if not s["date"]],
        "timeline": {
            "points": points,
            "first": first,
            "last": last,
            "today_left": pos(on) if first <= on <= last else None,
        },
        "versions": versions,
        "changes": changes,
        "hidden": j["hidden"],
    }


def version_detail(project, number):
    version = get_object_or_404(
        PlanVersion.objects.select_related("created_by", "approved_by"),
        project=project,
        number=number,
    )
    entries = list(version.entries.select_related("milestone").order_by("id"))
    period = next((e for e in entries if e.kind == PlanEntryKind.ZEITRAUM), None)
    by_milestone = {e.milestone_id: e.date for e in entries if e.kind == PlanEntryKind.MEILENSTEIN}
    return {"version": version, "period": period, "by_milestone": by_milestone}
