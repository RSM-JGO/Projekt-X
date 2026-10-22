import uuid

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class ProjectRole(models.TextChoices):
    PROJEKTLEITER = "PROJEKTLEITER", "Projektleiter"
    MITARBEITER = "MITARBEITER", "Mitarbeiter"
    MANAGEMENT = "MANAGEMENT", "Management"


class Project(models.Model):
    """Projekt. URLs verwenden ausschließlich public_id, nie den internen Schlüssel.

    Projektzeitraum (Etappe 4a): start_date/end_date bleiben die Anzeige. Bis zur ersten
    genehmigten Planversion sind sie direkt änderbar; danach ändern sie sich nur noch über die
    Genehmigung einer Planversion und werden dabei mitgeführt (apps.milestones.services).
    Prognose und Ist des Zeitraums sind aktuelle Werte; ihr Verlauf steht in den
    Terminänderungen (apps.milestones.models.DateChange).
    """

    public_id = models.UUIDField("öffentliche ID", default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField("Name", max_length=200)
    description = models.TextField("Beschreibung", blank=True)
    start_date = models.DateField("Beginn")
    end_date = models.DateField("Ende")
    forecast_start_date = models.DateField("Prognose Beginn", null=True, blank=True)
    forecast_end_date = models.DateField("Prognose Ende", null=True, blank=True)
    actual_start_date = models.DateField("Ist Beginn", null=True, blank=True)
    actual_end_date = models.DateField("Ist Ende", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="angelegt von",
    )
    created_at = models.DateTimeField("angelegt am", default=timezone.now)
    updated_at = models.DateTimeField("geändert am", auto_now=True)

    class Meta:
        verbose_name = "Projekt"
        verbose_name_plural = "Projekte"
        ordering = ["name", "id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gte=F("start_date")),
                name="projects_project_end_after_start",
                violation_error_message="Das Ende darf nicht vor dem Beginn liegen.",
            ),
        ]

    def __str__(self):
        return self.name


class ProjectMembership(models.Model):
    """Mitgliedschaft einer Person in einem Projekt. Aktiv, solange ended_at leer ist.

    Beendete Mitgliedschaften bleiben als Verlauf erhalten. Die Regeln "aktive
    Mitgliedschaft hat mindestens eine aktive Rolle" und "mindestens ein aktiver
    Projektleiter je Projekt" prüft apps.projects.services.
    """

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="memberships", verbose_name="Projekt"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="project_memberships",
        verbose_name="Person",
    )
    started_at = models.DateTimeField("Beginn", default=timezone.now)
    ended_at = models.DateTimeField("Ende", null=True, blank=True)

    class Meta:
        verbose_name = "Projektmitgliedschaft"
        verbose_name_plural = "Projektmitgliedschaften"
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                condition=Q(ended_at__isnull=True),
                name="projects_membership_one_active",
                violation_error_message="Die Person ist bereits Mitglied dieses Projekts.",
            ),
            models.CheckConstraint(
                condition=Q(ended_at__isnull=True) | Q(ended_at__gte=F("started_at")),
                name="projects_membership_end_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.user} in {self.project}"

    @property
    def is_active(self):
        return self.ended_at is None


class ProjectRoleAssignment(models.Model):
    """Projektrolle innerhalb einer Mitgliedschaft. Aktiv, solange ended_at leer ist."""

    membership = models.ForeignKey(
        ProjectMembership,
        on_delete=models.PROTECT,
        related_name="role_assignments",
        verbose_name="Mitgliedschaft",
    )
    role = models.CharField("Rolle", max_length=20, choices=ProjectRole.choices)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="vergeben von",
    )
    assigned_at = models.DateTimeField("vergeben am", default=timezone.now)
    ended_at = models.DateTimeField("beendet am", null=True, blank=True)
    ended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="beendet von",
    )

    class Meta:
        verbose_name = "Projektrolle"
        verbose_name_plural = "Projektrollen"
        constraints = [
            models.UniqueConstraint(
                fields=["membership", "role"],
                condition=Q(ended_at__isnull=True),
                name="projects_role_one_active",
                violation_error_message="Diese Rolle ist bereits aktiv vergeben.",
            ),
            models.CheckConstraint(
                condition=Q(ended_at__isnull=True) | Q(ended_at__gte=F("assigned_at")),
                name="projects_role_end_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.get_role_display()} ({self.membership})"

    @property
    def is_active(self):
        return self.ended_at is None
