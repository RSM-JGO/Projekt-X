import datetime
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

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
