import datetime
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.milestones import selectors as milestone_selectors
from apps.milestones import services as milestone_services
from apps.milestones.models import Deliverable, Milestone
from apps.projects import services
from apps.projects.models import Project, ProjectMembership, ProjectRole
from apps.tasks import services as task_services
from apps.tasks.models import Bucket, Task
from apps.tasks.selectors import today

# Beispieldaten: klar gekennzeichnet, nicht zustellbare Domain (.invalid, RFC 2606)
# Einziges Konto mit Administratorrechten ist das ausdrücklich benannte Vorführkonto admin@.
DEMO_USERS = {
    "admin": {
        "email": "admin@beispiel.invalid",
        "display_name": "Alex Admin – Vorführkonto Administrator (Beispiel)",
        "is_admin": True,
    },
    "pl": {
        "email": "projektleitung@beispiel.invalid",
        "display_name": "Paula Leitner (Beispiel)",
        "can_create_projects": True,
    },
    "ma1": {"email": "mitarbeiter1@beispiel.invalid", "display_name": "Max Muster (Beispiel)"},
    "ma2": {"email": "mitarbeiter2@beispiel.invalid", "display_name": "Mia Beispiel (Beispiel)"},
    "mgmt": {
        "email": "management@beispiel.invalid",
        "display_name": "Martin Management (Beispiel)",
    },
}

DEMO_PROJECTS = {
    "A": {
        "name": "Beispielprojekt A – Netzwerkerneuerung (Beispiel)",
        "description": "Erfundenes Beispielprojekt für die Entwicklung. Keine echten Daten.",
        "start_date": datetime.date(2026, 9, 1),
        "end_date": datetime.date(2027, 3, 31),
        "members": {
            "ma1": [ProjectRole.MITARBEITER],
            "ma2": [ProjectRole.MITARBEITER],
            "mgmt": [ProjectRole.MANAGEMENT],
        },
        "milestone_dates": {
            "M0": datetime.date(2026, 9, 15),
            "M1": datetime.date(2026, 10, 15),
            "M2": datetime.date(2026, 12, 1),
            "M3": datetime.date(2027, 1, 20),
            "M4": datetime.date(2027, 3, 1),
            "M5": datetime.date(2027, 3, 31),
        },
        # (Meilenstein, Lieferobjekt-Titelanfang) -> Status
        "deliverable_status": {
            ("M0", "Projektsteckbrief"): "VORHANDEN",
            ("M0", "Stakeholderliste"): "VORHANDEN",
            ("M0", "Kommunikationsmatrix"): "IN_ARBEIT",
            ("M0", "Erste Einschätzung"): "VORHANDEN",
            ("M1", "Projektauftrag"): "VORHANDEN",
            ("M1", "Termin- und Phasenplan"): "VORHANDEN",
            ("M1", "RACI-Matrix"): "IN_ARBEIT",
            ("M1", "Risikoliste"): "VORHANDEN",
            ("M1", "Kommunikationsplan"): "IN_ARBEIT",
            ("M2", "Spezifikation"): "IN_ARBEIT",
        },
        "responsible": {("M2", "Spezifikation"): "ma1", ("M2", "Abnahmekriterien"): "ma2"},
        # (Meilenstein, Ampel, Entscheidung, Auflagen)
        "approvals": [
            ("M0", "GRUEN", "Start Projektauftrag freigegeben (Beispiel)", ""),
            (
                "M1",
                "ORANGE",
                "Projektfreigabe unter Auflagen erteilt (Beispiel)",
                "RACI-Matrix bis zur Pilotfreigabe vervollständigen (Beispiel)",
            ),
        ],
        "actual": {"M0": datetime.date(2026, 9, 15), "M1": datetime.date(2026, 10, 15)},
        "forecast": {
            "M2": (
                datetime.date(2026, 12, 8),
                "Abstimmung mit dem Fachbereich dauert länger (Beispiel)",
            )
        },
        "buckets": ["Planung", "Umsetzung", "Abnahme"],
        # (Titel, Bucket, Fälligkeit in Tagen ab heute oder None, Zuständige, erledigt von)
        "tasks": [
            ("Bestandsaufnahme Switches", "Planung", -3, ["ma1"], None),
            ("Lieferant für Access Points anfragen", "Planung", 0, ["pl", "ma1"], None),
            ("Testaufbau im Labor", "Umsetzung", 5, ["ma2"], None),
            ("Verkabelungsplan prüfen", "Umsetzung", 12, ["ma1", "ma2"], None),
            ("Kick-off durchführen", "Planung", -10, ["pl"], "pl"),
            ("Abnahmeprotokoll vorbereiten", "Abnahme", None, [], None),
        ],
    },
    "B": {
        "name": "Beispielprojekt B – Druckerumstellung (Beispiel)",
        "description": "Zweites erfundenes Beispielprojekt zum Prüfen der Projektgrenzen.",
        "start_date": datetime.date(2026, 10, 1),
        "end_date": datetime.date(2026, 12, 18),
        "members": {"ma1": [ProjectRole.MITARBEITER]},
        "milestone_dates": {
            "M0": datetime.date(2026, 10, 5),
            "M1": datetime.date(2026, 10, 20),
            "M2": datetime.date(2026, 11, 10),
            "M3": datetime.date(2026, 11, 25),
            "M4": datetime.date(2026, 12, 10),
            "M5": datetime.date(2026, 12, 18),
        },
        "deliverable_status": {
            ("M0", "Projektsteckbrief"): "IN_ARBEIT",
            ("M0", "Stakeholderliste"): "VORHANDEN",
        },
        "responsible": {("M0", "Projektsteckbrief"): "ma1"},
        "approvals": [],
        "actual": {},
        "forecast": {},
        "buckets": ["Vorbereitung", "Rollout"],
        "tasks": [
            ("Druckerstandorte erfassen", "Vorbereitung", -1, ["ma1"], None),
            ("Treiberpaket testen", "Vorbereitung", 3, ["ma1", "pl"], None),
            ("Pilotstandort umstellen", "Rollout", 14, ["ma1"], None),
            ("Altgeräte-Liste abstimmen", "Vorbereitung", -5, ["ma1"], "ma1"),
            ("Rollout-Zeitplan kommunizieren", "Rollout", 7, ["pl"], None),
            ("Restposten klären", "Rollout", None, [], None),
        ],
    },
}


DEMO_PERSONAL = {
    "pl": [("Urlaubsvertretung organisieren (Beispiel)", 2)],
    "ma1": [("Schulung Netzwerkgrundlagen buchen (Beispiel)", None)],
}


class Command(BaseCommand):
    help = "Lädt gekennzeichnete Beispielkonten und -projekte (nur mit DEBUG, mehrfach ausführbar)."

    def handle(self, *args, **options):
        instance = getattr(settings, "PX_INSTANCE", "dev")
        if instance == "prod":
            raise CommandError("seed_demo ist in der Instanz prod immer gesperrt.")
        if not (settings.DEBUG or instance == "demo"):
            raise CommandError(
                "seed_demo ist nur in der Entwicklung (DEBUG=1) oder in der Instanz demo erlaubt."
            )
        password = os.environ.get("DEMO_PASSWORD", "")
        if not password or password == "HIER_EINTRAGEN":
            raise CommandError("Umgebungsvariable DEMO_PASSWORD fehlt (siehe .env.example).")

        with transaction.atomic():
            users = {key: self._user(spec, password) for key, spec in DEMO_USERS.items()}
            for spec in DEMO_PROJECTS.values():
                project = self._project(spec, users)
                self._tasks(project, spec, users)
                self._journey(project, spec, users)
            self._personal(users)

        self.stdout.write(
            self.style.SUCCESS(
                f"Beispieldaten bereit: {len(DEMO_USERS)} Konten, {len(DEMO_PROJECTS)} Projekte. "
                "Passwort: Wert von DEMO_PASSWORD."
            )
        )

    def _user(self, spec, password):
        User = get_user_model()
        defaults = {
            "display_name": spec["display_name"],
            "is_admin": spec.get("is_admin", False),
            "can_create_projects": spec.get("can_create_projects", False),
            "is_active": True,
        }
        user, _created = User.objects.update_or_create(email=spec["email"], defaults=defaults)
        if not user.check_password(password):
            user.set_password(password)
            user.save(update_fields=["password"])
        return user

    def _project(self, spec, users):
        lead = users["pl"]
        project = Project.objects.filter(name=spec["name"], created_by=lead).first()
        if project is None:
            project = services.create_project(
                actor=lead,
                name=spec["name"],
                description=spec["description"],
                start_date=spec["start_date"],
                end_date=spec["end_date"],
            )
        for key, roles in spec["members"].items():
            member = users[key]
            active = ProjectMembership.objects.filter(
                project=project, user=member, ended_at__isnull=True
            ).exists()
            if not active:
                services.add_member(actor=lead, project=project, user=member, roles=roles)
        return project

    def _tasks(self, project, spec, users):
        lead = users["pl"]
        buckets = {}
        for name in spec["buckets"]:
            bucket = Bucket.objects.filter(project=project, name=name, is_archived=False).first()
            buckets[name] = bucket or task_services.create_bucket(
                actor=lead, project=project, name=name
            )
        on = today()
        for title, bucket_name, offset, assignee_keys, done_by in spec["tasks"]:
            if Task.objects.filter(project=project, title=title).exists():
                continue
            task = task_services.create_project_task(
                actor=lead,
                project=project,
                bucket=buckets[bucket_name],
                title=title,
                description="Beispielaufgabe, keine echten Daten.",
                due_date=None if offset is None else on + datetime.timedelta(days=offset),
                assignees=[users[k] for k in assignee_keys],
            )
            if done_by:
                task_services.complete_task(actor=users[done_by], task=task)

    def _personal(self, users):
        on = today()
        for key, items in DEMO_PERSONAL.items():
            owner = users[key]
            for title, offset in items:
                if Task.objects.filter(owner=owner, title=title).exists():
                    continue
                task_services.create_personal_task(
                    actor=owner,
                    title=title,
                    due_date=None if offset is None else on + datetime.timedelta(days=offset),
                )

    def _journey(self, project, spec, users):
        """Etappe 4a: Plan genehmigen, Lieferobjekt-Status, Freigaben, Prognose/Ist (idempotent)."""
        lead = users["pl"]
        on = today()
        milestones = {m.code: m for m in Milestone.objects.filter(project=project)}

        def deliverable(code, prefix):
            return Deliverable.objects.filter(
                milestone=milestones[code], title__startswith=prefix
            ).first()

        if not milestone_services.period_locked(project):
            draft = milestone_services.draft_version(
                project
            ) or milestone_services.create_plan_draft(
                actor=lead, project=project, reason="Beispielplan (Beispiel)"
            )
            milestone_services.update_plan_draft(
                actor=lead,
                project=project,
                version=draft,
                start_date=project.start_date,
                end_date=project.end_date,
                milestone_dates=[(milestones[c], d) for c, d in spec["milestone_dates"].items()],
                reason="Beispielplan zum Projektstart (Beispiel)",
            )
            milestone_services.approve_plan_version(actor=lead, project=project, version=draft)

        for (code, prefix), key in spec["responsible"].items():
            d = deliverable(code, prefix)
            if d is not None and d.responsible_id is None:
                milestone_services.update_deliverable(
                    actor=lead, project=project, deliverable=d, responsible=users[key]
                )
        for (code, prefix), status in spec["deliverable_status"].items():
            d = deliverable(code, prefix)
            if d is not None and d.status == "FEHLT" and status != "FEHLT":
                milestone_services.set_deliverable_status(
                    actor=lead, project=project, deliverable=d, status=status
                )

        for code, light, decision, conditions in spec["approvals"]:
            milestone = milestones[code]
            if milestone.approvals.exists():
                continue
            missing = milestone_services.missing_required(milestone)
            milestone_services.grant_approval(
                actor=lead,
                project=project,
                milestone=milestone,
                light=light,
                decision=decision,
                decided_on=min(spec["milestone_dates"][code], on),
                participants=[lead, users["mgmt"]],
                external_participants="Auftraggeberin (Beispiel)",
                basis="Lieferobjekte laut Meilensteinseite (Beispiel)",
                conditions=conditions,
                confirmed_missing=[m["id"] for m in missing],
            )

        for code, value in spec["actual"].items():
            milestone = milestones[code]
            if milestone.actual_date is None and value <= on:
                milestone_services.change_date(
                    actor=lead,
                    project=project,
                    milestone=milestone,
                    kind="IST",
                    value=value,
                    reason="Meilenstein erreicht (Beispiel)",
                )
        for code, (value, reason) in spec["forecast"].items():
            milestone = milestones[code]
            if milestone.forecast_date is None:
                milestone_services.change_date(
                    actor=lead,
                    project=project,
                    milestone=milestone,
                    kind="PROGNOSE",
                    value=value,
                    reason=reason,
                )
        # Abgeleiteten Zustand einmal berechnen (fällt bei Fehlern im Seed sofort auf)
        milestone_selectors.journey(project)
