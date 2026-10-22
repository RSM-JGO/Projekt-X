"""Beispieldaten: nur mit DEBUG, gekennzeichnet, idempotent."""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.audit.models import AuditLog
from apps.projects.models import Project, ProjectMembership, ProjectRoleAssignment
from apps.projects.selectors import accessible_projects

User = get_user_model()


@pytest.mark.django_db
def test_seed_demo_bricht_ohne_debug_ab(settings, monkeypatch):
    settings.DEBUG = False
    monkeypatch.setenv("DEMO_PASSWORD", "Demo-Passwort-fuer-Tests-1")
    with pytest.raises(CommandError, match="DEBUG"):
        call_command("seed_demo")
    assert not User.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("wert", [None, "", "HIER_EINTRAGEN"])
def test_seed_demo_bricht_ohne_passwort_ab(settings, monkeypatch, wert):
    settings.DEBUG = True
    if wert is None:
        monkeypatch.delenv("DEMO_PASSWORD", raising=False)
    else:
        monkeypatch.setenv("DEMO_PASSWORD", wert)
    with pytest.raises(CommandError, match="DEMO_PASSWORD"):
        call_command("seed_demo")
    assert not User.objects.exists()


@pytest.mark.django_db
def test_seed_demo_ist_idempotent_und_gekennzeichnet(settings, monkeypatch):
    settings.DEBUG = True
    monkeypatch.setenv("DEMO_PASSWORD", "Demo-Passwort-fuer-Tests-1")
    call_command("seed_demo")
    zaehlung = (
        User.objects.count(),
        Project.objects.count(),
        ProjectMembership.objects.count(),
        ProjectRoleAssignment.objects.count(),
        AuditLog.objects.count(),
    )
    call_command("seed_demo")
    call_command("seed_demo")
    assert (
        User.objects.count(),
        Project.objects.count(),
        ProjectMembership.objects.count(),
        ProjectRoleAssignment.objects.count(),
        AuditLog.objects.count(),
    ) == zaehlung
    assert zaehlung[:2] == (5, 2)

    for user in User.objects.all():
        assert user.email.endswith("@beispiel.invalid")
        assert "(Beispiel)" in user.display_name
        assert user.check_password("Demo-Passwort-fuer-Tests-1")
    for project in Project.objects.all():
        assert "(Beispiel)" in project.name

    def sichtbar(email):
        return {p.name[:18] for p in accessible_projects(User.objects.get(email=email))}

    a, b = "Beispielprojekt A ", "Beispielprojekt B "
    assert sichtbar("admin@beispiel.invalid") == {a, b}
    assert sichtbar("projektleitung@beispiel.invalid") == {a, b}
    assert sichtbar("mitarbeiter1@beispiel.invalid") == {a, b}
    assert sichtbar("mitarbeiter2@beispiel.invalid") == {a}
    assert sichtbar("management@beispiel.invalid") == {a}
    assert User.objects.get(email="admin@beispiel.invalid").is_admin
    assert User.objects.get(email="projektleitung@beispiel.invalid").can_create_projects


@pytest.mark.django_db
def test_seed_demo_aufgaben_idempotent(settings, monkeypatch):
    from apps.tasks.models import Bucket, Task, TaskAssignment, TaskEvent, TaskStatus

    settings.DEBUG = True
    monkeypatch.setenv("DEMO_PASSWORD", "Demo-Passwort-fuer-Tests-1")
    call_command("seed_demo")
    zaehlung = (
        Bucket.objects.count(),
        Task.objects.count(),
        TaskAssignment.objects.count(),
        TaskEvent.objects.count(),
    )
    call_command("seed_demo")
    assert (
        Bucket.objects.count(),
        Task.objects.count(),
        TaskAssignment.objects.count(),
        TaskEvent.objects.count(),
    ) == zaehlung

    for project in Project.objects.all():
        assert 2 <= Bucket.objects.filter(project=project).count() <= 3
        assert Task.objects.filter(project=project).count() == 6
        assert Task.objects.filter(project=project, status=TaskStatus.ERLEDIGT).exists()
    pl = User.objects.get(email="projektleitung@beispiel.invalid")
    ma1 = User.objects.get(email="mitarbeiter1@beispiel.invalid")
    gemeinsam = [
        t
        for t in Task.objects.filter(project__isnull=False)
        if set(t.assignments.filter(ended_at=None).values_list("user", flat=True))
        == {pl.pk, ma1.pk}
    ]
    assert gemeinsam
    for owner in (pl, ma1):
        persoenlich = Task.objects.filter(owner=owner)
        assert persoenlich.count() == 1
        assert "(Beispiel)" in persoenlich.get().title


@pytest.mark.django_db
def test_seed_demo_meilensteine_freigaben_und_plan(settings, monkeypatch):
    """Etappe 4a: genehmigter Plan, Lieferobjekt-Status, M0 grün, M1 orange mit Auflagen (A)."""
    from apps.milestones import selectors, services
    from apps.milestones.models import Approval, DateChange, Deliverable, PlanVersion

    settings.DEBUG = True
    monkeypatch.setenv("DEMO_PASSWORD", "Demo-Passwort-fuer-Tests-1")
    call_command("seed_demo")

    def zaehlung():
        return (
            Approval.objects.count(),
            DateChange.objects.count(),
            PlanVersion.objects.count(),
            list(Deliverable.objects.order_by("id").values_list("status", "responsible_id")),
        )

    vorher = zaehlung()
    call_command("seed_demo")
    assert zaehlung() == vorher

    a = Project.objects.get(name__startswith="Beispielprojekt A")
    b = Project.objects.get(name__startswith="Beispielprojekt B")
    for project in (a, b):
        approved = services.approved_version(project)
        assert approved is not None and approved.entries.filter(kind="MEILENSTEIN").count() == 6
        period = approved.entries.get(kind="ZEITRAUM")
        assert (project.start_date, project.end_date) == (period.start_date, period.end_date)
        assert Deliverable.objects.filter(project=project).exclude(status="FEHLT").exists()

    m0, m1 = (Approval.objects.get(milestone__project=a, milestone__code=c) for c in ("M0", "M1"))
    assert m0.light == "GRUEN" and m0.missing_required == []
    assert m1.light == "ORANGE" and m1.conditions and m1.warning_confirmed
    assert [m["title"] for m in m1.missing_required] == ["RACI-Matrix"]
    assert not Approval.objects.filter(project=b).exists()
    assert selectors.journey(a)["current"]["milestone"].code == "M2"
    assert DateChange.objects.filter(project=a, kind="PROGNOSE").exists()
