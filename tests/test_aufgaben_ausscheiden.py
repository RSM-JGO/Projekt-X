"""V07b-Review: Zuweisungen bei Ausscheiden/Rollenwechsel, Zugriff Ausgeschiedener, Verlauf."""

import pytest
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from apps.projects import services as project_services
from apps.projects.models import ProjectRole
from apps.tasks import services
from apps.tasks.models import TaskAssignment, TaskEvent, TaskEventKind

GRUND = "wegen Ausscheiden/Rollenwechsel"


def _aktiv(task, user):
    return TaskAssignment.objects.filter(task=task, user=user, ended_at__isnull=True).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("handelnd", ["pl", "admin"])
def test_ausscheiden_beendet_zuweisungen_in_offenen_aufgaben(aufgaben, handelnd):
    u, a, m, t = aufgaben["users"], aufgaben["a"], aufgaben["memberships"], aufgaben["tasks"]
    erledigt = services.create_project_task(
        actor=u["pl"],
        project=a,
        bucket=aufgaben["buckets"]["planung"],
        title="Schon erledigt",
        assignees=[u["ma"]],
    )
    services.complete_task(actor=u["ma"], task=erledigt)
    version = t["t_ma"].version

    project_services.remove_member(actor=u[handelnd], project=a, membership=m["ma"])

    assert not _aktiv(t["t_ma"], u["ma"])
    assert _aktiv(erledigt, u["ma"])  # historische Zuständigkeit bleibt
    ereignis = TaskEvent.objects.filter(task=t["t_ma"], kind=TaskEventKind.UNASSIGNED).get()
    assert ereignis.actor == u[handelnd]
    assert ereignis.as_admin is (handelnd == "admin")
    assert ereignis.old_values == {"user_id": u["ma"].pk, "user": "Mats Arbeiter"}
    assert ereignis.new_values == {"reason": GRUND}
    t["t_ma"].refresh_from_db()
    assert t["t_ma"].version == version + 1
    assert not TaskEvent.objects.filter(task=erledigt, kind=TaskEventKind.UNASSIGNED).exists()


@pytest.mark.django_db
def test_rollenwechsel_zu_management_beendet_zuweisungen(aufgaben):
    u, a, m, t = aufgaben["users"], aufgaben["a"], aufgaben["memberships"], aufgaben["tasks"]
    project_services.change_roles(
        actor=u["pl"], project=a, membership=m["ma"], roles=[ProjectRole.MANAGEMENT]
    )
    assert not _aktiv(t["t_ma"], u["ma"])
    assert TaskEvent.objects.get(task=t["t_ma"], kind=TaskEventKind.UNASSIGNED).new_values == {
        "reason": GRUND
    }
    # Weiterhin Mitglied (Management): lesen ja, abschließen/bearbeiten nein
    with pytest.raises(PermissionDenied):
        services.complete_task(actor=u["ma"], task=t["t_ma"])


@pytest.mark.django_db
def test_rollenwechsel_mit_verbleibender_schreibrolle_behaelt_zuweisungen(aufgaben):
    u, a, m, t = aufgaben["users"], aufgaben["a"], aufgaben["memberships"], aufgaben["tasks"]
    project_services.change_roles(
        actor=u["pl"],
        project=a,
        membership=m["ma"],
        roles=[ProjectRole.MANAGEMENT, ProjectRole.PROJEKTLEITER],
    )
    assert _aktiv(t["t_ma"], u["ma"])
    assert not TaskEvent.objects.filter(kind=TaskEventKind.UNASSIGNED).exists()


@pytest.mark.django_db
def test_andere_projekte_bleiben_unberuehrt(aufgaben):
    u, b, m = aufgaben["users"], aufgaben["b"], aufgaben["memberships"]
    project_services.add_member(
        actor=u["pl_b"], project=b, user=u["ma"], roles=[ProjectRole.MITARBEITER]
    )
    task_b = services.create_project_task(
        actor=u["pl_b"],
        project=b,
        bucket=aufgaben["buckets"]["vorbereitung"],
        title="B für MA",
        assignees=[u["ma"]],
    )
    project_services.remove_member(actor=u["pl"], project=aufgaben["a"], membership=m["ma"])
    assert _aktiv(task_b, u["ma"])


@pytest.mark.django_db
def test_ausgeschiedenes_mitglied_kann_aufgabe_weder_lesen_noch_aendern(client, aufgaben):
    u, a, m, task = (
        aufgaben["users"],
        aufgaben["a"],
        aufgaben["memberships"],
        aufgaben["tasks"]["t_ma"],
    )
    project_services.remove_member(actor=u["pl"], project=a, membership=m["ma"])
    client.force_login(u["ma"])
    pid = task.public_id
    for response in (
        client.get(reverse("tasks:detail", args=[pid])),
        client.get(reverse("tasks:edit", args=[pid])),
        client.post(reverse("tasks:edit", args=[pid]), {"title": "X", "version": task.version}),
        client.post(reverse("tasks:complete", args=[pid])),
        client.post(reverse("tasks:reopen", args=[pid])),
    ):
        assert response.status_code == 403
        assert b"Geheime" not in response.content
    task.refresh_from_db()
    with pytest.raises(PermissionDenied):
        services.complete_task(actor=u["ma"], task=task)
    with pytest.raises(PermissionDenied):
        services.update_task(actor=u["ma"], task=task, expected_version=task.version, title="X")


@pytest.mark.django_db
def test_verlauf_zeigt_anzeigenamen_und_bucketnamen(client, aufgaben):
    u, a, m, task = (
        aufgaben["users"],
        aufgaben["a"],
        aufgaben["memberships"],
        aufgaben["tasks"]["t_ma"],
    )
    umsetzung = aufgaben["buckets"]["umsetzung"]
    task = services.update_task(
        actor=u["pl"], task=task, expected_version=task.version, bucket=umsetzung
    )
    ereignis = TaskEvent.objects.get(task=task, kind=TaskEventKind.UPDATED)
    assert ereignis.old_values == {
        "bucket": {"id": aufgaben["buckets"]["planung"].pk, "name": "Planung"}
    }
    assert ereignis.new_values == {"bucket": {"id": umsetzung.pk, "name": "Umsetzung"}}
    project_services.remove_member(actor=u["pl"], project=a, membership=m["ma"])

    client.force_login(u["pl"])
    html = client.get(reverse("tasks:detail", args=[task.public_id])).content.decode()
    assert "Pia Leiterin hat Mats Arbeiter zugewiesen" in html
    assert f"Zuweisung von Mats Arbeiter entfernt ({GRUND})" in html
    assert "Planung → Umsetzung" in html
    assert "@test.invalid" not in html.split('id="verlauf-title"')[1]


@pytest.mark.django_db
def test_abschliessen_sperrt_erst_projekt_dann_aufgabe(aufgaben, monkeypatch):
    """Sperrreihenfolge: Projektzeile vor Aufgabenzeile (wie Mitgliedschafts-Services)."""
    from apps.tasks import services as task_services

    reihenfolge = []
    original = task_services._lock_task

    class ProjektSpion:
        def __init__(self, manager):
            self.manager = manager

        def select_for_update(self, *args, **kwargs):
            reihenfolge.append("projekt")
            return self.manager.select_for_update(*args, **kwargs)

    monkeypatch.setattr(
        task_services.Project, "objects", ProjektSpion(task_services.Project.objects)
    )
    monkeypatch.setattr(
        task_services, "_lock_task", lambda t: reihenfolge.append("aufgabe") or original(t)
    )
    u, task = aufgaben["users"], aufgaben["tasks"]["t_ma"]
    task_services.complete_task(actor=u["ma"], task=task)
    task_services.reopen_task(actor=u["pl"], task=task)
    assert reihenfolge == ["projekt", "aufgabe", "projekt", "aufgabe"]
