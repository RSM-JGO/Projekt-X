"""Etappe 4a: Meilensteine, Lieferobjekte, Freigaben und abgeleiteter Status.

Abnahmekriterien (docs/auftrag-etappe-4a.md): 1, 2, 3 (Service), 4, 5, 6 (Service), 9, 10 sowie
Projektgrenzen in der Datenbank und die Datenmigration bestehender Projekte.
"""

import datetime
import importlib

import pytest
from django.apps import apps as django_apps
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection, transaction
from django.urls import reverse

from apps.audit.models import AuditLog
from apps.milestones import selectors, services
from apps.milestones.catalog import STANDARD_CATALOG_V1
from apps.milestones.models import (
    AppendOnlyError,
    Approval,
    ApprovalLight,
    Deliverable,
    DeliverableStatus,
    DeliverableTemplate,
    Milestone,
    MilestoneTemplate,
    PlanEntry,
    PlanStatus,
    PlanVersion,
)
from apps.projects import services as project_services
from apps.projects.models import ProjectRole

CODES = ["M0", "M1", "M2", "M3", "M4", "M5"]


def ms(project, code):
    return Milestone.objects.get(project=project, code=code)


def deliv(project, code, prefix):
    return Deliverable.objects.get(
        milestone__project=project, milestone__code=code, title__startswith=prefix
    )


def alles_vorhanden(project, code):
    Deliverable.objects.filter(milestone=ms(project, code)).update(
        status=DeliverableStatus.VORHANDEN
    )


def freigabe(welt, code, light=ApprovalLight.GRUEN, actor="pl", project="a", **extra):
    project = welt[project]
    milestone = ms(project, code)
    missing = services.missing_required(milestone)
    extra.setdefault("conditions", "Auflage" if light == ApprovalLight.ORANGE else "")
    return services.grant_approval(
        actor=welt["users"][actor],
        project=project,
        milestone=milestone,
        light=light,
        decision="Entscheidung",
        decided_on=extra.pop("decided_on", services.today()),
        confirmed_missing=[m["id"] for m in missing],
        **extra,
    )


def termin(welt, code, tage=10, project="a"):
    """Gibt dem Meilenstein eine Prognose (ein Termin, damit er bewertet wird)."""
    project = welt[project]
    services.change_date(
        actor=welt["users"]["pl"],
        project=project,
        milestone=ms(project, code),
        kind="PROGNOSE",
        value=services.today() + datetime.timedelta(days=tage),
        reason="Test",
    )


# ---------- Kriterium 1: M0–M5 mit Standard-Lieferobjekten, Katalog wird kopiert ----------


@pytest.mark.django_db
def test_standardkatalog_ist_in_der_datenbank(standardkatalog):
    assert list(MilestoneTemplate.objects.values_list("code", flat=True)) == CODES
    for spec in STANDARD_CATALOG_V1:
        template = MilestoneTemplate.objects.get(code=spec["code"])
        assert template.deliverables.count() == len(spec["deliverables"])
        assert template.deliverables.filter(required=True).exists()


@pytest.mark.django_db
def test_jedes_neue_projekt_hat_m0_bis_m5_mit_standard_lieferobjekten(welt):
    for project in (welt["a"], welt["b"]):
        milestones = list(project.milestones.order_by("position"))
        assert [m.code for m in milestones] == CODES
        for m, spec in zip(milestones, STANDARD_CATALOG_V1, strict=True):
            assert (m.phase_name, m.title, m.goal) == (
                spec["phase_name"],
                spec["title"],
                spec["goal"],
            )
            assert [(d.title, d.required, d.area) for d in m.deliverables.order_by("position")] == [
                tuple(d) for d in spec["deliverables"]
            ]
            assert set(m.deliverables.values_list("status", flat=True)) == {DeliverableStatus.FEHLT}
            assert not m.is_hidden
        version = PlanVersion.objects.get(project=project)
        assert (version.number, version.status) == (1, PlanStatus.ENTWURF)
        period = version.entries.get(kind="ZEITRAUM")
        assert (period.start_date, period.end_date) == (project.start_date, project.end_date)


@pytest.mark.django_db
def test_katalogaenderung_veraendert_bestehende_projekte_nicht(welt):
    a = welt["a"]
    vorher = list(Deliverable.objects.filter(project=a).values_list("title", "required", "area"))
    template = MilestoneTemplate.objects.get(code="M0")
    template.title = "Neuer Standardtitel"
    template.save()
    first = template.deliverables.order_by("position").first()
    first.title = "Geänderter Standard"
    first.required = False
    first.save()
    DeliverableTemplate.objects.create(
        milestone_template=template, title="Zusätzliches Dokument", area="steckbrief", position=99
    )

    assert (
        list(Deliverable.objects.filter(project=a).values_list("title", "required", "area"))
        == vorher
    )
    assert ms(a, "M0").title == "Start Projektauftrag"

    neu = project_services.create_project(
        actor=welt["users"]["pl"],
        name="Neu",
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 6, 30),
    )
    titles = set(
        Deliverable.objects.filter(milestone__project=neu, milestone__code="M0").values_list(
            "title", flat=True
        )
    )
    assert {"Geänderter Standard", "Zusätzliches Dokument"} <= titles
    assert ms(neu, "M0").title == "Neuer Standardtitel"


@pytest.mark.django_db
def test_datenmigration_legt_m0_m5_und_planentwurf_fuer_bestehende_projekte_an(welt):
    """Simuliert ein Projekt aus der Zeit vor 4a und führt die Datenmigration 0003 aus."""
    a = welt["a"]
    with connection.cursor() as cursor:
        cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
        cursor.execute(
            "ALTER TABLE milestones_milestone DISABLE TRIGGER milestones_milestone_no_delete"
        )
        cursor.execute("DELETE FROM milestones_planentry WHERE project_id = %s", [a.pk])
        cursor.execute("DELETE FROM milestones_planversion WHERE project_id = %s", [a.pk])
        cursor.execute("DELETE FROM milestones_deliverable WHERE project_id = %s", [a.pk])
        cursor.execute("DELETE FROM milestones_milestone WHERE project_id = %s", [a.pk])
        cursor.execute(
            "ALTER TABLE milestones_milestone ENABLE TRIGGER milestones_milestone_no_delete"
        )
    assert not Milestone.objects.filter(project=a).exists()
    b_vorher = Milestone.objects.filter(project=welt["b"]).count()

    migration = importlib.import_module(
        "apps.milestones.migrations.0003_standard_catalog_and_existing_projects"
    )
    migration.forwards(django_apps, None)
    migration.forwards(django_apps, None)  # mehrfach ausführbar

    assert [m.code for m in a.milestones.order_by("position")] == CODES
    assert set(Deliverable.objects.filter(project=a).values_list("status", flat=True)) == {"FEHLT"}
    version = PlanVersion.objects.get(project=a)
    assert (version.number, version.status) == (1, PlanStatus.ENTWURF)
    assert "Übernahme" in version.reason and version.created_by == a.created_by
    period = version.entries.get(kind="ZEITRAUM")
    assert (period.start_date, period.end_date) == (a.start_date, a.end_date)
    assert Milestone.objects.filter(project=welt["b"]).count() == b_vorher


# ---------- Kriterium 2: ergänzen und ausblenden, nicht löschen ----------


@pytest.mark.django_db
def test_meilenstein_ergaenzen_reiht_sich_ein(welt):
    a, pl = welt["a"], welt["users"]["pl"]
    neu = services.add_milestone(
        actor=pl,
        project=a,
        code="M2a",
        phase_name="Zwischenschritt",
        title="Zusatz",
        after=ms(a, "M2"),
    )
    assert [m.code for m in a.milestones.order_by("position")] == [
        "M0",
        "M1",
        "M2",
        "M2a",
        "M3",
        "M4",
        "M5",
    ]
    assert neu.deliverables.count() == 0
    with pytest.raises(ValidationError):
        services.add_milestone(actor=pl, project=a, code="m2a", phase_name="x", title="Doppelt")
    with pytest.raises(PermissionDenied):
        services.add_milestone(
            actor=welt["users"]["ma"], project=a, code="X", phase_name="x", title="x"
        )
    assert AuditLog.objects.filter(action="milestone.added", project=a).count() == 1


@pytest.mark.django_db
def test_ausblenden_statt_loeschen_freigaben_bleiben(client, welt):
    a, pl = welt["a"], welt["users"]["pl"]
    m1 = ms(a, "M1")
    approval = freigabe(welt, "M1", ApprovalLight.ROT)
    services.set_milestone_hidden(actor=pl, project=a, milestone=m1, hidden=True)

    journey = selectors.journey(a)
    assert "M1" not in [s["milestone"].code for s in journey["visible"]]
    assert [s["milestone"].code for s in journey["hidden"]] == ["M1"]
    assert Approval.objects.filter(pk=approval.pk).exists()

    client.force_login(pl)
    html = client.get(reverse("projects:detail", args=[a.public_id])).content.decode()
    assert reverse("milestones:detail", args=[a.public_id, m1.public_id]) not in html
    assert "Initiierung" not in html
    seite = client.get(reverse("milestones:detail", args=[a.public_id, m1.public_id]))
    assert seite.status_code == 200 and "ausgeblendet" in seite.content.decode()
    assert "keine Freigabe" in seite.content.decode()  # Freigabe weiterhin sichtbar

    services.set_milestone_hidden(actor=pl, project=a, milestone=m1, hidden=False)
    assert "M1" in [s["milestone"].code for s in selectors.journey(a)["visible"]]


@pytest.mark.django_db
def test_meilenstein_laesst_sich_nicht_loeschen(welt):
    m = services.add_milestone(
        actor=welt["users"]["pl"], project=welt["a"], code="X", phase_name="x", title="x"
    )
    with pytest.raises(AppendOnlyError):
        m.delete()
    with pytest.raises(AppendOnlyError):
        Milestone.objects.filter(pk=m.pk).delete()
    with pytest.raises(Exception, match="nie geloescht"), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM milestones_milestone WHERE id = %s", [m.pk])
    assert Milestone.objects.filter(pk=m.pk).exists()


# ---------- Kriterium 3: Status eines Lieferobjekts (Service) ----------


@pytest.mark.django_db
def test_status_setzen_projektleitung_admin_und_verantwortliche(welt):
    u, a = welt["users"], welt["a"]
    eigen = deliv(a, "M0", "Projektsteckbrief")
    fremd = deliv(a, "M0", "Stakeholderliste")
    services.update_deliverable(actor=u["pl"], project=a, deliverable=eigen, responsible=u["ma"])

    services.set_deliverable_status(actor=u["ma"], project=a, deliverable=eigen, status="IN_ARBEIT")
    with pytest.raises(PermissionDenied):
        services.set_deliverable_status(
            actor=u["ma"], project=a, deliverable=fremd, status="IN_ARBEIT"
        )
    with pytest.raises(PermissionDenied):
        services.set_deliverable_status(
            actor=u["mgmt"], project=a, deliverable=eigen, status="FEHLT"
        )
    with pytest.raises(PermissionDenied):
        services.set_deliverable_status(
            actor=u["ma_b"], project=a, deliverable=eigen, status="FEHLT"
        )
    # Verantwortliche darf sonst nichts ändern
    with pytest.raises(PermissionDenied):
        services.update_deliverable(actor=u["ma"], project=a, deliverable=eigen, title="Neu")

    services.set_deliverable_status(actor=u["pl"], project=a, deliverable=fremd, status="VORHANDEN")
    services.set_deliverable_status(
        actor=u["admin"], project=a, deliverable=eigen, status="VORHANDEN"
    )
    eintraege = AuditLog.objects.filter(action="deliverable.status_changed").order_by("id")
    assert [(e.actor_id, e.as_admin) for e in eintraege] == [
        (u["ma"].pk, False),
        (u["pl"].pk, False),
        (u["admin"].pk, True),
    ]
    assert eintraege[0].old_values == {"status": "FEHLT"} and eintraege[0].new_values == {
        "status": "IN_ARBEIT"
    }


@pytest.mark.django_db
def test_verantwortliche_ohne_schreibrolle_verliert_das_recht(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    eigen = deliv(a, "M0", "Projektsteckbrief")
    services.update_deliverable(actor=u["pl"], project=a, deliverable=eigen, responsible=u["ma"])
    project_services.change_roles(
        actor=u["pl"], project=a, membership=m["ma"], roles=[ProjectRole.MANAGEMENT]
    )
    with pytest.raises(PermissionDenied):
        services.set_deliverable_status(
            actor=u["ma"], project=a, deliverable=eigen, status="VORHANDEN"
        )


@pytest.mark.django_db
@pytest.mark.parametrize("person", ["mgmt", "nobody", "ma_b"])
def test_verantwortlich_nur_aktive_projektleiter_oder_mitarbeiter(welt, person):
    u, a = welt["users"], welt["a"]
    with pytest.raises(ValidationError):
        services.update_deliverable(
            actor=u["pl"],
            project=a,
            deliverable=deliv(a, "M0", "Projektsteckbrief"),
            responsible=u[person],
        )


# ---------- Kriterium 4: Warnung, Schnappschuss, Orange verlangt Auflagen ----------


@pytest.mark.django_db
def test_freigabe_bei_fehlenden_pflichtdokumenten_verlangt_bestaetigung(client, welt):
    u, a = welt["users"], welt["a"]
    m0 = ms(a, "M0")
    Deliverable.objects.filter(pk=deliv(a, "M0", "Projektsteckbrief").pk).update(status="VORHANDEN")
    fehlend = services.missing_required(m0)
    assert [m["title"] for m in fehlend] == ["Stakeholderliste"]

    with pytest.raises(ValidationError) as exc:
        services.grant_approval(
            actor=u["pl"],
            project=a,
            milestone=m0,
            light="GRUEN",
            decision="Ja",
            decided_on=services.today(),
        )
    assert exc.value.code == "missing_required"
    assert not Approval.objects.exists()

    approval = services.grant_approval(
        actor=u["pl"],
        project=a,
        milestone=m0,
        light="GRUEN",
        decision="Ja",
        decided_on=services.today(),
        confirmed_missing=[fehlend[0]["id"]],
    )
    assert approval.warning_confirmed
    assert [m["title"] for m in approval.missing_required] == ["Stakeholderliste"]

    # Später nachgereicht: Der Schnappschuss bleibt unverändert und sichtbar
    services.set_deliverable_status(
        actor=u["pl"], project=a, deliverable=deliv(a, "M0", "Stakeholderliste"), status="VORHANDEN"
    )
    approval.refresh_from_db()
    assert [m["title"] for m in approval.missing_required] == ["Stakeholderliste"]
    client.force_login(u["mgmt"])
    html = client.get(
        reverse("milestones:detail", args=[a.public_id, m0.public_id])
    ).content.decode()
    assert "Fehlende Pflichtdokumente zum Zeitpunkt" in html and "Stakeholderliste" in html
    assert "Warnung wurde bestätigt" in html


@pytest.mark.django_db
def test_bestaetigung_muss_zur_aktuellen_liste_passen(welt):
    u, a = welt["users"], welt["a"]
    m0 = ms(a, "M0")
    with pytest.raises(ValidationError, match="geändert"):
        services.grant_approval(
            actor=u["pl"],
            project=a,
            milestone=m0,
            light="GRUEN",
            decision="Ja",
            decided_on=services.today(),
            confirmed_missing=[deliv(a, "M0", "Projektsteckbrief").pk],
        )


@pytest.mark.django_db
def test_freigabe_ueber_oberflaeche_zeigt_warnung_und_verlangt_bestaetigung(client, welt):
    u, a = welt["users"], welt["a"]
    m0 = ms(a, "M0")
    url = reverse("milestones:approve", args=[a.public_id, m0.public_id])
    client.force_login(u["pl"])
    html = client.get(url).content.decode()
    assert "Es fehlen 2 Pflichtdokumente" in html and "Projektsteckbrief" in html
    ids = ",".join(str(m["id"]) for m in services.missing_required(m0))
    data = {
        "light": "GRUEN",
        "decision": "Ja",
        "decided_on": services.today().isoformat(),
        "missing_ids": ids,
    }
    response = client.post(url, data)
    assert response.status_code == 200 and "bestätigen" in response.content.decode()
    assert not Approval.objects.exists()
    response = client.post(url, data | {"confirm_missing": "on"})
    assert response.status_code == 302
    assert Approval.objects.get().warning_confirmed


@pytest.mark.django_db
def test_orange_verlangt_auflagen_auch_in_der_datenbank(welt):
    u, a = welt["users"], welt["a"]
    alles_vorhanden(a, "M0")
    with pytest.raises(ValidationError) as exc:
        services.grant_approval(
            actor=u["pl"],
            project=a,
            milestone=ms(a, "M0"),
            light="ORANGE",
            decision="Ja",
            decided_on=services.today(),
            conditions="  ",
        )
    assert "conditions" in exc.value.message_dict
    with pytest.raises(IntegrityError), transaction.atomic():
        Approval.objects.create(
            project=a,
            milestone=ms(a, "M0"),
            light="ORANGE",
            decision="x",
            decided_on=services.today(),
            granted_by=u["pl"],
        )


@pytest.mark.django_db
def test_rot_braucht_keine_bestaetigung_friert_aber_ein(welt):
    u, a = welt["users"], welt["a"]
    approval = services.grant_approval(
        actor=u["pl"],
        project=a,
        milestone=ms(a, "M1"),
        light="ROT",
        decision="Nein",
        decided_on=services.today(),
    )
    assert not approval.warning_confirmed
    assert len(approval.missing_required) == 4


# ---------- Kriterium 5: unveränderlich, Korrektur ersetzt ----------


@pytest.mark.django_db
def test_freigaben_sind_im_code_unveraenderlich(welt):
    approval = freigabe(welt, "M0")
    approval.decision = "geändert"
    with pytest.raises(AppendOnlyError):
        approval.save()
    with pytest.raises(AppendOnlyError):
        approval.delete()
    with pytest.raises(AppendOnlyError):
        Approval.objects.filter(pk=approval.pk).update(decision="x")
    with pytest.raises(AppendOnlyError):
        Approval.objects.all().delete()
    with pytest.raises(AppendOnlyError):
        approval.participant_links.all().delete()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("table", "sql"),
    [
        ("milestones_approval", "UPDATE milestones_approval SET decision = 'x'"),
        ("milestones_approval", "DELETE FROM milestones_approval"),
        ("milestones_approvalparticipant", "DELETE FROM milestones_approvalparticipant"),
        (
            "milestones_approvalparticipant",
            "UPDATE milestones_approvalparticipant SET display_name = 'x'",
        ),
    ],
)
def test_freigaben_sind_in_der_datenbank_unveraenderlich(welt, table, sql):
    freigabe(welt, "M0", participants=[welt["users"]["mgmt"]])
    with pytest.raises(Exception, match="nur anfuegbar"), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(sql)
    assert Approval.objects.get().decision == "Entscheidung"


@pytest.mark.django_db
def test_truncate_von_freigaben_wird_abgewiesen(welt):
    freigabe(welt, "M0")
    with pytest.raises(Exception, match="TRUNCATE"), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(
                "ALTER TABLE milestones_approval ENABLE TRIGGER milestones_approval_no_truncate"
            )
            cursor.execute("TRUNCATE milestones_approval CASCADE")
    assert Approval.objects.exists()


@pytest.mark.django_db
def test_korrektur_ist_neue_freigabe_mit_verweis(client, welt):
    u, a = welt["users"], welt["a"]
    alt = freigabe(welt, "M1", ApprovalLight.GRUEN)
    neu = freigabe(welt, "M1", ApprovalLight.ORANGE, replaces=alt, conditions="Nachreichen")
    assert neu.replaces == alt and Approval.objects.count() == 2
    alt.refresh_from_db()
    assert alt.light == ApprovalLight.GRUEN  # unverändert
    state = selectors.state_for(selectors.journey(a), ms(a, "M1"))
    assert state["approval"] == neu
    assert [(i["approval"].pk, i["replaced"]) for i in state["approvals"]] == [
        (neu.pk, False),
        (alt.pk, True),
    ]
    assert AuditLog.objects.filter(action="approval.corrected").count() == 1
    # Eine bereits ersetzte Freigabe kann nicht noch einmal korrigiert werden
    with pytest.raises(ValidationError):
        freigabe(welt, "M1", replaces=alt)
    client.force_login(u["ma"])
    html = client.get(
        reverse("milestones:detail", args=[a.public_id, ms(a, "M1").public_id])
    ).content.decode()
    assert "ersetzt durch Korrektur" in html and "Frühere Freigabeentscheidungen" in html


@pytest.mark.django_db
def test_korrektur_nur_innerhalb_desselben_meilensteins_datenbank(welt):
    u, a = welt["users"], welt["a"]
    alt = freigabe(welt, "M0")
    with pytest.raises(IntegrityError), transaction.atomic():
        Approval.objects.create(
            project=a,
            milestone=ms(a, "M1"),
            light="ROT",
            decision="x",
            decided_on=services.today(),
            granted_by=u["pl"],
            replaces=alt,
        )


@pytest.mark.django_db
def test_keine_endpunkte_zum_aendern_oder_loeschen(client, welt):
    approval = freigabe(welt, "M0")
    client.force_login(welt["users"]["admin"])
    url = reverse("milestones:approve", args=[welt["a"].public_id, ms(welt["a"], "M0").public_id])
    assert client.delete(url).status_code == 405
    assert client.put(url).status_code == 405
    assert str(approval.public_id) not in client.get(url).content.decode()


# ---------- Kriterium 6: Freigaben nur Projektleitung und Admin, Admin gekennzeichnet ----------


@pytest.mark.django_db
@pytest.mark.parametrize("person", ["ma", "mgmt", "nobody", "pl_b", "creator"])
def test_freigaben_erteilen_nur_projektleitung_und_admin(welt, person):
    with pytest.raises(PermissionDenied):
        freigabe(welt, "M0", ApprovalLight.ROT, actor=person)
    assert not Approval.objects.exists()


@pytest.mark.django_db
def test_admin_freigabe_ist_gekennzeichnet_und_protokolliert(client, welt):
    a = welt["a"]
    approval = freigabe(welt, "M0", ApprovalLight.ROT, actor="admin")
    assert approval.as_admin and approval.granted_by == welt["users"]["admin"]
    eintrag = AuditLog.objects.get(action="approval.granted")
    assert eintrag.as_admin and eintrag.new_values["light"] == "ROT"
    assert not freigabe(welt, "M1", ApprovalLight.ROT, actor="pl").as_admin
    client.force_login(welt["users"]["ma"])
    html = client.get(
        reverse("milestones:detail", args=[a.public_id, ms(a, "M0").public_id])
    ).content.decode()
    assert "als Administrator" in html


# ---------- Kriterium 9: aktueller Meilenstein ----------


def aktuell(project):
    current = selectors.journey(project)["current"]
    return current["milestone"].code if current else None


@pytest.mark.django_db
def test_aktueller_meilenstein_erster_sichtbarer_ohne_gueltige_freigabe(welt):
    a, pl = welt["a"], welt["users"]["pl"]
    assert aktuell(a) == "M0"
    freigabe(welt, "M0", ApprovalLight.GRUEN)
    assert aktuell(a) == "M1"
    rot = freigabe(welt, "M1", ApprovalLight.ROT)
    assert aktuell(a) == "M1"  # Rot zählt als offen
    freigabe(welt, "M1", ApprovalLight.ORANGE, replaces=rot)
    assert aktuell(a) == "M2"  # Orange zählt als gültig
    services.set_milestone_hidden(actor=pl, project=a, milestone=ms(a, "M2"), hidden=True)
    assert aktuell(a) == "M3"  # ausgeblendete zählen nicht


@pytest.mark.django_db
def test_abgelaufene_freigabe_zaehlt_als_offen(welt):
    a = welt["a"]
    gestern = services.today() - datetime.timedelta(days=1)
    freigabe(welt, "M0", decided_on=gestern - datetime.timedelta(days=5), valid_until=gestern)
    assert aktuell(a) == "M0"
    state = selectors.state_for(selectors.journey(a), ms(a, "M0"))
    assert state["approval_expired"] and state["approval_marker"]["label"] == "Freigabe abgelaufen"
    assert state["approval_marker"]["tone"] == "neutral"
    # Gültig bis heute ist noch gültig
    freigabe(welt, "M0", decided_on=gestern, valid_until=services.today())
    assert aktuell(a) == "M1"


@pytest.mark.django_db
def test_alle_freigegeben_kein_aktueller_meilenstein(welt):
    for code in CODES:
        freigabe(welt, code, ApprovalLight.GRUEN)
    assert aktuell(welt["a"]) is None


# ---------- Kriterium 10: nicht bewertet, nie grün ----------


@pytest.mark.django_db
def test_ohne_termin_oder_ohne_lieferobjekte_nicht_bewertet(welt):
    a, pl = welt["a"], welt["users"]["pl"]
    alles_vorhanden(a, "M0")
    state = selectors.state_for(selectors.journey(a), ms(a, "M0"))
    assert not state["has_date"]
    assert state["rating"]["label"] == "nicht bewertet" and state["rating"]["tone"] == "neutral"

    termin(welt, "M0")
    state = selectors.state_for(selectors.journey(a), ms(a, "M0"))
    assert state["rating"]["label"] == "erledigt" and state["rating"]["tone"] == "mint"

    leer = services.add_milestone(actor=pl, project=a, code="MX", phase_name="Leer", title="Leer")
    termin(welt, "MX")
    state = selectors.state_for(selectors.journey(a), leer)
    assert state["has_date"] and state["total"] == 0
    assert state["rating"]["label"] == "nicht bewertet" and state["rating"]["tone"] != "mint"


@pytest.mark.django_db
def test_abgeleiteter_status_teilweise_und_nicht_begonnen(welt):
    a = welt["a"]
    termin(welt, "M1")
    assert (
        selectors.state_for(selectors.journey(a), ms(a, "M1"))["rating"]["label"]
        == "nicht begonnen"
    )
    services.set_deliverable_status(
        actor=welt["users"]["pl"], project=a, deliverable=deliv(a, "M1", "RACI"), status="IN_ARBEIT"
    )
    state = selectors.state_for(selectors.journey(a), ms(a, "M1"))
    assert state["rating"]["label"] == "offen" and state["rating"]["icon"] == "●"
    assert (state["present"], state["total"], state["open"]) == (0, 5, 5)


@pytest.mark.django_db
def test_nicht_bewertet_in_der_oberflaeche_grau(client, welt):
    a = welt["a"]
    alles_vorhanden(a, "M0")
    client.force_login(welt["users"]["mgmt"])
    html = client.get(
        reverse("milestones:detail", args=[a.public_id, ms(a, "M0").public_id])
    ).content.decode()
    assert (
        '<span class="jstate__icon tone-neutral" aria-hidden="true">–</span>'
        '<span class="jstate__text">nicht bewertet</span>' in html
    )
    assert '<span class="jstate__text">erledigt</span>' not in html


# ---------- Projektgrenzen in der Datenbank ----------


@pytest.mark.django_db
def test_lieferobjekt_und_freigabe_nur_mit_meilenstein_desselben_projekts(welt):
    a, b, pl = welt["a"], welt["b"], welt["users"]["pl"]
    with pytest.raises(IntegrityError), transaction.atomic():
        Deliverable.objects.create(project=a, milestone=ms(b, "M0"), title="x", area="steckbrief")
    with pytest.raises(IntegrityError), transaction.atomic():
        Approval.objects.create(
            project=a,
            milestone=ms(b, "M0"),
            light="ROT",
            decision="x",
            decided_on=services.today(),
            granted_by=pl,
        )
    draft_b = PlanVersion.objects.get(project=b)
    with pytest.raises(IntegrityError), transaction.atomic():
        PlanEntry.objects.create(
            project=a,
            plan_version=draft_b,
            kind="MEILENSTEIN",
            milestone=ms(a, "M0"),
            date=services.today(),
        )
    with pytest.raises(ValidationError):
        services.add_deliverable(
            actor=pl, project=a, milestone=ms(b, "M0"), title="x", area="steckbrief"
        )
