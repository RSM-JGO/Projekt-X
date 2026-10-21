from django import forms
from django.contrib.auth import get_user_model

from apps.projects.forms import DateInput
from apps.projects.models import ProjectRole, ProjectRoleAssignment

from .selectors import active_buckets


class AssigneeField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.display_name


def assignable_users(project):
    """Aktive Projektleiter und Mitarbeiter des Projekts (Management allein nicht)."""
    ids = ProjectRoleAssignment.objects.filter(
        membership__project=project,
        membership__ended_at__isnull=True,
        membership__user__is_active=True,
        ended_at__isnull=True,
        role__in=[ProjectRole.PROJEKTLEITER, ProjectRole.MITARBEITER],
    ).values("membership__user_id")
    return get_user_model().objects.filter(pk__in=ids).order_by("display_name", "email")


class TaskForm(forms.Form):
    title = forms.CharField(label="Titel", max_length=200)
    description = forms.CharField(
        label="Beschreibung", required=False, widget=forms.Textarea(attrs={"rows": 4})
    )
    due_date = forms.DateField(label="Fälligkeit", required=False, widget=DateInput())
    bucket = forms.ModelChoiceField(label="Bucket", queryset=None, empty_label=None)
    assignees = AssigneeField(
        label="Zuständig",
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Nur aktive Projektleiter und Mitarbeiter sind auswählbar.",
    )
    version = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, project=None, can_assign=True, **kwargs):
        super().__init__(*args, **kwargs)
        if project is None:
            # Persönliche Aufgabe: ohne Bucket und ohne Zuweisung
            del self.fields["bucket"]
            del self.fields["assignees"]
            return
        self.fields["bucket"].queryset = active_buckets(project)
        if can_assign:
            self.fields["assignees"].queryset = assignable_users(project)
        else:
            # Zuständige ändern nur Projektleiter und Administrator; Feld entfällt
            del self.fields["assignees"]


class BucketForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)
