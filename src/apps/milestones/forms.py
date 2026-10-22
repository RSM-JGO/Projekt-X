"""Formulare ohne Modellbindung: gespeichert wird ausschließlich über die Services."""

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.projects.forms import DateInput, UserChoiceField
from apps.projects.models import ProjectRole

from .models import ApprovalLight, Area, DateKind, DatePoint, DeliverableStatus, PlanStatus


def _members(project, roles=None):
    """Aktive Konten mit aktiver Mitgliedschaft (optional nur mit bestimmten aktiven Rollen)."""
    condition = Q(
        project_memberships__project=project,
        project_memberships__ended_at__isnull=True,
    )
    if roles:
        condition &= Q(
            project_memberships__role_assignments__role__in=roles,
            project_memberships__role_assignments__ended_at__isnull=True,
        )
    return get_user_model().objects.filter(condition, is_active=True)


def responsible_queryset(project, current=None):
    users = _members(project, [ProjectRole.PROJEKTLEITER, ProjectRole.MITARBEITER])
    if current is not None:
        users = get_user_model().objects.filter(Q(pk__in=users.values("pk")) | Q(pk=current.pk))
    return users.distinct().order_by("display_name", "email")


class MilestoneForm(forms.Form):
    code = forms.CharField(label="Kürzel", max_length=10, help_text="z. B. M2a")
    phase_name = forms.CharField(label="Abschnitt", max_length=100)
    title = forms.CharField(label="Titel", max_length=200)
    goal = forms.CharField(label="Ziel", required=False, widget=forms.Textarea(attrs={"rows": 3}))
    after = forms.ModelChoiceField(
        label="Einfügen nach", queryset=None, required=False, empty_label="am Ende"
    )

    def __init__(self, *args, project, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["after"].queryset = project.milestones.order_by("position", "id")


class DeliverableForm(forms.Form):
    title = forms.CharField(label="Titel", max_length=200)
    required = forms.BooleanField(label="Pflicht (für die Freigabe benötigt)", required=False)
    area = forms.ChoiceField(label="Bereich", choices=Area.choices)
    status = forms.ChoiceField(label="Status", choices=DeliverableStatus.choices)
    responsible = UserChoiceField(
        label="Verantwortlich", queryset=None, required=False, empty_label="niemand"
    )
    note = forms.CharField(label="Notiz", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, project, current_responsible=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsible"].queryset = responsible_queryset(project, current_responsible)
        self.fields["responsible"].help_text = (
            "Nur aktive Projektleiter oder Mitarbeiter. Die verantwortliche Person darf den "
            "Status selbst setzen."
        )


class DeliverableStatusForm(forms.Form):
    status = forms.ChoiceField(label="Status", choices=DeliverableStatus.choices)


class ApprovalForm(forms.Form):
    light = forms.ChoiceField(
        label="Ampel", choices=ApprovalLight.choices, widget=forms.RadioSelect
    )
    decision = forms.CharField(label="Entscheidung", widget=forms.Textarea(attrs={"rows": 2}))
    decided_on = forms.DateField(label="Datum der Entscheidung", widget=DateInput())
    participants = forms.ModelMultipleChoiceField(
        label="Beteiligte (Konten)",
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    external_participants = forms.CharField(
        label="Weitere Beteiligte (Freitext, z. B. Externe)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    basis = forms.CharField(
        label="Grundlage", required=False, widget=forms.Textarea(attrs={"rows": 2})
    )
    conditions = forms.CharField(
        label="Auflagen",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="Bei Orange erforderlich.",
    )
    valid_until = forms.DateField(label="Gültig bis", required=False, widget=DateInput())
    plan_version = forms.ModelChoiceField(
        label="Bezug auf Planversion", queryset=None, required=False, empty_label="kein Bezug"
    )
    confirm_missing = forms.BooleanField(
        label="Ich habe die Warnung gelesen und gebe trotz fehlender Pflichtdokumente frei.",
        required=False,
    )
    missing_ids = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, project, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["participants"].queryset = (
            _members(project).distinct().order_by("display_name", "email")
        )
        self.fields["participants"].label_from_instance = lambda u: u.display_name
        self.fields["plan_version"].queryset = project.plan_versions.exclude(
            status=PlanStatus.ENTWURF
        ).order_by("-number")

    def confirmed_missing(self):
        """IDs der bestätigten fehlenden Pflichtdokumente oder None ohne Bestätigung."""
        if not self.cleaned_data.get("confirm_missing"):
            return None
        raw = self.cleaned_data.get("missing_ids") or ""
        return [int(x) for x in raw.split(",") if x.strip().isdigit()]


class PlanReasonForm(forms.Form):
    reason = forms.CharField(
        label="Anlass", widget=forms.Textarea(attrs={"rows": 2}), max_length=2000
    )


class PlanDraftForm(forms.Form):
    """Projektzeitraum und je Meilenstein ein Termin (leer = ohne Termin).

    Ausgeblendete Meilensteine mit Planeintrag stehen gekennzeichnet im Formular, damit ihre
    Termine sichtbar und korrigierbar bleiben und der Entwurf nicht an verdeckten Einträgen
    außerhalb des Zeitraums scheitert.
    """

    start_date = forms.DateField(label="Projekt Beginn", widget=DateInput())
    end_date = forms.DateField(label="Projekt Ende", widget=DateInput())
    reason = forms.CharField(
        label="Anlass", required=False, widget=forms.Textarea(attrs={"rows": 2})
    )

    def __init__(self, *args, milestones, hidden_milestones=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.milestones = list(milestones)
        self.hidden_milestones = list(hidden_milestones)
        for m in self.milestones:
            self.fields[f"ms_{m.pk}"] = forms.DateField(
                label=m.label, required=False, widget=DateInput()
            )
        for m in self.hidden_milestones:
            self.fields[f"ms_{m.pk}"] = forms.DateField(
                label=f"{m.label} (ausgeblendet)", required=False, widget=DateInput()
            )

    def milestone_fields(self):
        return [self[f"ms_{m.pk}"] for m in self.milestones]

    def hidden_fields_list(self):
        return [self[f"ms_{m.pk}"] for m in self.hidden_milestones]

    def milestone_dates(self):
        return [
            (m, self.cleaned_data.get(f"ms_{m.pk}"))
            for m in self.milestones + self.hidden_milestones
        ]

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "Das Ende darf nicht vor dem Beginn liegen.")
        return cleaned


class DateChangeForm(forms.Form):
    kind = forms.ChoiceField(label="Art", choices=DateKind.choices, widget=forms.RadioSelect)
    point = forms.ChoiceField(
        label="Terminpunkt",
        choices=[(DatePoint.BEGINN, "Beginn"), (DatePoint.ENDE, "Ende")],
        widget=forms.RadioSelect,
    )
    value = forms.DateField(
        label="Neuer Wert",
        required=False,
        widget=DateInput(),
        help_text="Leer lassen, um den Wert zu entfernen.",
    )
    reason = forms.CharField(label="Begründung", widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, for_milestone, **kwargs):
        super().__init__(*args, **kwargs)
        if for_milestone:
            del self.fields["point"]
