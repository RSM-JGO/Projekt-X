from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone


class AppendOnlyError(Exception):
    """Protokolleinträge dürfen weder geändert noch gelöscht werden."""


class AuditLogQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise AppendOnlyError("Protokolleinträge sind unveränderlich.")

    def delete(self):
        raise AppendOnlyError("Protokolleinträge sind unveränderlich.")


class AuditLog(models.Model):
    """Nur anfügbares Änderungsprotokoll: wer, wann, was, alter und neuer Wert.

    Zusätzlich zur Sperre im Code verhindert ein Datenbank-Trigger (Migration 0002)
    UPDATE und DELETE auf dieser Tabelle.
    """

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="Person",
    )
    actor_label = models.CharField("Person (Stand)", max_length=300)
    action = models.CharField("Aktion", max_length=64)
    object_type = models.CharField("Objekttyp", max_length=64)
    object_id = models.CharField("Objekt-ID", max_length=64)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_entries",
        verbose_name="Projekt",
    )
    as_admin = models.BooleanField(
        "als Administrator",
        default=False,
        help_text="Änderung über die Administratorbefugnis statt über eine Projektrolle",
    )
    created_at = models.DateTimeField("Zeitpunkt", default=timezone.now, db_index=True)
    old_values = models.JSONField("alt", null=True, blank=True, encoder=DjangoJSONEncoder)
    new_values = models.JSONField("neu", null=True, blank=True, encoder=DjangoJSONEncoder)

    objects = AuditLogQuerySet.as_manager()

    class Meta:
        verbose_name = "Protokolleintrag"
        verbose_name_plural = "Protokolleinträge"
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["project", "created_at"])]

    def __str__(self):
        return f"{self.created_at:%d.%m.%Y %H:%M} {self.actor_label}: {self.action}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise AppendOnlyError("Protokolleinträge sind unveränderlich.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise AppendOnlyError("Protokolleinträge sind unveränderlich.")
