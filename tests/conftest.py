import datetime

import pytest
from django.contrib.auth import get_user_model
from django.db import connection

from apps.projects import services
from apps.projects.models import ProjectRole

PASSWORT = "Test-Passwort-fuer-Tests-123"

# Etappe 4a: nur anfügbare bzw. nach Genehmigung unveränderliche Tabellen
# (Trigger in milestones 0002)
MILESTONE_APPEND_ONLY_TABLES = (
    "milestones_approval",
    "milestones_approvalparticipant",
    "milestones_datechange",
    "milestones_planversion",
    "milestones_planentry",
)


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Nur in der Testdatenbank: TRUNCATE-Sperre von Protokoll und Aufgabenverlauf abschalten.

    Djangos flush (Tests mit transaction=True) leert alle Tabellen per TRUNCATE und würde
    sonst scheitern. UPDATE- und DELETE-Sperre bleiben aktiv; die TRUNCATE-Sperre selbst wird
    in test_projekte_services.py gezielt wieder eingeschaltet und geprüft.
    """
    with django_db_blocker.unblock(), connection.cursor() as cursor:
        cursor.execute("ALTER TABLE audit_auditlog DISABLE TRIGGER audit_auditlog_no_truncate")
        cursor.execute("ALTER TABLE tasks_taskevent DISABLE TRIGGER tasks_taskevent_no_truncate")
        for table in MILESTONE_APPEND_ONLY_TABLES:
            cursor.execute(f"ALTER TABLE {table} DISABLE TRIGGER {table}_no_truncate")


@pytest.fixture
def standardkatalog(db):
    """Standardkatalog sicherstellen: flush (transaction=True) leert auch Migrationsdaten."""
    from apps.milestones.catalog import ensure_standard_catalog

    ensure_standard_catalog()


@pytest.fixture
def make_user(standardkatalog):
    counter = {"n": 0}

    def _make(email=None, password=None, **extra):
        counter["n"] += 1
        email = email or f"person{counter['n']}@test.invalid"
        extra.setdefault("display_name", f"Person {counter['n']}")
        return get_user_model().objects.create_user(email=email, password=password, **extra)

    return _make


@pytest.fixture
def welt(make_user):
    """Zwei Projekte mit getrennten Mitgliedern.

    Projekt A: pl (Projektleiter), ma (Mitarbeiter), mgmt (Management)
    Projekt B: pl_b (Projektleiter), ma_b (Mitarbeiter)
    admin: fachlicher Administrator ohne Mitgliedschaft
    creator: darf Projekte anlegen, aber ohne Mitgliedschaft
    nobody: Konto ohne Befugnis und ohne Mitgliedschaft
    """
    u = {
        "admin": make_user("admin@test.invalid", is_admin=True, display_name="Admin"),
        "pl": make_user("pl@test.invalid", can_create_projects=True, display_name="Pia Leiterin"),
        "ma": make_user("ma@test.invalid", display_name="Mats Arbeiter"),
        "mgmt": make_user("mgmt@test.invalid", display_name="Mona Management"),
        "pl_b": make_user("plb@test.invalid", can_create_projects=True, display_name="Paul B"),
        "ma_b": make_user("mab@test.invalid", display_name="Mia B"),
        "creator": make_user("creator@test.invalid", can_create_projects=True),
        "nobody": make_user("nobody@test.invalid"),
    }
    a = services.create_project(
        actor=u["pl"],
        name="Projekt A",
        description="Geheime Beschreibung A",
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 12, 31),
    )
    b = services.create_project(
        actor=u["pl_b"],
        name="Projekt B",
        description="Geheime Beschreibung B",
        start_date=datetime.date(2026, 2, 1),
        end_date=datetime.date(2026, 11, 30),
    )
    m = {
        "ma": services.add_member(
            actor=u["pl"], project=a, user=u["ma"], roles=[ProjectRole.MITARBEITER]
        ),
        "mgmt": services.add_member(
            actor=u["pl"], project=a, user=u["mgmt"], roles=[ProjectRole.MANAGEMENT]
        ),
        "ma_b": services.add_member(
            actor=u["pl_b"], project=b, user=u["ma_b"], roles=[ProjectRole.MITARBEITER]
        ),
    }
    m["pl"] = a.memberships.get(user=u["pl"])
    m["pl_b"] = b.memberships.get(user=u["pl_b"])
    return {"users": u, "a": a, "b": b, "memberships": m}


@pytest.fixture
def aufgaben(welt):
    """Buckets und Aufgaben auf Basis von welt.

    t_ma: Projekt A, zugewiesen an ma | t_pl: Projekt A, zugewiesen an pl
    t_b:  Projekt B, zugewiesen an ma_b
    p_ma: persönliche Aufgabe von ma | p_nobody: persönliche Aufgabe von nobody
    """
    from apps.tasks import services as task_services

    u, a, b = welt["users"], welt["a"], welt["b"]
    planung = task_services.create_bucket(actor=u["pl"], project=a, name="Planung")
    umsetzung = task_services.create_bucket(actor=u["pl"], project=a, name="Umsetzung")
    vorbereitung = task_services.create_bucket(actor=u["pl_b"], project=b, name="Vorbereitung")
    t = {
        "t_ma": task_services.create_project_task(
            actor=u["pl"],
            project=a,
            bucket=planung,
            title="Aufgabe MA",
            description="Geheime Aufgabenbeschreibung A",
            assignees=[u["ma"]],
        ),
        "t_pl": task_services.create_project_task(
            actor=u["pl"],
            project=a,
            bucket=umsetzung,
            title="Aufgabe PL",
            description="Geheime Aufgabenbeschreibung A2",
            assignees=[u["pl"]],
        ),
        "t_b": task_services.create_project_task(
            actor=u["pl_b"],
            project=b,
            bucket=vorbereitung,
            title="Aufgabe B",
            description="Geheime Aufgabenbeschreibung B",
            assignees=[u["ma_b"]],
        ),
        "p_ma": task_services.create_personal_task(
            actor=u["ma"], title="Privat MA", description="Geheime private Notiz MA"
        ),
        "p_nobody": task_services.create_personal_task(
            actor=u["nobody"], title="Privat Nobody", description="Geheime private Notiz N"
        ),
    }
    return welt | {
        "tasks": t,
        "buckets": {"planung": planung, "umsetzung": umsetzung, "vorbereitung": vorbereitung},
    }
