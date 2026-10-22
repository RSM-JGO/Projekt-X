"""Standardkatalog M0–M5 (Orientierung, kein festes Phasenmodell; F12 bleibt offen).

Grundlage: docs/fachliche-orientierung-projektablauf.md und Skizze F19 v3. Die Daten werden
durch Migration 0003 in die Vorlagen-Tabellen geschrieben und beim Anlegen eines Projekts
**kopiert**, nie live verknüpft.

STANDARD_CATALOG_V1 entspricht dem Stand aus Migration 0003 (dort als eigene Kopie). Ein späterer
Standard kommt als neue Konstante mit eigener Datenmigration (oder über die spätere Pflegeseite).
"""

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


def write_catalog(milestone_template_model, deliverable_template_model, catalog):
    """Schreibt einen Katalog in leere Vorlagen-Tabellen (auch mit historischen Modellen)."""
    for position, spec in enumerate(catalog):
        template = milestone_template_model.objects.create(
            code=spec["code"],
            phase_name=spec["phase_name"],
            title=spec["title"],
            goal=spec["goal"],
            position=position,
        )
        for d_position, (title, required, area) in enumerate(spec["deliverables"]):
            deliverable_template_model.objects.create(
                milestone_template=template,
                title=title,
                required=required,
                area=area,
                position=d_position,
            )


PLAN_V1_REASON = "Erster Planstand aus dem Projektzeitraum"
PLAN_V1_REASON_MIGRATION = "Übernahme des bisherigen Projektzeitraums (Etappe 4a)"


def copy_catalog_to_project(models, project, created_by_id, reason):
    """Kopiert den Katalog in ein Projekt und legt Planversion 1 als Entwurf an.

    models: Zuordnung der Modellklassen (aktuelle oder historische aus einer Migration) unter
    den Schlüsseln MilestoneTemplate, Milestone, Deliverable, PlanVersion, PlanEntry.
    Die Kopie ist eigenständig; spätere Katalogänderungen wirken nicht auf das Projekt.
    """
    templates = (
        models["MilestoneTemplate"]
        .objects.prefetch_related("deliverables")
        .order_by("position", "id")
    )
    for position, template in enumerate(templates):
        milestone = models["Milestone"].objects.create(
            project_id=project.pk,
            code=template.code,
            phase_name=template.phase_name,
            title=template.title,
            goal=template.goal,
            position=position,
        )
        for d_position, dt in enumerate(
            sorted(template.deliverables.all(), key=lambda d: (d.position, d.id))
        ):
            models["Deliverable"].objects.create(
                project_id=project.pk,
                milestone=milestone,
                title=dt.title,
                required=dt.required,
                area=dt.area,
                position=d_position,
            )
    version = models["PlanVersion"].objects.create(
        project_id=project.pk,
        number=1,
        status="ENTWURF",
        reason=reason,
        created_by_id=created_by_id,
    )
    entry = models["PlanEntry"](
        project_id=project.pk,
        plan_version=version,
        kind="ZEITRAUM",
        start_date=project.start_date,
        end_date=project.end_date,
    )
    entry.save()
    return version


def ensure_standard_catalog():
    """Legt den Standardkatalog an, falls die Vorlagen fehlen (z. B. nach flush in Tests)."""
    from .models import DeliverableTemplate, MilestoneTemplate

    if not MilestoneTemplate.objects.exists():
        write_catalog(MilestoneTemplate, DeliverableTemplate, STANDARD_CATALOG_V1)
