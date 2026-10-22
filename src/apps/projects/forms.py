from django import forms
from django.contrib.auth import get_user_model

from .models import ProjectMembership, ProjectRole


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        super().__init__(format="%Y-%m-%d", **kwargs)


class ProjectForm(forms.Form):
    """Formular ohne Modellbindung: gespeichert wird ausschließlich über den Service."""

    name = forms.CharField(label="Name", max_length=200)
    description = forms.CharField(
        label="Beschreibung", required=False, widget=forms.Textarea(attrs={"rows": 4})
    )
    start_date = forms.DateField(label="Beginn", widget=DateInput())
    end_date = forms.DateField(label="Ende", widget=DateInput())

    def __init__(self, *args, period_locked=False, **kwargs):
        super().__init__(*args, **kwargs)
        if period_locked:
            # Gesperrte Felder: Django verwendet den Ausgangswert, eingesandte Werte zählen nicht
            for name in ("start_date", "end_date"):
                self.fields[name].disabled = True
                self.fields[name].help_text = "Änderbar über eine neue Planversion."

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "Das Ende darf nicht vor dem Beginn liegen.")
        return cleaned


class RolesField(forms.MultipleChoiceField):
    def __init__(self, **kwargs):
        super().__init__(
            label="Projektrollen",
            choices=ProjectRole.choices,
            widget=forms.CheckboxSelectMultiple,
            error_messages={"required": "Bitte mindestens eine Rolle auswählen."},
            **kwargs,
        )


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.display_name} ({obj.email})"


class MemberAddForm(forms.Form):
    user = UserChoiceField(label="Person", queryset=get_user_model().objects.none())
    roles = RolesField()

    def __init__(self, *args, project, **kwargs):
        super().__init__(*args, **kwargs)
        active_member_ids = ProjectMembership.objects.filter(
            project=project, ended_at__isnull=True
        ).values("user_id")
        self.fields["user"].queryset = (
            get_user_model()
            .objects.filter(is_active=True)
            .exclude(pk__in=active_member_ids)
            .order_by("display_name", "email")
        )


class MemberRolesForm(forms.Form):
    roles = RolesField()
