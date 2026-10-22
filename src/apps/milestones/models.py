"""Meilensteine, Lieferobjekte, Freigaben, Planversionen und Terminänderungen (Etappe 4a).

Grundlage: docs/entwurf-datenmodell-projektbereich.md (bestätigt am 22.10.2026).

Datenbankregeln zusätzlich zu den Modellen (Migration 0002):
- zusammengesetzte Fremdschlüssel sichern, dass Lieferobjekte, Freigaben, Planeinträge und
  Terminänderungen zum selben Projekt gehören wie ihr Meilenstein bzw. ihre Planversion;
- Freigaben, Beteiligte und Terminänderungen sind nur anfügbar (Trigger gegen UPDATE, DELETE,
  TRUNCATE);
- genehmigte Planversionen und ihre Einträge sind unveränderlich; erlaubt ist nur der
  Statuswechsel genehmigt -> abgelöst.
"""

import uuid

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class AppendOnlyError(Exception):
    """Freigaben, Terminänderungen und genehmigte Planstände sind unveränderlich."""


class AppendOnlyQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise AppendOnlyError("Diese Einträge sind unveränderlich.")

    def delete(self):
        raise AppendOnlyError("Diese Einträge sind unveränderlich.")


class AppendOnlyModel(models.Model):
    objects = AppendOnlyQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise AppendOnlyError("Diese Einträge sind unveränderlich.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise AppendOnlyError("Diese Einträge sind unveränderlich.")


class Area(models.TextChoices):
    """Bereiche des Projekts in der Reihenfolge aus Entscheidung 006 (ohne Übersicht)."""

    STECKBRIEF = "steckbrief", "Steckbrief & Auftrag"
    KOMMUNIKATION = "kommunikation", "Kommunikation"
    TERMINE = "termine", "Termine & Zeitstrahl"
    AUFGABEN = "aufgaben", "Aufgaben"
    RISIKEN = "risiken", "Risiken & Chancen"
    AENDERUNGEN = "aenderungen", "Änderungen & Entscheidungen"
    PRODUKT = "produkt", "Produkt & Pilot"
    BERICHTE = "berichte", "Berichte"
    DOKUMENTE = "dokumente", "Dokumente"
    ABSCHLUSS = "abschluss", "Abschluss & Lessons Learned"


# ---------- Standardkatalog ----------


class MilestoneTemplate(models.Model):
    """Vorlage eines Standard-Meilensteins. Wird beim Anlegen eines Projekts kopiert."""

    code = models.CharField("Kürzel", max_length=10, unique=True)
    phase_name = models.CharField("Abschnitt", max_length=100)
    title = models.CharField("Titel", max_length=200)
    goal = models.TextField("Ziel", blank=True)
    position = models.PositiveIntegerField("Reihenfolge", default=0)

    class Meta:
        verbose_name = "Meilenstein-Vorlage"
        verbose_name_plural = "Meilenstein-Vorlagen"
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.code} {self.title}"


class DeliverableTemplate(models.Model):
    milestone_template = models.ForeignKey(
        MilestoneTemplate,
        on_delete=models.CASCADE,
        related_name="deliverables",
        verbose_name="Meilenstein-Vorlage",
    )
    title = models.CharField("Titel", max_length=200)
    required = models.BooleanField("Pflicht", default=False)
    area = models.CharField("Bereich", max_length=20, choices=Area.choices)
    position = models.PositiveIntegerField("Reihenfolge", default=0)

    class Meta:
        verbose_name = "Lieferobjekt-Vorlage"
        verbose_name_plural = "Lieferobjekt-Vorlagen"
        ordering = ["position", "id"]

    def __str__(self):
        return self.title


# ---------- Meilensteine und Lieferobjekte ----------


class MilestoneQuerySet(models.QuerySet):
    def delete(self):
        raise AppendOnlyError("Meilensteine werden nur ausgeblendet, nie gelöscht.")


class Milestone(models.Model):
    """Meilenstein eines Projekts. Wird nur ausgeblendet, nie gelöscht.

    Prognose und Ist sind aktuelle Werte; jede Änderung erzeugt eine Terminänderung (Verlauf).
    Der Plantermin steht in den Planversionen.
    """

    public_id = models.UUIDField("öffentliche ID", default=uuid.uuid4, unique=True, editable=False)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.PROTECT,
        related_name="milestones",
        verbose_name="Projekt",
    )
    code = models.CharField("Kürzel", max_length=10)
    phase_name = models.CharField("Abschnitt", max_length=100)
    title = models.CharField("Titel", max_length=200)
    goal = models.TextField("Ziel", blank=True)
    position = models.PositiveIntegerField("Reihenfolge", default=0)
    is_hidden = models.BooleanField("ausgeblendet", default=False)
    forecast_date = models.DateField("Prognose", null=True, blank=True)
    actual_date = models.DateField("Ist", null=True, blank=True)
    created_at = models.DateTimeField("angelegt am", default=timezone.now)

    objects = MilestoneQuerySet.as_manager()

    class Meta:
        verbose_name = "Meilenstein"
        verbose_name_plural = "Meilensteine"
        ordering = ["position", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "code"],
                name="milestones_milestone_code_unique",
                violation_error_message="Dieses Kürzel gibt es im Projekt bereits.",
            ),
            # Ziel der zusammengesetzten Fremdschlüssel (…, Projekt) -> Meilenstein, siehe 0002
            models.UniqueConstraint(
                fields=["id", "project"], name="milestones_milestone_id_project"
            ),
        ]

    def __str__(self):
        return f"{self.code} {self.title}"

    @property
    def label(self):
        return f"{self.code} {self.title}"

    def delete(self, *args, **kwargs):
        raise AppendOnlyError("Meilensteine werden nur ausgeblendet, nie gelöscht.")


class DeliverableStatus(models.TextChoices):
    FEHLT = "FEHLT", "fehlt"
    IN_ARBEIT = "IN_ARBEIT", "in Arbeit"
    VORHANDEN = "VORHANDEN", "vorhanden"


class Deliverable(models.Model):
    """Lieferobjekt eines Meilensteins. Status wird in 4a manuell gepflegt."""

    public_id = models.UUIDField("öffentliche ID", default=uuid.uuid4, unique=True, editable=False)
    project = models.ForeignKey(
        "projects.Project", on_delete=models.PROTECT, related_name="+", verbose_name="Projekt"
    )
    milestone = models.ForeignKey(
        Milestone, on_delete=models.PROTECT, related_name="deliverables", verbose_name="Meilenstein"
    )
    title = models.CharField("Titel", max_length=200)
    required = models.BooleanField("Pflicht", default=False)
    area = models.CharField("Bereich", max_length=20, choices=Area.choices)
    status = models.CharField(
        "Status", max_length=10, choices=DeliverableStatus.choices, default=DeliverableStatus.FEHLT
    )
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="verantwortlich",
    )
    note = models.TextField("Notiz", blank=True)
    position = models.PositiveIntegerField("Reihenfolge", default=0)
    created_at = models.DateTimeField("angelegt am", default=timezone.now)
    updated_at = models.DateTimeField("geändert am", auto_now=True)

    class Meta:
        verbose_name = "Lieferobjekt"
        verbose_name_plural = "Lieferobjekte"
        ordering = ["position", "id"]

    def __str__(self):
        return self.title

    @property
    def is_present(self):
        return self.status == DeliverableStatus.VORHANDEN


# ---------- Planversionen ----------


class PlanStatus(models.TextChoices):
    ENTWURF = "ENTWURF", "Entwurf"
    GENEHMIGT = "GENEHMIGT", "genehmigt"
    ABGELOEST = "ABGELOEST", "abgelöst"


class PlanVersion(models.Model):
    """Planstand eines Projekts. Je Projekt höchstens ein Entwurf und eine gültige Genehmigung.

    Genehmigte Versionen sind unveränderlich (Code-Sperre und Trigger, 0002); erlaubt ist nur
    der Wechsel genehmigt -> abgelöst, wenn eine neuere Version genehmigt wird.
    """

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.PROTECT,
        related_name="plan_versions",
        verbose_name="Projekt",
    )
    number = models.PositiveIntegerField("Nummer")
    status = models.CharField(
        "Status", max_length=10, choices=PlanStatus.choices, default=PlanStatus.ENTWURF
    )
    reason = models.TextField("Anlass", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="angelegt von",
    )
    created_at = models.DateTimeField("angelegt am", default=timezone.now)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="genehmigt von",
    )
    approved_at = models.DateTimeField("genehmigt am", null=True, blank=True)
    approved_as_admin = models.BooleanField("als Administrator genehmigt", default=False)

    class Meta:
        verbose_name = "Planversion"
        verbose_name_plural = "Planversionen"
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "number"], name="milestones_planversion_number_unique"
            ),
            models.UniqueConstraint(
                fields=["project"],
                condition=Q(status="ENTWURF"),
                name="milestones_planversion_one_draft",
                violation_error_message="Es gibt bereits einen Planentwurf.",
            ),
            models.UniqueConstraint(
                fields=["project"],
                condition=Q(status="GENEHMIGT"),
                name="milestones_planversion_one_approved",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status="ENTWURF", approved_by__isnull=True, approved_at__isnull=True)
                    | (
                        Q(status__in=["GENEHMIGT", "ABGELOEST"])
                        & Q(approved_by__isnull=False, approved_at__isnull=False)
                    )
                ),
                name="milestones_planversion_approval_consistent",
            ),
            models.UniqueConstraint(
                fields=["id", "project"], name="milestones_planversion_id_project"
            ),
        ]

    def __str__(self):
        return f"Planversion {self.number} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            stored = PlanVersion.objects.filter(pk=self.pk).values_list("status", flat=True).first()
            if stored != PlanStatus.ENTWURF:
                raise AppendOnlyError("Genehmigte Planversionen sind unveränderlich.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise AppendOnlyError("Planversionen werden nicht gelöscht.")

    @property
    def is_draft(self):
        return self.status == PlanStatus.ENTWURF


class PlanEntryKind(models.TextChoices):
    ZEITRAUM = "ZEITRAUM", "Projektzeitraum"
    MEILENSTEIN = "MEILENSTEIN", "Meilenstein"


class PlanEntry(models.Model):
    """Eintrag einer Planversion: Projektzeitraum oder Termin eines Meilensteins."""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.PROTECT, related_name="+", verbose_name="Projekt"
    )
    plan_version = models.ForeignKey(
        PlanVersion, on_delete=models.PROTECT, related_name="entries", verbose_name="Planversion"
    )
    kind = models.CharField("Art", max_length=12, choices=PlanEntryKind.choices)
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="plan_entries",
        verbose_name="Meilenstein",
    )
    start_date = models.DateField("Beginn", null=True, blank=True)
    end_date = models.DateField("Ende", null=True, blank=True)
    date = models.DateField("Termin", null=True, blank=True)

    class Meta:
        verbose_name = "Planeintrag"
        verbose_name_plural = "Planeinträge"
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        kind="ZEITRAUM",
                        milestone__isnull=True,
                        date__isnull=True,
                        start_date__isnull=False,
                        end_date__isnull=False,
                        end_date__gte=F("start_date"),
                    )
                    | Q(
                        kind="MEILENSTEIN",
                        milestone__isnull=False,
                        date__isnull=False,
                        start_date__isnull=True,
                        end_date__isnull=True,
                    )
                ),
                name="milestones_planentry_kind_consistent",
            ),
            models.UniqueConstraint(
                fields=["plan_version"],
                condition=Q(kind="ZEITRAUM"),
                name="milestones_planentry_one_period",
            ),
            models.UniqueConstraint(
                fields=["plan_version", "milestone"], name="milestones_planentry_one_per_milestone"
            ),
        ]

    def __str__(self):
        if self.kind == PlanEntryKind.ZEITRAUM:
            return f"Zeitraum {self.start_date} – {self.end_date}"
        return f"{self.milestone}: {self.date}"

    def save(self, *args, **kwargs):
        if self.plan_version.status != PlanStatus.ENTWURF:
            raise AppendOnlyError("Einträge genehmigter Planversionen sind unveränderlich.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.plan_version.status != PlanStatus.ENTWURF:
            raise AppendOnlyError("Einträge genehmigter Planversionen sind unveränderlich.")
        return super().delete(*args, **kwargs)


# ---------- Freigaben ----------


class ApprovalLight(models.TextChoices):
    GRUEN = "GRUEN", "Grün – Freigabe erteilt"
    ORANGE = "ORANGE", "Orange – Freigabe unter Auflagen"
    ROT = "ROT", "Rot – keine Freigabe"


class Approval(AppendOnlyModel):
    """Freigabeentscheidung zu einem Meilenstein. Unveränderlich; Korrektur = neue Freigabe.

    missing_required ist der Schnappschuss der zum Zeitpunkt der Freigabe fehlenden
    Pflicht-Lieferobjekte (Liste aus {"id", "title", "status"}).
    """

    public_id = models.UUIDField("öffentliche ID", default=uuid.uuid4, unique=True, editable=False)
    project = models.ForeignKey(
        "projects.Project", on_delete=models.PROTECT, related_name="+", verbose_name="Projekt"
    )
    milestone = models.ForeignKey(
        Milestone, on_delete=models.PROTECT, related_name="approvals", verbose_name="Meilenstein"
    )
    light = models.CharField("Ampel", max_length=6, choices=ApprovalLight.choices)
    decision = models.TextField("Entscheidung")
    decided_on = models.DateField("Datum")
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ApprovalParticipant",
        related_name="+",
        verbose_name="Beteiligte",
    )
    external_participants = models.TextField("weitere Beteiligte", blank=True)
    basis = models.TextField("Grundlage", blank=True)
    conditions = models.TextField("Auflagen", blank=True)
    valid_until = models.DateField("gültig bis", null=True, blank=True)
    plan_version = models.ForeignKey(
        PlanVersion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Planversion",
    )
    missing_required = models.JSONField(
        "fehlende Pflichtdokumente", default=list, blank=True, encoder=DjangoJSONEncoder
    )
    warning_confirmed = models.BooleanField("Warnung bestätigt", default=False)
    replaces = models.OneToOneField(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="replaced_by",
        verbose_name="ersetzt",
    )
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="erteilt von",
    )
    as_admin = models.BooleanField("als Administrator", default=False)
    created_at = models.DateTimeField("erfasst am", default=timezone.now)

    class Meta:
        verbose_name = "Freigabe"
        verbose_name_plural = "Freigaben"
        ordering = ["created_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(light="ORANGE") | ~Q(conditions=""),
                name="milestones_approval_orange_needs_conditions",
                violation_error_message="Orange braucht Auflagen.",
            ),
            models.CheckConstraint(
                condition=Q(light="ROT") | Q(missing_required=[]) | Q(warning_confirmed=True),
                name="milestones_approval_missing_confirmed",
                violation_error_message="Fehlende Pflichtdokumente müssen bestätigt werden.",
            ),
            models.CheckConstraint(
                condition=Q(replaces__isnull=True) | ~Q(replaces=F("id")),
                name="milestones_approval_not_self",
            ),
            # Ziel des Fremdschlüssels (ersetzt, Meilenstein) -> Freigabe, siehe 0002
            models.UniqueConstraint(
                fields=["id", "milestone"], name="milestones_approval_id_milestone"
            ),
        ]

    def __str__(self):
        return f"{self.milestone}: {self.get_light_display()} ({self.decided_on})"

    @property
    def is_positive(self):
        return self.light in (ApprovalLight.GRUEN, ApprovalLight.ORANGE)

    def is_valid_on(self, day):
        return self.is_positive and (self.valid_until is None or self.valid_until >= day)


class ApprovalParticipant(AppendOnlyModel):
    approval = models.ForeignKey(
        Approval, on_delete=models.PROTECT, related_name="participant_links"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    display_name = models.CharField("Name (Stand)", max_length=200)

    class Meta:
        verbose_name = "Beteiligte Person"
        verbose_name_plural = "Beteiligte Personen"
        constraints = [
            models.UniqueConstraint(
                fields=["approval", "user"], name="milestones_participant_unique"
            )
        ]

    def __str__(self):
        return self.display_name


# ---------- Terminänderungen (Prognose und Ist) ----------


class DatePoint(models.TextChoices):
    BEGINN = "BEGINN", "Beginn"
    ENDE = "ENDE", "Ende"
    TERMIN = "TERMIN", "Termin"


class DateKind(models.TextChoices):
    PROGNOSE = "PROGNOSE", "Prognose"
    IST = "IST", "Ist"


class DateChange(AppendOnlyModel):
    """Nur anfügbarer Verlauf jeder Prognose- und Ist-Änderung (alt, neu, Person, Begründung).

    Ziel ist entweder der Projektzeitraum (Meilenstein leer; Beginn oder Ende) oder ein
    Meilenstein (Termin).
    """

    project = models.ForeignKey(
        "projects.Project", on_delete=models.PROTECT, related_name="+", verbose_name="Projekt"
    )
    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="date_changes",
        verbose_name="Meilenstein",
    )
    point = models.CharField("Terminpunkt", max_length=6, choices=DatePoint.choices)
    kind = models.CharField("Art", max_length=8, choices=DateKind.choices)
    old_value = models.DateField("alt", null=True, blank=True)
    new_value = models.DateField("neu", null=True, blank=True)
    reason = models.TextField("Begründung")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+", verbose_name="Person"
    )
    as_admin = models.BooleanField("als Administrator", default=False)
    created_at = models.DateTimeField("Zeitpunkt", default=timezone.now)

    class Meta:
        verbose_name = "Terminänderung"
        verbose_name_plural = "Terminänderungen"
        ordering = ["created_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(milestone__isnull=True, point__in=["BEGINN", "ENDE"])
                    | Q(milestone__isnull=False, point="TERMIN")
                ),
                name="milestones_datechange_target_consistent",
            ),
            models.CheckConstraint(condition=~Q(reason=""), name="milestones_datechange_reason"),
        ]

    def __str__(self):
        return f"{self.get_kind_display()} {self.old_value} -> {self.new_value}"
