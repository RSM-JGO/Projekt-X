"""Seiten für Meilensteine, Lieferobjekte, Freigaben und Termine (Etappe 4a).

Reihenfolge der Prüfung wie in apps.projects.views: nicht angemeldet -> Anmeldung; Projekt
unbekannt -> 404; kein aktives Mitglied -> 403 „Kein Zugriff auf dieses Projekt“; Objekt nicht
im Projekt -> 404; Aktion nicht erlaubt -> 403. Die Services prüfen die Rechte zusätzlich.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from apps.projects import selectors as project_selectors
from apps.projects.views import _add_service_errors

from . import policies, selectors, services
from .forms import (
    ApprovalForm,
    DateChangeForm,
    DeliverableForm,
    DeliverableStatusForm,
    MilestoneForm,
    PlanDraftForm,
    PlanReasonForm,
)
from .models import ApprovalLight, DeliverableStatus, PlanVersion


def _require(allowed):
    if not allowed:
        raise PermissionDenied


def _admin_flag(request, project):
    return policies.acts_as_admin(policies.can_manage, request.user, project)


def _context(request, project, active, journey=None, selected=None, **extra):
    journey = journey or selectors.journey(project)
    return {
        "project": project,
        "project_nav": selectors.navigation(project, active, journey, selected),
        "can_manage": policies.can_manage(request.user, project),
        "acts_as_admin": _admin_flag(request, project),
        **extra,
    }


def _milestone_redirect(project, milestone):
    return redirect("milestones:detail", public_id=project.public_id, ms_id=milestone.public_id)


# ---------- Termine & Zeitstrahl ----------


@login_required
@require_http_methods(["GET"])
def schedule(request, public_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    journey = selectors.journey(project)
    return render(
        request,
        "milestones/schedule.html",
        _context(
            request,
            project,
            "termine",
            journey,
            schedule=selectors.schedule(project, journey),
            plans=journey["plans"],
        ),
    )


# ---------- Meilensteine ----------


@login_required
@require_http_methods(["GET"])
def milestone_detail(request, public_id, ms_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    milestone = selectors.get_milestone_or_404(project, ms_id)
    journey = selectors.journey(project)
    state = selectors.state_for(journey, milestone)
    rows = [
        {
            "deliverable": d,
            "marker": selectors.DELIVERABLE_MARKER[d.status],
            "area_label": d.get_area_display(),
            "area_url": selectors.section_url(project, d.area),
            "can_set_status": policies.can_set_deliverable_status(request.user, d),
        }
        for d in state["deliverables"]
    ]
    return render(
        request,
        "milestones/milestone_detail.html",
        _context(
            request,
            project,
            "meilenstein",
            journey,
            selected=state if not milestone.is_hidden else None,
            state=state,
            milestone=milestone,
            rows=rows,
            statuses=DeliverableStatus.choices,
        ),
    )


@login_required
@require_http_methods(["GET", "POST"])
def milestone_add(request, public_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage(request.user, project))
    form = MilestoneForm(request.POST or None, project=project)
    if request.method == "POST" and form.is_valid():
        try:
            milestone = services.add_milestone(
                actor=request.user, project=project, **form.cleaned_data
            )
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, f"Meilenstein {milestone.code} ergänzt.")
            return _milestone_redirect(project, milestone)
    return render(
        request, "milestones/milestone_form.html", _context(request, project, "termine", form=form)
    )


@login_required
@require_POST
def milestone_visibility(request, public_id, ms_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage(request.user, project))
    milestone = selectors.get_milestone_or_404(project, ms_id)
    hidden = request.POST.get("hidden") == "1"
    services.set_milestone_hidden(
        actor=request.user, project=project, milestone=milestone, hidden=hidden
    )
    messages.success(
        request,
        f"{milestone.label} ist ausgeblendet. Freigaben und Planstände bleiben erhalten."
        if hidden
        else f"{milestone.label} ist wieder eingeblendet.",
    )
    return _milestone_redirect(project, milestone)


# ---------- Lieferobjekte ----------


@login_required
@require_http_methods(["GET", "POST"])
def deliverable_add(request, public_id, ms_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage(request.user, project))
    milestone = selectors.get_milestone_or_404(project, ms_id)
    form = DeliverableForm(
        request.POST or None, project=project, initial={"status": DeliverableStatus.FEHLT}
    )
    if request.method == "POST" and form.is_valid():
        try:
            services.add_deliverable(
                actor=request.user, project=project, milestone=milestone, **form.cleaned_data
            )
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, "Lieferobjekt ergänzt.")
            return _milestone_redirect(project, milestone)
    return render(
        request,
        "milestones/deliverable_form.html",
        _context(request, project, "meilenstein", form=form, milestone=milestone, deliverable=None),
    )


@login_required
@require_http_methods(["GET", "POST"])
def deliverable_edit(request, public_id, d_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage(request.user, project))
    deliverable = selectors.get_deliverable_or_404(project, d_id)
    initial = {
        "title": deliverable.title,
        "required": deliverable.required,
        "area": deliverable.area,
        "status": deliverable.status,
        "responsible": deliverable.responsible_id,
        "note": deliverable.note,
    }
    form = DeliverableForm(
        request.POST or None,
        project=project,
        current_responsible=deliverable.responsible,
        initial=initial,
    )
    if request.method == "POST" and form.is_valid():
        try:
            services.update_deliverable(
                actor=request.user, project=project, deliverable=deliverable, **form.cleaned_data
            )
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, "Lieferobjekt gespeichert.")
            return _milestone_redirect(project, deliverable.milestone)
    return render(
        request,
        "milestones/deliverable_form.html",
        _context(
            request,
            project,
            "meilenstein",
            form=form,
            milestone=deliverable.milestone,
            deliverable=deliverable,
        ),
    )


@login_required
@require_POST
def deliverable_status(request, public_id, d_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    deliverable = selectors.get_deliverable_or_404(project, d_id)
    _require(policies.can_set_deliverable_status(request.user, deliverable))
    form = DeliverableStatusForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Ungültiger Status.")
    else:
        services.set_deliverable_status(
            actor=request.user,
            project=project,
            deliverable=deliverable,
            status=form.cleaned_data["status"],
        )
        messages.success(request, f"Status von „{deliverable.title}“ gespeichert.")
    return _milestone_redirect(project, deliverable.milestone)


# ---------- Freigaben ----------


@login_required
@require_http_methods(["GET", "POST"])
def approval_create(request, public_id, ms_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage(request.user, project))
    milestone = selectors.get_milestone_or_404(project, ms_id)
    current = services.current_approval(milestone)
    correction = request.GET.get("korrektur") == "1" or request.POST.get("korrektur") == "1"
    if correction and current is None:
        correction = False
    missing = services.missing_required(milestone)
    initial = {"decided_on": services.today()}
    if correction:
        initial |= {
            "light": current.light,
            "decision": current.decision,
            "decided_on": current.decided_on,
            "participants": list(current.participant_links.values_list("user_id", flat=True)),
            "external_participants": current.external_participants,
            "basis": current.basis,
            "conditions": current.conditions,
            "valid_until": current.valid_until,
            "plan_version": current.plan_version_id,
        }
    form = ApprovalForm(request.POST or None, project=project, initial=initial)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            services.grant_approval(
                actor=request.user,
                project=project,
                milestone=milestone,
                light=data["light"],
                decision=data["decision"],
                decided_on=data["decided_on"],
                participants=data["participants"],
                external_participants=data["external_participants"],
                basis=data["basis"],
                conditions=data["conditions"],
                valid_until=data["valid_until"],
                plan_version=data["plan_version"],
                replaces=current if correction else None,
                confirmed_missing=form.confirmed_missing(),
            )
        except ValidationError as exc:
            # Aktuelle Liste anzeigen; das Template setzt die IDs für die erneute Bestätigung
            missing = services.missing_required(milestone)
            if getattr(exc, "code", None) == "missing_required":
                # Erneute ausdrückliche Bestätigung nötig: Häkchen nicht übernehmen
                data = request.POST.copy()
                data.pop("confirm_missing", None)
                form = ApprovalForm(data, project=project, initial=initial)
                form.is_valid()
            _add_service_errors(form, exc)
        else:
            messages.success(
                request,
                "Korrektur gespeichert." if correction else "Freigabeentscheidung gespeichert.",
            )
            return _milestone_redirect(project, milestone)
    return render(
        request,
        "milestones/approval_form.html",
        _context(
            request,
            project,
            "meilenstein",
            form=form,
            milestone=milestone,
            missing=missing,
            missing_ids=",".join(str(m["id"]) for m in missing),
            current=current if correction else None,
            correction=correction,
            lights=ApprovalLight,
        ),
    )


# ---------- Planversionen ----------


@login_required
@require_http_methods(["GET", "POST"])
def plan_create(request, public_id):
    project = project_selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage(request.user, project))
    form = PlanReasonForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            version = services.create_plan_draft(
                actor=request.user, project=project, reason=form.cleaned_data["reason"]
            )
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, f"Planentwurf {version.number} angelegt.")
            return redirect("milestones:plan", public_id=project.public_id, number=version.number)
    return render(
        request,
        "milestones/plan_create.html",
        _context(request, project, "termine", form=form, draft=services.draft_version(project)),
    )


@login_required
@require_http_methods(["GET", "POST"])
def plan_detail(request, public_id, number):
    project = project_selectors.get_accessible_project(request.user, public_id)
    detail = selectors.version_detail(project, number)
    version = detail["version"]
    journey = selectors.journey(project)
    editable = version.is_draft and policies.can_manage(request.user, project)
    if request.method == "POST":
        _require(policies.can_manage(request.user, project))
        if not version.is_draft:
            raise PermissionDenied("Genehmigte Planversionen sind unveränderlich.")
    milestones = [s["milestone"] for s in journey["visible"]]
    # Ausgeblendete mit Planeintrag im Entwurf: gekennzeichnet im Formular (siehe PlanDraftForm)
    hidden = [
        s["milestone"] for s in journey["hidden"] if s["milestone"].pk in detail["by_milestone"]
    ]
    form = None
    if editable:
        initial = {"reason": version.reason}
        if detail["period"]:
            initial |= {
                "start_date": detail["period"].start_date,
                "end_date": detail["period"].end_date,
            }
        for m in milestones + hidden:
            initial[f"ms_{m.pk}"] = detail["by_milestone"].get(m.pk)
        form = PlanDraftForm(
            request.POST or None, milestones=milestones, hidden_milestones=hidden, initial=initial
        )
        if request.method == "POST" and form.is_valid():
            try:
                services.update_plan_draft(
                    actor=request.user,
                    project=project,
                    version=version,
                    start_date=form.cleaned_data["start_date"],
                    end_date=form.cleaned_data["end_date"],
                    milestone_dates=form.milestone_dates(),
                    reason=form.cleaned_data["reason"],
                )
            except ValidationError as exc:
                _add_service_errors(form, exc)
            else:
                messages.success(request, "Planentwurf gespeichert.")
                return redirect("milestones:plan", public_id=project.public_id, number=number)
    rows = [
        {"state": s, "date": detail["by_milestone"].get(s["milestone"].pk)}
        for s in journey["states"]
        if s["milestone"].pk in detail["by_milestone"] or not s["milestone"].is_hidden
    ]
    return render(
        request,
        "milestones/plan_detail.html",
        _context(
            request,
            project,
            "termine",
            journey,
            detail=detail,
            version=version,
            form=form,
            rows=rows,
        ),
    )


@login_required
@require_POST
def plan_approve(request, public_id, number):
    project = project_selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage(request.user, project))
    version = get_object_or_404(PlanVersion, project=project, number=number)
    try:
        services.approve_plan_version(actor=request.user, project=project, version=version)
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect("milestones:plan", public_id=project.public_id, number=number)
    messages.success(
        request,
        f"Planversion {version.number} genehmigt. Der Projektzeitraum wurde übernommen.",
    )
    return redirect("milestones:schedule", public_id=project.public_id)


# ---------- Prognose und Ist ----------


@login_required
@require_http_methods(["GET", "POST"])
def date_change(request, public_id, ms_id=None):
    project = project_selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage(request.user, project))
    milestone = selectors.get_milestone_or_404(project, ms_id) if ms_id else None
    form = DateChangeForm(request.POST or None, for_milestone=milestone is not None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            services.change_date(
                actor=request.user,
                project=project,
                milestone=milestone,
                point=data.get("point"),
                kind=data["kind"],
                value=data["value"],
                reason=data["reason"],
            )
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, "Termin geändert. Die Änderung steht im Verlauf.")
            return redirect("milestones:schedule", public_id=project.public_id)
    return render(
        request,
        "milestones/date_change_form.html",
        _context(request, project, "termine", form=form, milestone=milestone),
    )
