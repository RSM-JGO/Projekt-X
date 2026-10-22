from django.db import migrations

# Standardkatalog M0–M5 anlegen und jedem bestehenden Projekt eine eigene Kopie geben:
# Meilensteine mit Standard-Lieferobjekten (Status „fehlt“) und Planversion 1 als **Entwurf**
# aus dem bisherigen Projektzeitraum (Benutzerentscheidung 22.10.2026: ehrlich, weil es noch
# keine echte Genehmigung gab).
#
# Die Migration ist bewusst eigenständig: Katalogdaten und Logik sind hierher kopiert und
# arbeiten nur mit historischen Modellen (apps.get_model). Spätere Änderungen an
# apps/milestones/catalog.py wirken nicht auf diese Migration.

PLAN_V1_REASON_MIGRATION = "Übernahme des bisherigen Projektzeitraums (Etappe 4a)"

# Bereichsschlüssel siehe models.Area
STANDARD_CATALOG_V1 = (
    {
        "code": "M0",
        "phase_name": "Auftragsklärung",
        "title": "Start Projektauftrag",
        "goal": "Klären, was das Projekt erreichen soll, wen es betrifft und wie kritisch es ist.",
        "deliverables": (
            ("Projektsteckbrief", True, "steckbrief"),
            ("Stakeholderliste", True, "kommunikation"),
            ("Kommunikationsmatrix", False, "kommunikation"),
            ("Erste Einschätzung der Kritikalität", False, "steckbrief"),
        ),
    },
    {
        "code": "M1",
        "phase_name": "Initiierung",
        "title": "Projektfreigabe",
        "goal": (
            "Auftrag, Verantwortlichkeiten und Risiken so weit klären, dass über die "
            "Projektfreigabe entschieden werden kann."
        ),
        "deliverables": (
            ("Projektauftrag (Ziele, Scope, Business Case, Toleranzen)", True, "steckbrief"),
            ("Termin- und Phasenplan", True, "termine"),
            ("RACI-Matrix", True, "kommunikation"),
            ("Risikoliste mit Gefahren und Chancen", True, "risiken"),
            ("Kommunikationsplan", False, "kommunikation"),
        ),
    },
    {
        "code": "M2",
        "phase_name": "Vorbereitung",
        "title": "Pilotfreigabe",
        "goal": "Produkt beschreiben, Abnahmekriterien vereinbaren und den Pilot vorbereiten.",
        "deliverables": (
            ("Spezifikation / Produktbeschreibung", True, "produkt"),
            ("Abnahmekriterien", True, "produkt"),
            ("Pilotplan", True, "produkt"),
            ("Risikoliste aktualisiert", False, "risiken"),
            ("Statusbericht", False, "berichte"),
        ),
    },
    {
        "code": "M3",
        "phase_name": "Pilot",
        "title": "Skalierungsfreigabe",
        "goal": (
            "Pilot durchführen, Ergebnisse bewerten und die Go-/No-Go-Entscheidung vorbereiten."
        ),
        "deliverables": (
            ("Pilotbericht", True, "produkt"),
            ("Defektliste mit Maßnahmen", True, "produkt"),
            ("Go-/No-Go-Entscheidung", True, "aenderungen"),
        ),
    },
    {
        "code": "M4",
        "phase_name": "Rollout",
        "title": "Rolloutfreigabe",
        "goal": (
            "Rollout übergreifend steuern: Ziele, Fortschritt, Risiken, Kosten und Änderungen im "
            "Blick behalten. Die operative Rolloutplanung liegt beim Rolloutmanagement."
        ),
        "deliverables": (
            ("Change- und Entscheidungslog aktuell", True, "aenderungen"),
            ("Statusbericht", True, "berichte"),
            ("Risikoliste aktualisiert", False, "risiken"),
        ),
    },
    {
        "code": "M5",
        "phase_name": "Abschluss",
        "title": "Abschlussfreigabe",
        "goal": "Zielerreichung bewerten, Restpunkte übergeben und Erfahrungen festhalten.",
        "deliverables": (
            ("Abschlussbericht", True, "abschluss"),
            ("Lessons Learned", True, "abschluss"),
            ("Restpunkte übergeben", False, "abschluss"),
        ),
    },
)


def write_catalog(MilestoneTemplate, DeliverableTemplate):
    for position, spec in enumerate(STANDARD_CATALOG_V1):
        template = MilestoneTemplate.objects.create(
            code=spec["code"],
            phase_name=spec["phase_name"],
            title=spec["title"],
            goal=spec["goal"],
            position=position,
        )
        for d_position, (title, required, area) in enumerate(spec["deliverables"]):
            DeliverableTemplate.objects.create(
                milestone_template=template,
                title=title,
                required=required,
                area=area,
                position=d_position,
            )


def copy_catalog_to_project(apps, project):
    MilestoneTemplate = apps.get_model("milestones", "MilestoneTemplate")
    Milestone = apps.get_model("milestones", "Milestone")
    Deliverable = apps.get_model("milestones", "Deliverable")
    PlanVersion = apps.get_model("milestones", "PlanVersion")
    PlanEntry = apps.get_model("milestones", "PlanEntry")
    templates = MilestoneTemplate.objects.prefetch_related("deliverables").order_by("position", "id")
    for position, template in enumerate(templates):
        milestone = Milestone.objects.create(
            project_id=project.pk,
            code=template.code,
            phase_name=template.phase_name,
            title=template.title,
            goal=template.goal,
            position=position,
        )
        deliverables = sorted(template.deliverables.all(), key=lambda d: (d.position, d.id))
        for d_position, dt in enumerate(deliverables):
            Deliverable.objects.create(
                project_id=project.pk,
                milestone=milestone,
                title=dt.title,
                required=dt.required,
                area=dt.area,
                position=d_position,
            )
    version = PlanVersion.objects.create(
        project_id=project.pk,
        number=1,
        status="ENTWURF",
        reason=PLAN_V1_REASON_MIGRATION,
        created_by_id=project.created_by_id,
    )
    PlanEntry.objects.create(
        project_id=project.pk,
        plan_version=version,
        kind="ZEITRAUM",
        start_date=project.start_date,
        end_date=project.end_date,
    )


def forwards(apps, schema_editor):
    MilestoneTemplate = apps.get_model("milestones", "MilestoneTemplate")
    DeliverableTemplate = apps.get_model("milestones", "DeliverableTemplate")
    Milestone = apps.get_model("milestones", "Milestone")
    Project = apps.get_model("projects", "Project")
    if not MilestoneTemplate.objects.exists():
        write_catalog(MilestoneTemplate, DeliverableTemplate)
    for project in Project.objects.order_by("id"):
        if not Milestone.objects.filter(project_id=project.pk).exists():
            copy_catalog_to_project(apps, project)


class Migration(migrations.Migration):
    dependencies = [
        ("milestones", "0002_composite_fks_and_append_only"),
        ("projects", "0002_project_forecast_actual"),
    ]

    # Rückwärts nicht umkehrbar: Planstände sind nur anfügbar (Trigger aus 0002)
    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
