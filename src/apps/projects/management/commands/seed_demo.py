import datetime
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.projects import services
from apps.projects.models import Project, ProjectMembership, ProjectRole

# Beispieldaten: klar gekennzeichnet, nicht zustellbare Domain (.invalid, RFC 2606)
DEMO_USERS = {
    "admin": {
        "email": "admin@beispiel.invalid",
        "display_name": "Alex Admin (Beispiel)",
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
    },
    "B": {
        "name": "Beispielprojekt B – Druckerumstellung (Beispiel)",
        "description": "Zweites erfundenes Beispielprojekt zum Prüfen der Projektgrenzen.",
        "start_date": datetime.date(2026, 10, 1),
        "end_date": datetime.date(2026, 12, 18),
        "members": {"ma1": [ProjectRole.MITARBEITER]},
    },
}


class Command(BaseCommand):
    help = "Lädt gekennzeichnete Beispielkonten und -projekte (nur mit DEBUG, mehrfach ausführbar)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_demo ist nur in der Entwicklungsumgebung (DEBUG=1) erlaubt.")
        password = os.environ.get("DEMO_PASSWORD", "")
        if not password or password == "HIER_EINTRAGEN":
            raise CommandError("Umgebungsvariable DEMO_PASSWORD fehlt (siehe .env.example).")

        with transaction.atomic():
            users = {key: self._user(spec, password) for key, spec in DEMO_USERS.items()}
            for spec in DEMO_PROJECTS.values():
                self._project(spec, users)

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
