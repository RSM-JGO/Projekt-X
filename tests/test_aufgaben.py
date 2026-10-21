"""V07b: gemeinsame Aufgaben – Kriterien 1–5, 7, 8 sowie Datenregeln und Fälligkeit."""

import datetime
import zoneinfo

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection, transaction
from django.urls import reverse

from apps.projects import services as project_services
from apps.projects.models import ProjectRole
from apps.tasks import policies, selectors, services
from apps.tasks.forms import assignable_users
from apps.tasks.models import (
    AppendOnlyError,
    Bucket,
    Task,
    TaskAssignment,
    TaskEvent,
    TaskEventKind,
    TaskStatus,
)

BERLIN = zoneinfo.ZoneInfo("Europe/Berlin")


def _workplace_tasks(user):
    wp = selectors.my_workplace(user)
    offen = [row["task"] for g in wp["groups"] for row in g["rows"]]
    return offen, [row["task"] for row in wp["done"]]


# ---------- Kriterium 1: ein Datensatz, mehrere Zuständige ----------


@pytest.mark.django_db
def test_aufgabe_mit_zwei_zustaendigen_ist_ein_datensatz(client, aufgaben):
    u, a = aufgaben["users"], aufgaben["a"]
    task = services.create_project_task(
        actor=u["pl"],
        project=a,
        bucket=aufgaben["buckets"]["planung"],
        title="Gemeinsam",
        assignees=[u["pl"], u["ma"]],
    )
    assert Task.objects.filter(title="Gemeinsam").count() == 1
    assert TaskAssignment.objects.filter(task=task, ended_at=None).count() == 2

    for person in ("pl", "ma"):
        offen, _ = _workplace_tasks(u[person])
        assert [t.pk for t in offen].count(task.pk) == 1
        client.force_login(u[person])
        html = client.get(reverse("tasks:workplace")).content.decode()
        assert html.count(str(task.public_id)) == 1

    board = selectors.project_board(a, "offen")
    ids = [c["task"].pk for col in board["columns"] for c in col["tasks"]]
    assert ids.count(task.pk) == 1


@pytest.mark.django_db
def test_herkunft_im_arbeitsplatz_unterscheidbar(aufgaben):
    u, t = aufgaben["users"], aufgaben["tasks"]
    rows = {
        row["task"].pk: row["origin"]
        for g in selectors.my_workplace(u["pl"])["groups"]
        for row in g["rows"]
    }
    assert rows[t["t_pl"].pk] == "zugewiesen"
    assert rows[t["t_ma"].pk] == "geleitet"  # nicht zugewiesen, aber in geleitetem Projekt
    personal = services.create_personal_task(actor=u["pl"], title="Notiz PL")
    rows = {
        row["task"].pk: row["origin"]
        for g in selectors.my_workplace(u["pl"])["groups"]
        for row in g["rows"]
    }
    assert rows[personal.pk] == "persoenlich"
    assert t["t_b"].pk not in rows and t["p_ma"].pk not in rows


@pytest.mark.django_db
def test_arbeitsplatz_ohne_beendete_mitgliedschaft(aufgaben):
    u, a, m = aufgaben["users"], aufgaben["a"], aufgaben["memberships"]
    project_services.remove_member(actor=u["pl"], project=a, membership=m["ma"])
    offen, _ = _workplace_tasks(u["ma"])
    assert aufgaben["tasks"]["t_ma"].pk not in [t.pk for t in offen]


# ---------- Kriterium 2: Zuweisung nur an aktive PL/MA ----------


@pytest.mark.django_db
def test_management_allein_ist_nicht_zuweisbar(aufgaben):
    u, a = aufgaben["users"], aufgaben["a"]
    assert not policies.is_assignable(u["mgmt"], a)
    assert u["mgmt"] not in assignable_users(a)
    assert set(assignable_users(a)) == {u["pl"], u["ma"]}
    with pytest.raises(ValidationError):
        services.create_project_task(
            actor=u["pl"],
            project=a,
            bucket=aufgaben["buckets"]["planung"],
            title="X",
            assignees=[u["mgmt"]],
        )
    task = aufgaben["tasks"]["t_ma"]
    with pytest.raises(ValidationError):
        services.update_task(
            actor=u["pl"], task=task, expected_version=task.version, assignees=[u["mgmt"]]
        )
    assert not TaskAssignment.objects.filter(user=u["mgmt"]).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("person", ["ma_b", "nobody", "admin"])
def test_nichtmitglieder_sind_nicht_zuweisbar(aufgaben, person):
    u, a = aufgaben["users"], aufgaben["a"]
    with pytest.raises(ValidationError):
        services.create_project_task(
            actor=u["pl"],
            project=a,
            bucket=aufgaben["buckets"]["planung"],
            title="X",
            assignees=[u[person]],
        )


@pytest.mark.django_db
def test_management_mit_zusaetzlicher_mitarbeiterrolle_ist_zuweisbar(aufgaben):
    u, a, m = aufgaben["users"], aufgaben["a"], aufgaben["memberships"]
    project_services.change_roles(
        actor=u["pl"],
        project=a,
        membership=m["mgmt"],
        roles=[ProjectRole.MANAGEMENT, ProjectRole.MITARBEITER],
    )
    assert policies.is_assignable(u["mgmt"], a)


@pytest.mark.django_db
def test_deaktiviertes_konto_ist_nicht_zuweisbar(aufgaben):
    u, a = aufgaben["users"], aufgaben["a"]
    u["ma"].is_active = False
    u["ma"].save()
    assert u["ma"] not in assignable_users(a)
    assert not policies.is_assignable(u["ma"], a)


# ---------- Kriterium 3: Abschluss gilt für alle ----------


@pytest.mark.django_db
def test_abschluss_durch_eine_zugewiesene_person_gilt_fuer_alle(client, aufgaben):
    u, a = aufgaben["users"], aufgaben["a"]
    task = services.create_project_task(
        actor=u["pl"],
        project=a,
        bucket=aufgaben["buckets"]["planung"],
        title="Gemeinsam",
        assignees=[u["pl"], u["ma"]],
    )
    client.force_login(u["ma"])
    assert client.post(reverse("tasks:complete", args=[task.public_id])).status_code == 302
    task.refresh_from_db()
    assert task.status == TaskStatus.ERLEDIGT
    assert task.completed_by == u["ma"] and task.completed_at is not None

    _, erledigt_pl = _workplace_tasks(u["pl"])
    assert task.pk in [t.pk for t in erledigt_pl]
    client.force_login(u["pl"])
    html = client.get(reverse("tasks:detail", args=[task.public_id])).content.decode()
    assert "Abgeschlossen von Mats Arbeiter" in html
    assert "von Mats Arbeiter am" in html


@pytest.mark.django_db
def test_doppelter_abschluss_wird_abgelehnt(aufgaben):
    u, task = aufgaben["users"], aufgaben["tasks"]["t_ma"]
    services.complete_task(actor=u["ma"], task=task)
    with pytest.raises(ValidationError):
        services.complete_task(actor=u["pl"], task=task)
    assert TaskEvent.objects.filter(task=task, kind=TaskEventKind.COMPLETED).count() == 1


# ---------- Kriterium 4: Filter ----------


@pytest.mark.django_db
def test_erledigte_aufgaben_ueber_filter_sichtbar(client, aufgaben):
    u, a, t = aufgaben["users"], aufgaben["a"], aufgaben["tasks"]
    services.complete_task(actor=u["ma"], task=t["t_ma"])

    def ids(filter_key):
        board = selectors.project_board(a, filter_key)
        return {c["task"].pk for col in board["columns"] for c in col["tasks"]}, {
            f["key"]: f["count"] for f in board["filters"]
        }

    offen, zaehler = ids("offen")
    assert t["t_ma"].pk not in offen and t["t_pl"].pk in offen
    assert zaehler == {"offen": 1, "erledigt": 1, "alle": 2}
    assert ids("erledigt")[0] == {t["t_ma"].pk}
    assert ids("alle")[0] == {t["t_ma"].pk, t["t_pl"].pk}

    client.force_login(u["mgmt"])
    url = reverse("projects:detail", args=[a.public_id])
    assert "Aufgabe MA" not in client.get(url).content.decode()
    assert "Aufgabe MA" in client.get(url + "?filter=erledigt").content.decode()
    assert "Aufgabe MA" in client.get(url + "?filter=alle").content.decode()
    assert "Aufgabe MA" not in client.get(url + "?filter=unsinn").content.decode()


# ---------- Kriterium 5: Wiederöffnen ----------


@pytest.mark.django_db
def test_projektleiter_oeffnet_wieder_und_abschluss_bleibt_im_verlauf(client, aufgaben):
    u, task = aufgaben["users"], aufgaben["tasks"]["t_ma"]
    services.complete_task(actor=u["ma"], task=task)
    with pytest.raises(PermissionDenied):
        services.reopen_task(actor=u["ma"], task=task)
    client.force_login(u["pl"])
    assert client.post(reverse("tasks:reopen", args=[task.public_id])).status_code == 302
    task.refresh_from_db()
    assert task.status == TaskStatus.OFFEN and task.completed_at is None

    kinds = list(TaskEvent.objects.filter(task=task).values_list("kind", flat=True))
    assert kinds[-2:] == [TaskEventKind.COMPLETED, TaskEventKind.REOPENED]
    reopened = TaskEvent.objects.get(task=task, kind=TaskEventKind.REOPENED)
    assert reopened.old_values["completed_by"] == "Mats Arbeiter"
    assert reopened.old_values["completed_by_id"] == u["ma"].pk
    html = client.get(reverse("tasks:detail", args=[task.public_id])).content.decode()
    assert "Abgeschlossen von Mats Arbeiter" in html
    assert "Wiedergeöffnet von Pia Leiterin" in html


# ---------- Kriterium 7: persönliche Aufgaben ----------


@pytest.mark.django_db
def test_persoenliche_aufgabe_nur_eigentuemer_und_admin(aufgaben):
    u, p = aufgaben["users"], aufgaben["tasks"]["p_ma"]
    for person in ("pl", "mgmt", "nobody", "ma_b"):
        with pytest.raises(PermissionDenied):
            services.update_task(actor=u[person], task=p, expected_version=p.version, title="X")
        with pytest.raises(PermissionDenied):
            services.complete_task(actor=u[person], task=p)
    offen, _ = _workplace_tasks(u["pl"])
    assert p.pk not in [t.pk for t in offen]
    assert policies.can_view_task(u["admin"], p)


@pytest.mark.django_db
def test_persoenliche_aufgabe_ohne_zuweisung(aufgaben):
    u, p = aufgaben["users"], aufgaben["tasks"]["p_ma"]
    with pytest.raises(ValidationError):
        services.update_task(actor=u["ma"], task=p, expected_version=p.version, assignees=[u["pl"]])
    assert not TaskAssignment.objects.filter(task=p).exists()


# ---------- Kriterium 8: Administratoraktionen ----------


@pytest.mark.django_db
@pytest.mark.parametrize("objekt", ["t_b", "p_nobody"])
def test_admin_aenderung_mit_alt_neu_und_kennzeichnung(client, aufgaben, objekt):
    u, task = aufgaben["users"], aufgaben["tasks"][objekt]
    services.update_task(
        actor=u["admin"],
        task=task,
        expected_version=task.version,
        title="Korrigiert",
        due_date=datetime.date(2026, 11, 30),
    )
    ereignis = TaskEvent.objects.filter(task=task, kind=TaskEventKind.UPDATED).get()
    assert ereignis.actor == u["admin"] and ereignis.as_admin
    assert ereignis.old_values == {"title": task.title, "due_date": None}
    assert ereignis.new_values == {"title": "Korrigiert", "due_date": "2026-11-30"}
    client.force_login(u["admin"])
    html = client.get(reverse("tasks:detail", args=[task.public_id])).content.decode()
    assert "Administratoraktion" in html
    assert "30.11.2026" in html and "als Administrator" in html


@pytest.mark.django_db
def test_admin_als_projektleiter_ist_keine_admin_aktion(aufgaben):
    u, a, task = aufgaben["users"], aufgaben["a"], aufgaben["tasks"]["t_ma"]
    project_services.add_member(
        actor=u["pl"], project=a, user=u["admin"], roles=[ProjectRole.PROJEKTLEITER]
    )
    services.complete_task(actor=u["admin"], task=task)
    assert not TaskEvent.objects.get(task=task, kind=TaskEventKind.COMPLETED).as_admin


# ---------- Versionszähler ----------


@pytest.mark.django_db
def test_veralteter_stand_wird_nicht_still_ueberschrieben(client, aufgaben):
    u, task = aufgaben["users"], aufgaben["tasks"]["t_ma"]
    alte_version = task.version
    services.update_task(actor=u["pl"], task=task, expected_version=alte_version, title="Neu PL")
    with pytest.raises(services.TaskConflictError):
        services.update_task(actor=u["ma"], task=task, expected_version=alte_version, title="MA")
    client.force_login(u["ma"])
    response = client.post(
        reverse("tasks:edit", args=[task.public_id]),
        {
            "title": "MA über Formular",
            "bucket": task.bucket_id,
            "assignees": [u["ma"].pk],
            "version": alte_version,
        },
    )
    assert response.status_code == 200
    assert "inzwischen von einer anderen Person geändert" in response.content.decode()
    task.refresh_from_db()
    assert task.title == "Neu PL"


@pytest.mark.django_db
def test_version_steigt_bei_jeder_aenderung(aufgaben):
    u, task = aufgaben["users"], aufgaben["tasks"]["t_ma"]
    v = task.version
    task = services.update_task(actor=u["pl"], task=task, expected_version=v, title="A")
    task = services.complete_task(actor=u["ma"], task=task)
    task = services.reopen_task(actor=u["pl"], task=task)
    assert task.version == v + 3
    unveraendert = services.update_task(
        actor=u["pl"], task=task, expected_version=task.version, title="A"
    )
    assert unveraendert.version == v + 3


# ---------- Datenbankregeln ----------


@pytest.mark.django_db
def test_constraints_projekt_bucket_eigentuemer(aufgaben):
    u, a = aufgaben["users"], aufgaben["a"]
    planung, fremd = aufgaben["buckets"]["planung"], aufgaben["buckets"]["vorbereitung"]
    falsch = [
        dict(project=a, bucket=None, owner=None),  # Projektaufgabe ohne Bucket
        dict(project=None, bucket=None, owner=None),  # persönlich ohne Eigentümer
        dict(project=None, bucket=planung, owner=u["ma"]),  # persönlich mit Bucket
        dict(project=a, bucket=planung, owner=u["ma"]),  # Projektaufgabe mit Eigentümer
        dict(project=a, bucket=fremd, owner=None),  # Bucket aus anderem Projekt
    ]
    for felder in falsch:
        with pytest.raises(IntegrityError), transaction.atomic():
            Task.objects.bulk_create([Task(title="X", created_by=u["pl"], **felder)])


@pytest.mark.django_db
def test_constraint_erledigt_genau_mit_abschlussdaten(aufgaben):
    task = aufgaben["tasks"]["t_ma"]
    with pytest.raises(IntegrityError), transaction.atomic():
        Task.objects.filter(pk=task.pk).update(status=TaskStatus.ERLEDIGT)
    with pytest.raises(IntegrityError), transaction.atomic():
        Task.objects.filter(pk=task.pk).update(completed_by=aufgaben["users"]["pl"])


@pytest.mark.django_db
def test_hoechstens_eine_aktive_zuweisung(aufgaben):
    u, task = aufgaben["users"], aufgaben["tasks"]["t_ma"]
    with pytest.raises(IntegrityError), transaction.atomic():
        TaskAssignment.objects.create(task=task, user=u["ma"], assigned_by=u["pl"])


@pytest.mark.django_db
def test_bucketname_je_projekt_eindeutig(aufgaben):
    u, a, b = aufgaben["users"], aufgaben["a"], aufgaben["b"]
    with pytest.raises(ValidationError):
        services.create_bucket(actor=u["pl"], project=a, name="PLANUNG")
    with pytest.raises(IntegrityError), transaction.atomic():
        Bucket.objects.create(project=a, name="planung")
    services.create_bucket(actor=u["pl_b"], project=b, name="Planung")  # anderes Projekt ok
    Bucket.objects.filter(pk=aufgaben["buckets"]["planung"].pk).update(is_archived=True)
    services.create_bucket(actor=u["pl"], project=a, name="Planung")  # archivierter zählt nicht


@pytest.mark.django_db
def test_buckets_umbenennen_und_sortieren(client, aufgaben):
    u, a = aufgaben["users"], aufgaben["a"]
    planung, umsetzung = aufgaben["buckets"]["planung"], aufgaben["buckets"]["umsetzung"]
    client.force_login(u["pl"])
    url = reverse("tasks:bucket_update", args=[a.public_id, umsetzung.pk])
    client.post(url, {"move": "up"})
    assert list(selectors.active_buckets(a)) == [umsetzung, planung]
    client.post(url, {"name": "Bau"})
    umsetzung.refresh_from_db()
    assert umsetzung.name == "Bau"
    with pytest.raises(PermissionDenied):
        services.rename_bucket(actor=u["ma"], bucket=planung, name="X")


@pytest.mark.django_db
def test_verlauf_ist_nur_anfuegbar(aufgaben):
    ereignis = TaskEvent.objects.first()
    with pytest.raises(AppendOnlyError):
        ereignis.save()
    with pytest.raises(AppendOnlyError):
        TaskEvent.objects.all().delete()
    for sql in ("UPDATE tasks_taskevent SET kind = 'X'", "DELETE FROM tasks_taskevent"):
        with pytest.raises(Exception, match="nur anfuegbar"), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(sql)
    with pytest.raises(Exception, match="TRUNCATE"), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute("ALTER TABLE tasks_taskevent ENABLE TRIGGER tasks_taskevent_no_truncate")
            cursor.execute("TRUNCATE tasks_taskevent CASCADE")


# ---------- Überfällig (Europe/Berlin) ----------


def _task(status=TaskStatus.OFFEN, due=None):
    return Task(status=status, due_date=due)


def test_heute_nach_berliner_zeit():
    # 21.10.2026 22:30 UTC ist in Berlin bereits der 22.10.2026 (00:30 MESZ)
    now = datetime.datetime(2026, 10, 21, 22, 30, tzinfo=datetime.UTC)
    assert selectors.today(now) == datetime.date(2026, 10, 22)
    assert now.astimezone(BERLIN).date() == datetime.date(2026, 10, 22)


def test_ueberfaellig_nur_offen_und_vor_heute():
    heute = datetime.date(2026, 10, 22)
    gestern = datetime.date(2026, 10, 21)
    assert selectors.is_overdue(_task(due=gestern), heute)
    assert not selectors.is_overdue(_task(due=heute), heute)
    assert not selectors.is_overdue(_task(due=None), heute)
    assert not selectors.is_overdue(_task(status=TaskStatus.ERLEDIGT, due=gestern), heute)
    assert selectors.due_group(_task(due=gestern), heute) == "ueberfaellig"
    assert selectors.due_group(_task(due=heute), heute) == "heute"
    assert selectors.due_group(_task(due=datetime.date(2026, 10, 30)), heute) == "demnaechst"
    assert selectors.due_group(_task(), heute) == "ohne"
    assert selectors.due_tone(_task(due=gestern), heute) == "rose"
    assert selectors.due_tone(_task(due=heute), heute) == "peach"
    assert selectors.due_tone(_task(status=TaskStatus.ERLEDIGT, due=gestern), heute) == "mint"


@pytest.mark.django_db
def test_arbeitsplatz_gruppiert_nach_faelligkeit(aufgaben):
    u, a = aufgaben["users"], aufgaben["a"]
    heute = selectors.today()
    bucket = aufgaben["buckets"]["planung"]
    erstellt = {}
    for key, due in {
        "ueberfaellig": heute - datetime.timedelta(days=1),
        "heute": heute,
        "demnaechst": heute + datetime.timedelta(days=3),
    }.items():
        erstellt[key] = services.create_project_task(
            actor=u["pl"], project=a, bucket=bucket, title=key, due_date=due, assignees=[u["ma"]]
        )
    gruppen = {
        g["key"]: [row["task"].pk for row in g["rows"]]
        for g in selectors.my_workplace(u["ma"])["groups"]
    }
    for key, task in erstellt.items():
        assert task.pk in gruppen[key]
    assert aufgaben["tasks"]["t_ma"].pk in gruppen["ohne"]


# ---------- Zuständige ändern nur Projektleiter und Administrator ----------


@pytest.mark.django_db
def test_mitarbeiter_darf_zustaendige_nicht_aendern(aufgaben):
    u, task = aufgaben["users"], aufgaben["tasks"]["t_ma"]
    for neue in ([u["ma"], u["pl"]], []):
        with pytest.raises(PermissionDenied):
            services.update_task(
                actor=u["ma"], task=task, expected_version=task.version, assignees=neue
            )
    assert set(
        TaskAssignment.objects.filter(task=task, ended_at=None).values_list("user", flat=True)
    ) == {u["ma"].pk}
    # Gleiche Liste und Feldänderungen sind erlaubt
    services.update_task(
        actor=u["ma"],
        task=task,
        expected_version=task.version,
        assignees=[u["ma"]],
        title="MA ändert Titel",
        bucket=aufgaben["buckets"]["umsetzung"],
    )


@pytest.mark.django_db
@pytest.mark.parametrize("person", ["pl", "admin"])
def test_projektleiter_und_admin_aendern_zustaendige(aufgaben, person):
    u, task = aufgaben["users"], aufgaben["tasks"]["t_ma"]
    services.update_task(
        actor=u[person], task=task, expected_version=task.version, assignees=[u["pl"], u["ma"]]
    )
    assert TaskAssignment.objects.filter(task=task, ended_at=None).count() == 2


@pytest.mark.django_db
def test_mitarbeiter_legt_nur_fuer_sich_selbst_an(client, aufgaben):
    u, a, bucket = aufgaben["users"], aufgaben["a"], aufgaben["buckets"]["planung"]
    for zustaendig in ([u["pl"]], [u["ma"], u["pl"]], []):
        with pytest.raises(PermissionDenied):
            services.create_project_task(
                actor=u["ma"], project=a, bucket=bucket, title="X", assignees=zustaendig
            )
    client.force_login(u["ma"])
    url = reverse("tasks:create", args=[a.public_id])
    html = client.get(url).content.decode()
    assert 'name="assignees"' not in html and "Zuständige ändern nur Projektleiter" in html
    # Auch ein manipuliertes Formular weist niemand anderen zu
    client.post(url, {"title": "MA-Aufgabe", "bucket": bucket.pk, "assignees": [u["pl"].pk]})
    task = Task.objects.get(title="MA-Aufgabe")
    assert list(task.assignments.values_list("user", flat=True)) == [u["ma"].pk]


@pytest.mark.django_db
def test_bearbeiten_formular_zeigt_zustaendige_nur_fuer_projektleiter(client, aufgaben):
    u, task = aufgaben["users"], aufgaben["tasks"]["t_ma"]
    url = reverse("tasks:edit", args=[task.public_id])
    client.force_login(u["ma"])
    html = client.get(url).content.decode()
    assert 'name="assignees"' not in html and "Mats Arbeiter" in html
    client.post(
        url,
        {
            "title": "Neu",
            "bucket": task.bucket_id,
            "version": task.version,
            "assignees": [u["pl"].pk],
        },
    )
    task.refresh_from_db()
    assert task.title == "Neu"
    assert list(task.assignments.filter(ended_at=None).values_list("user", flat=True)) == [
        u["ma"].pk
    ]
    client.force_login(u["pl"])
    assert 'name="assignees"' in client.get(url).content.decode()
