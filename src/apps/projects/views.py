"""Seiten für Projekte und Mitglieder.

Reihenfolge der Prüfung: nicht angemeldet -> Anmeldung; Projekt unbekannt -> 404;
kein aktives Mitglied -> 403 „Kein Zugriff auf dieses Projekt“; Aktion nicht erlaubt -> 403.
Die Services prüfen die Rechte zusätzlich.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.milestones import policies as milestone_policies
from apps.milestones import selectors as milestone_selectors
from apps.milestones import services as milestone_services

from . import policies, selectors, services
from .forms import MemberAddForm, MemberRolesForm, ProjectForm


def _add_service_errors(form, error):
    if hasattr(error, "error_dict"):
        for field, errors in error.error_dict.items():
            form.add_error(field if field in form.fields else None, errors)
    else:
        form.add_error(None, error)


def _require(allowed):
    if not allowed:
        raise PermissionDenied


@login_required
@require_http_methods(["GET"])
def project_list(request):
    return render(
        request,
        "projects/project_list.html",
        {
            "overview": selectors.project_overview(request.user),
            "can_create": policies.can_create_project(request.user),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def project_create(request):
    _require(policies.can_create_project(request.user))
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            project = services.create_project(actor=request.user, **form.cleaned_data)
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, "Projekt angelegt. Du bist Projektleiter.")
            return redirect("projects:detail", public_id=project.public_id)
    return render(request, "projects/project_form.html", {"form": form, "project": None})


def project_nav(project, active, journey=None):
    """Unterpunkte des geöffneten Projekts für das Hauptmenü (Etappe 4a)."""
    return milestone_selectors.navigation(project, active, journey)


def _my_roles(members, user):
    return [r for m in members if m["user"].pk == user.pk for r in m["roles"]]


@login_required
@require_http_methods(["GET"])
def project_detail(request, public_id):
    """Übersicht als Cockpit: aktueller Abschnitt, nächste Schritte, Kacheln, Team."""
    project = selectors.get_accessible_project(request.user, public_id)
    journey = milestone_selectors.journey(project)
    cockpit = milestone_selectors.cockpit(project, journey)
    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "project_nav": project_nav(project, "uebersicht", journey),
            "cockpit": cockpit,
            "current": journey["current"],
            "my_roles": _my_roles(cockpit["members"], request.user),
            "can_edit": policies.can_edit_project(request.user, project),
            "can_manage": milestone_policies.can_manage(request.user, project),
            "acts_as_admin": policies.acts_as_admin(request.user, project),
        },
    )


@login_required
@require_http_methods(["GET"])
def team(request, public_id):
    """Team: Mitglieder mit Rollen und Mitgliederverwaltung (aus der Übersicht erreichbar)."""
    project = selectors.get_accessible_project(request.user, public_id)
    members = selectors.membership_rows(project)
    return render(
        request,
        "projects/team.html",
        {
            "project": project,
            "project_nav": project_nav(project, "uebersicht"),
            "members": members,
            "my_roles": _my_roles(members, request.user),
            "can_manage_members": policies.can_manage_members(request.user, project),
            "acts_as_admin": policies.acts_as_admin(request.user, project),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def project_edit(request, public_id):
    project = selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_edit_project(request.user, project))
    initial = {f: getattr(project, f) for f in services.PROJECT_FIELDS}
    # Nach der ersten genehmigten Planversion nur noch über Planversionen änderbar
    period_locked = milestone_services.period_locked(project)
    form = ProjectForm(request.POST or None, initial=initial, period_locked=period_locked)
    if request.method == "POST" and form.is_valid():
        try:
            saved = services.update_project(
                actor=request.user, project=project, **form.cleaned_data
            )
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, "Projekt gespeichert.")
            if getattr(saved, "draft_period_kept", False):
                messages.warning(
                    request,
                    "Der Planentwurf hat einen eigenen, bereits bearbeiteten Zeitraum und wurde "
                    "nicht überschrieben. Bitte den Entwurf unter Termine & Zeitstrahl prüfen.",
                )
            return redirect("projects:detail", public_id=project.public_id)
    return render(
        request,
        "projects/project_form.html",
        {
            "form": form,
            "project": project,
            "project_nav": project_nav(project, "uebersicht"),
            "period_locked": period_locked,
            "acts_as_admin": policies.acts_as_admin(request.user, project),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def member_add(request, public_id):
    project = selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage_members(request.user, project))
    form = MemberAddForm(request.POST or None, project=project)
    if request.method == "POST" and form.is_valid():
        try:
            services.add_member(
                actor=request.user,
                project=project,
                user=form.cleaned_data["user"],
                roles=form.cleaned_data["roles"],
            )
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, "Mitglied hinzugefügt.")
            return redirect("projects:team", public_id=project.public_id)
    return render(
        request,
        "projects/member_add.html",
        {
            "form": form,
            "project": project,
            "project_nav": project_nav(project, "uebersicht"),
            "acts_as_admin": policies.acts_as_admin(request.user, project),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def member_roles(request, public_id, membership_id):
    project = selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage_members(request.user, project))
    membership = selectors.get_active_membership_or_404(project, membership_id)
    current = [a.role for a in membership.active_role_list]
    form = MemberRolesForm(request.POST or None, initial={"roles": current})
    if request.method == "POST" and form.is_valid():
        try:
            services.change_roles(
                actor=request.user,
                project=project,
                membership=membership,
                roles=form.cleaned_data["roles"],
            )
        except ValidationError as exc:
            _add_service_errors(form, exc)
        else:
            messages.success(request, "Rollen gespeichert.")
            return redirect("projects:team", public_id=project.public_id)
    return render(
        request,
        "projects/member_roles.html",
        {
            "form": form,
            "project": project,
            "project_nav": project_nav(project, "uebersicht"),
            "membership": membership,
            "acts_as_admin": policies.acts_as_admin(request.user, project),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def member_remove(request, public_id, membership_id):
    project = selectors.get_accessible_project(request.user, public_id)
    _require(policies.can_manage_members(request.user, project))
    membership = selectors.get_active_membership_or_404(project, membership_id)
    error = None
    if request.method == "POST":
        try:
            services.remove_member(actor=request.user, project=project, membership=membership)
        except ValidationError as exc:
            error = " ".join(exc.messages)
        else:
            messages.success(request, f"{membership.user.display_name} wurde entfernt.")
            return redirect("projects:team", public_id=project.public_id)
    return render(
        request,
        "projects/member_remove.html",
        {
            "project": project,
            "project_nav": project_nav(project, "uebersicht"),
            "membership": membership,
            "roles": [a.get_role_display() for a in membership.active_role_list],
            "error": error,
            "acts_as_admin": policies.acts_as_admin(request.user, project),
        },
        status=400 if error else 200,
    )
