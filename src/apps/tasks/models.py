import uuid

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils import timezone


class AppendOnlyError(Exception):
    """Verlaufseinträge dürfen weder geändert noch gelöscht werden."""


class Bucket(models.Model):
    """Spalte des Aufgabenboards eines Projekts."""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.PROTECT, related_name="buckets", verbose_name="Projekt"
    )
    name = models.CharField("Name", max_length=100)
    position = models.PositiveIntegerField("Reihenfolge", default=0)
    is_archived = models.BooleanField("archiviert", default=False)
    created_at = models.DateTimeField("angelegt am", default=timezone.now)

    class Meta:
        verbose_name = "Bucket"
        verbose_name_plural = "Buckets"
        ordering = ["position", "id"]
        constraints = [
            models.UniqueConstraint(
                "project",
                Lower("name"),
                condition=Q(is_archived=False),
                name="tasks_bucket_name_unique_active",
                violation_error_message="Diesen Bucket-Namen gibt es im Projekt bereits.",
            ),
            # Ziel des zusammengesetzten Fremdschlüssels Aufgabe -> (Bucket, Projekt), siehe 0002
            models.UniqueConstraint(fields=["id", "project"], name="tasks_bucket_id_project"),
        ]

    def __str__(self):
        return self.name


class TaskStatus(models.TextChoices):
    OFFEN = "OFFEN", "Offen"
    ERLEDIGT = "ERLEDIGT", "Erledigt"


class Task(models.Model):
    """Gemeinsame Projektaufgabe oder persönliche Aufgabe ohne Projekt.

    Projektaufgabe: Projekt und Bucket gesetzt, kein Eigentümer; Rechte aus Projektrollen.
    Persönliche Aufgabe: weder Projekt noch Bucket, Eigentümer Pflicht; keine Zuweisungen.
    Der Status ist gemeinsam: Schließt eine zugewiesene Person ab, ist die Aufgabe für alle
    erledigt. Der Versionszähler verhindert stilles Überschreiben paralleler Bearbeitungen.
    """

    public_id = models.UUIDField("öffentliche ID", default=uuid.uuid4, unique=True, editable=False)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Projekt",
    )
    bucket = models.ForeignKey(
        Bucket,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Bucket",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="personal_tasks",
        verbose_name="Eigentümer",
    )
    title = models.CharField("Titel", max_length=200)
    description = models.TextField("Beschreibung", blank=True)
    status = models.CharField(
        "Status", max_length=10, choices=TaskStatus.choices, default=TaskStatus.OFFEN
    )
    due_date = models.DateField("Fälligkeit", null=True, blank=True)
    completed_at = models.DateTimeField("abgeschlossen am", null=True, blank=True)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="abgeschlossen von",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="angelegt von",
    )
    created_at = models.DateTimeField("angelegt am", default=timezone.now)
    updated_at = models.DateTimeField("geändert am", auto_now=True)
    version = models.PositiveIntegerField("Version", default=1)

    class Meta:
        verbose_name = "Aufgabe"
        verbose_name_plural = "Aufgaben"
        ordering = ["due_date", "id"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(project__isnull=False, bucket__isnull=False, owner__isnull=True)
                    | Q(project__isnull=True, bucket__isnull=True, owner__isnull=False)
                ),
                name="tasks_task_project_or_personal",
                violation_error_message=(
                    "Projektaufgaben brauchen Projekt und Bucket, persönliche Aufgaben "
                    "einen Eigentümer und keinen Bucket."
                ),
            ),
            models.CheckConstraint(
                condition=(
                    Q(status="ERLEDIGT", completed_at__isnull=False, completed_by__isnull=False)
                    | Q(status="OFFEN", completed_at__isnull=True, completed_by__isnull=True)
                ),
                name="tasks_task_completion_consistent",
                violation_error_message="Erledigt nur mit Abschlusszeit und Person.",
            ),
        ]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["owner", "status"]),
        ]

    def __str__(self):
        return self.title

    @property
    def is_personal(self):
        return self.project_id is None

    @property
    def is_done(self):
        return self.status == TaskStatus.ERLEDIGT


class TaskAssignment(models.Model):
    """Zuweisung einer Person zu einer Projektaufgabe. Aktiv, solange ended_at leer ist."""

    task = models.ForeignKey(
        Task, on_delete=models.PROTECT, related_name="assignments", verbose_name="Aufgabe"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="task_assignments",
        verbose_name="Person",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    assigned_at = models.DateTimeField("zugewiesen am", default=timezone.now)
    ended_at = models.DateTimeField("beendet am", null=True, blank=True)
    ended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )

    class Meta:
        verbose_name = "Zuweisung"
        verbose_name_plural = "Zuweisungen"
        constraints = [
            models.UniqueConstraint(
                fields=["task", "user"],
                condition=Q(ended_at__isnull=True),
                name="tasks_assignment_one_active",
                violation_error_message="Die Person ist bereits zugewiesen.",
            ),
        ]

    def __str__(self):
        return f"{self.user} -> {self.task}"


class TaskEventKind(models.TextChoices):
    CREATED = "CREATED", "angelegt"
    UPDATED = "UPDATED", "geändert"
    COMPLETED = "COMPLETED", "abgeschlossen"
    REOPENED = "REOPENED", "wiedergeöffnet"
    ASSIGNED = "ASSIGNED", "zugewiesen"
    UNASSIGNED = "UNASSIGNED", "Zuweisung entfernt"


class TaskEventQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise AppendOnlyError("Verlaufseinträge sind unveränderlich.")

    def delete(self):
        raise AppendOnlyError("Verlaufseinträge sind unveränderlich.")


class TaskEvent(models.Model):
    """Nur anfügbarer Aufgabenverlauf (zusätzlich per Datenbank-Trigger geschützt, 0002)."""

    task = models.ForeignKey(
        Task, on_delete=models.PROTECT, related_name="events", verbose_name="Aufgabe"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+", verbose_name="Person"
    )
    kind = models.CharField("Ereignis", max_length=12, choices=TaskEventKind.choices)
    created_at = models.DateTimeField("Zeitpunkt", default=timezone.now)
    old_values = models.JSONField("alt", null=True, blank=True, encoder=DjangoJSONEncoder)
    new_values = models.JSONField("neu", null=True, blank=True, encoder=DjangoJSONEncoder)
    as_admin = models.BooleanField("als Administrator", default=False)

    objects = TaskEventQuerySet.as_manager()

    class Meta:
        verbose_name = "Aufgabenereignis"
        verbose_name_plural = "Aufgabenverlauf"
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.get_kind_display()} ({self.task})"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise AppendOnlyError("Verlaufseinträge sind unveränderlich.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise AppendOnlyError("Verlaufseinträge sind unveränderlich.")
