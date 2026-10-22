"""Etappe 4a: Planversionen, ursprünglicher/genehmigter Plan, Prognose/Ist, Projektzeitraum.

Abnahmekriterien 7, 8 und 11 (docs/auftrag-etappe-4a.md).
"""

import datetime

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection, transaction
from django.urls import reverse

from apps.audit.models import AuditLog
from apps.milestones import selectors, services
from apps.milestones.models import (
    AppendOnlyError,
    DateChange,
    Milestone,
    PlanEntry,
    PlanStatus,
    PlanVersion,
)
from apps.projects import services as project_services

D = datetime.date


def ms(project, code):
    return Milestone.objects.get(project=project, code=code)


START, ENDE = D(2026, 1, 1), D(2026, 12, 31)


def plan(welt, termine, start=START, ende=ENDE, actor="pl", reason="Anlass"):
    """Bearbeitet den Entwurf (legt ihn bei Bedarf an) und genehmigt ihn."""
    a, user = welt["a"], welt["users"][actor]
    draft = services.draft_version(a) or services.create_plan_draft(
        actor=user, project=a, reason=reason
    )
    services.update_plan_draft(
        actor=user,
        project=a,
        version=draft,
        start_date=start,
        end_date=ende,
        milestone_dates=[(ms(a, code), day) for code, day in termine.items()],
    )
    return services.approve_plan_version(actor=user, project=a, version=draft)


def period_in_sync(project):
    """Invariante (Kriterium 11): Projektzeitraum = Zeitraum des genehmigten Plans."""
    project.refresh_from_db()
    approved = services.approved_version(project)
    if approved is None:
        return True
    entry = approved.entries.get(kind="ZEITRAUM")
    return (project.start_date, project.end_date) == (entry.start_date, entry.end_date)


# ---------- Kriterium 7: ursprünglicher und genehmigter Plan ----------


@pytest.mark.django_db
def test_urspruenglicher_plan_bleibt_genehmigter_plan_ist_der_neueste(welt):
    a = welt["a"]
    v1 = plan(welt, {"M0": D(2026, 2, 1), "M1": D(2026, 3, 1)})
    plans = selectors.plan_overview(a)
    assert plans["original"][ms(a, "M1").pk] == (D(2026, 3, 1), 1)
    assert plans["approved"][ms(a, "M1").pk] == D(2026, 3, 1)

    v2 = plan(
        welt, {"M0": D(2026, 2, 1), "M1": D(2026, 4, 1), "M2": D(2026, 6, 1)}, reason="Verschiebung"
    )
    v3 = plan(
        welt, {"M0": D(2026, 2, 1), "M1": D(2026, 5, 1), "M2": D(2026, 6, 1)}, reason="Erneut"
    )
    plans = selectors.plan_overview(a)
    assert plans["original"][ms(a, "M1").pk] == (D(2026, 3, 1), 1)  # unverändert
    assert plans["original"][ms(a, "M2").pk] == (D(2026, 6, 1), 2)  # erst ab Version 2 enthalten
    assert plans["approved"][ms(a, "M1").pk] == D(2026, 5, 1)
    assert plans["approved_version"] == v3
    statuses = dict(PlanVersion.objects.filter(project=a).values_list("number", "status"))
    assert statuses == {1: "ABGELOEST", 2: "ABGELOEST", 3: "GENEHMIGT"}
    assert v1.number == 1 and v2.number == 2

    state = selectors.state_for(selectors.journey(a), ms(a, "M1"))
    assert (state["original_date"], state["planned_date"]) == (D(2026, 3, 1), D(2026, 5, 1))


@pytest.mark.django_db
def test_neuer_entwurf_uebernimmt_genehmigten_plan_und_nur_ein_entwurf(welt):
    a, pl = welt["a"], welt["users"]["pl"]
    plan(welt, {"M0": D(2026, 2, 1)})
    draft = services.create_plan_draft(actor=pl, project=a, reason="Neu")
    assert draft.number == 2 and draft.status == PlanStatus.ENTWURF
    assert draft.entries.get(milestone=ms(a, "M0")).date == D(2026, 2, 1)
    with pytest.raises(ValidationError):
        services.create_plan_draft(actor=pl, project=a, reason="Noch einer")
    with pytest.raises(ValidationError):
        services.create_plan_draft(actor=pl, project=a, reason="")


@pytest.mark.django_db
def test_genehmigte_version_im_service_unveraenderlich(welt):
    a, pl = welt["a"], welt["users"]["pl"]
    v1 = plan(welt, {"M0": D(2026, 2, 1)})
    with pytest.raises(ValidationError):
        services.update_plan_draft(
            actor=pl,
            project=a,
            version=v1,
            start_date=D(2026, 1, 1),
            end_date=D(2026, 12, 31),
            milestone_dates=[],
        )
    with pytest.raises(ValidationError):
        services.approve_plan_version(actor=pl, project=a, version=v1)
    v1.reason = "geändert"
    with pytest.raises(AppendOnlyError):
        v1.save()
    with pytest.raises(AppendOnlyError):
        v1.delete()
    entry = v1.entries.get(milestone=ms(a, "M0"))
    entry.date = D(2026, 3, 1)
    with pytest.raises(AppendOnlyError):
        entry.save()
    with pytest.raises(AppendOnlyError):
        entry.delete()
    with pytest.raises(AppendOnlyError):
        PlanEntry(
            project=a,
            plan_version=v1,
            kind="MEILENSTEIN",
            milestone=ms(a, "M1"),
            date=D(2026, 4, 1),
        ).save()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "sql",
    [
        "UPDATE milestones_planversion SET reason = 'x' WHERE status = 'GENEHMIGT'",
        "UPDATE milestones_planversion SET status = 'ENTWURF', approved_by_id = NULL, "
        "approved_at = NULL WHERE status = 'GENEHMIGT'",
        "UPDATE milestones_planversion SET status = 'ABGELOEST', reason = 'x' "
        "WHERE status = 'GENEHMIGT'",
        "DELETE FROM milestones_planversion WHERE status = 'GENEHMIGT'",
        "UPDATE milestones_planentry SET date = '2026-03-03' WHERE kind = 'MEILENSTEIN'",
        "DELETE FROM milestones_planentry",
    ],
)
def test_genehmigte_version_in_der_datenbank_unveraenderlich(welt, sql):
    v1 = plan(welt, {"M0": D(2026, 2, 1)})
    with pytest.raises(Exception, match="unveraenderlich"), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(sql)
    v1.refresh_from_db()
    assert v1.status == PlanStatus.GENEHMIGT


@pytest.mark.django_db
def test_eintrag_in_genehmigte_version_einfuegen_wird_in_der_datenbank_abgewiesen(welt):
    a = welt["a"]
    v1 = plan(welt, {"M0": D(2026, 2, 1)})
    with pytest.raises(Exception, match="unveraenderlich"), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO milestones_planentry "
                "(project_id, plan_version_id, kind, milestone_id, date) "
                "VALUES (%s, %s, 'MEILENSTEIN', %s, '2026-04-01')",
                [a.pk, v1.pk, ms(a, "M1").pk],
            )


@pytest.mark.django_db
def test_ablosung_ist_der_einzige_erlaubte_statuswechsel(welt):
    v1 = plan(welt, {"M0": D(2026, 2, 1)})
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE milestones_planversion SET status = 'ABGELOEST' WHERE id = %s", [v1.pk]
        )
    v1.refresh_from_db()
    assert v1.status == PlanStatus.ABGELOEST


@pytest.mark.django_db
def test_termine_ausserhalb_des_zeitraums_werden_abgelehnt(welt):
    with pytest.raises(ValidationError, match="außerhalb"):
        plan(welt, {"M0": D(2027, 2, 1)})


@pytest.mark.django_db
def test_genehmigung_protokolliert_admin_gekennzeichnet(welt):
    v1 = plan(welt, {"M0": D(2026, 2, 1)}, actor="admin")
    assert v1.approved_as_admin and v1.approved_by == welt["users"]["admin"]
    eintrag = AuditLog.objects.get(action="plan.approved")
    assert eintrag.as_admin and eintrag.new_values["project_period"] == ["2026-01-01", "2026-12-31"]


@pytest.mark.django_db
@pytest.mark.parametrize("person", ["ma", "mgmt", "nobody", "pl_b"])
def test_planversionen_nur_projektleitung_und_admin(welt, person):
    a, user = welt["a"], welt["users"][person]
    draft = services.draft_version(a)
    with pytest.raises(PermissionDenied):
        services.approve_plan_version(actor=user, project=a, version=draft)
    with pytest.raises(PermissionDenied):
        services.update_plan_draft(
            actor=user,
            project=a,
            version=draft,
            start_date=D(2026, 1, 1),
            end_date=D(2026, 2, 1),
            milestone_dates=[],
        )


# ---------- Kriterium 8: Prognose und Ist mit Verlauf ----------


@pytest.mark.django_db
def test_jede_aenderung_von_prognose_oder_ist_erzeugt_verlaufseintrag(client, welt):
    a, u = welt["a"], welt["users"]
    m1 = ms(a, "M1")
    services.change_date(
        actor=u["pl"],
        project=a,
        milestone=m1,
        kind="PROGNOSE",
        value=D(2026, 5, 1),
        reason="Erste Schätzung",
    )
    services.change_date(
        actor=u["admin"],
        project=a,
        milestone=m1,
        kind="PROGNOSE",
        value=D(2026, 5, 15),
        reason="Lieferverzug",
    )
    gestern = services.today() - datetime.timedelta(days=1)
    services.change_date(
        actor=u["pl"], project=a, milestone=m1, kind="IST", value=gestern, reason="Erreicht"
    )
    services.change_date(
        actor=u["pl"],
        project=a,
        point="ENDE",
        kind="PROGNOSE",
        value=D(2027, 1, 31),
        reason="Puffer",
    )

    m1.refresh_from_db()
    a.refresh_from_db()
    assert (m1.forecast_date, m1.actual_date, a.forecast_end_date) == (
        D(2026, 5, 15),
        gestern,
        D(2027, 1, 31),
    )
    verlauf = list(
        DateChange.objects.order_by("id").values_list(
            "milestone__code",
            "point",
            "kind",
            "old_value",
            "new_value",
            "actor__email",
            "reason",
            "as_admin",
        )
    )
    assert verlauf == [
        (
            "M1",
            "TERMIN",
            "PROGNOSE",
            None,
            D(2026, 5, 1),
            "pl@test.invalid",
            "Erste Schätzung",
            False,
        ),
        (
            "M1",
            "TERMIN",
            "PROGNOSE",
            D(2026, 5, 1),
            D(2026, 5, 15),
            "admin@test.invalid",
            "Lieferverzug",
            True,
        ),
        ("M1", "TERMIN", "IST", None, gestern, "pl@test.invalid", "Erreicht", False),
        (None, "ENDE", "PROGNOSE", None, D(2027, 1, 31), "pl@test.invalid", "Puffer", False),
    ]
    assert AuditLog.objects.filter(action="date.changed").count() == 4
    # Der genehmigte Plan ändert sich dadurch nicht
    assert selectors.plan_overview(a)["approved"] == {}

    client.force_login(u["mgmt"])
    html = client.get(reverse("milestones:schedule", args=[a.public_id])).content.decode()
    assert (
        "Lieferverzug" in html
        and "01.05.2026 → 15.05.2026" in html
        and "(als Administrator)" in html
    )


@pytest.mark.django_db
def test_prognose_ist_regeln(welt):
    a, pl = welt["a"], welt["users"]["pl"]
    m1 = ms(a, "M1")
    with pytest.raises(ValidationError):
        services.change_date(
            actor=pl, project=a, milestone=m1, kind="PROGNOSE", value=D(2026, 5, 1), reason=" "
        )
    with pytest.raises(ValidationError, match="Zukunft"):
        services.change_date(
            actor=pl,
            project=a,
            milestone=m1,
            kind="IST",
            value=services.today() + datetime.timedelta(days=1),
            reason="x",
        )
    services.change_date(
        actor=pl, project=a, milestone=m1, kind="PROGNOSE", value=D(2026, 5, 1), reason="x"
    )
    with pytest.raises(ValidationError, match="unverändert"):
        services.change_date(
            actor=pl, project=a, milestone=m1, kind="PROGNOSE", value=D(2026, 5, 1), reason="x"
        )
    services.change_date(
        actor=pl, project=a, point="BEGINN", kind="PROGNOSE", value=D(2026, 6, 1), reason="x"
    )
    with pytest.raises(ValidationError, match="Ende"):
        services.change_date(
            actor=pl, project=a, point="ENDE", kind="PROGNOSE", value=D(2026, 5, 1), reason="x"
        )
    with pytest.raises(PermissionDenied):
        services.change_date(
            actor=welt["users"]["ma"],
            project=a,
            milestone=m1,
            kind="PROGNOSE",
            value=D(2026, 6, 1),
            reason="x",
        )
    # Entfernen ist möglich, ebenfalls mit Begründung und Verlauf
    services.change_date(
        actor=pl, project=a, milestone=m1, kind="PROGNOSE", value=None, reason="unklar"
    )
    assert DateChange.objects.filter(milestone=m1).last().new_value is None


@pytest.mark.django_db
def test_terminverlauf_ist_unveraenderlich(welt):
    a, pl = welt["a"], welt["users"]["pl"]
    change = services.change_date(
        actor=pl, project=a, milestone=ms(a, "M1"), kind="PROGNOSE", value=D(2026, 5, 1), reason="x"
    )
    with pytest.raises(AppendOnlyError):
        change.save()
    with pytest.raises(AppendOnlyError):
        DateChange.objects.all().delete()
    for sql in (
        "UPDATE milestones_datechange SET reason = 'y'",
        "DELETE FROM milestones_datechange",
    ):
        with pytest.raises(Exception, match="nur anfuegbar"), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(sql)
    assert DateChange.objects.get().reason == "x"


# ---------- Kriterium 11: Projektzeitraum und genehmigter Plan synchron ----------


@pytest.mark.django_db
def test_projektzeitraum_und_genehmigter_plan_laufen_nicht_auseinander(client, welt):
    a, pl = welt["a"], welt["users"]["pl"]
    # Vor der ersten Genehmigung: Projektzeitraum frei änderbar, Entwurf wird mitgeführt
    project_services.update_project(actor=pl, project=a, end_date=D(2027, 1, 31))
    draft = services.draft_version(a)
    assert draft.entries.get(kind="ZEITRAUM").end_date == D(2027, 1, 31)
    assert period_in_sync(a)

    # Genehmigung übernimmt den Zeitraum des Plans
    plan(welt, {"M0": D(2026, 2, 1)}, start=D(2026, 1, 15), ende=D(2027, 2, 28))
    a.refresh_from_db()
    assert (a.start_date, a.end_date) == (D(2026, 1, 15), D(2027, 2, 28))
    assert period_in_sync(a)

    # Danach: direkte Änderung abgelehnt (Service) ...
    with pytest.raises(ValidationError):
        project_services.update_project(actor=pl, project=a, end_date=D(2027, 6, 30))
    with pytest.raises(ValidationError):
        project_services.update_project(
            actor=welt["users"]["admin"], project=a, start_date=D(2026, 1, 1)
        )
    project_services.update_project(
        actor=pl, project=a, name="Umbenannt"
    )  # anderes bleibt änderbar
    assert period_in_sync(a)

    # ... und im Formular gesperrt: eingesandte Werte werden ignoriert
    client.force_login(pl)
    url = reverse("projects:edit", args=[a.public_id])
    html = client.get(url).content.decode()
    assert "durch eine genehmigte Planversion festgelegt" in html
    assert html.count("disabled") >= 2
    response = client.post(
        url, {"name": "Formular", "start_date": "2025-01-01", "end_date": "2030-12-31"}
    )
    assert response.status_code == 302
    a.refresh_from_db()
    assert a.name == "Formular" and (a.start_date, a.end_date) == (D(2026, 1, 15), D(2027, 2, 28))

    # Neue Planversion: Zeitraum folgt der Genehmigung
    plan(
        welt,
        {"M0": D(2026, 2, 1)},
        start=D(2026, 1, 15),
        ende=D(2027, 4, 30),
        reason="Verlängerung",
    )
    assert period_in_sync(a)
    a.refresh_from_db()
    assert a.end_date == D(2027, 4, 30)


@pytest.mark.django_db
def test_entwurf_bearbeiten_aendert_projektzeitraum_erst_bei_genehmigung(welt):
    a, pl = welt["a"], welt["users"]["pl"]
    draft = services.draft_version(a)
    services.update_plan_draft(
        actor=pl,
        project=a,
        version=draft,
        start_date=D(2026, 3, 1),
        end_date=D(2026, 9, 30),
        milestone_dates=[],
    )
    a.refresh_from_db()
    assert (a.start_date, a.end_date) == (D(2026, 1, 1), D(2026, 12, 31))
    services.approve_plan_version(actor=pl, project=a, version=draft)
    a.refresh_from_db()
    assert (a.start_date, a.end_date) == (D(2026, 3, 1), D(2026, 9, 30))


# ---------- Oberfläche Termine ----------


@pytest.mark.django_db
def test_terminseite_zeigt_vier_terminbegriffe_und_zeitstrahl(client, welt):
    a = welt["a"]
    plan(welt, {"M0": D(2026, 2, 1), "M1": D(2026, 3, 1)})
    plan(welt, {"M0": D(2026, 2, 1), "M1": D(2026, 4, 1)}, reason="Verschiebung")
    client.force_login(welt["users"]["mgmt"])
    html = client.get(reverse("milestones:schedule", args=[a.public_id])).content.decode()
    for begriff in ("Ursprünglicher Plan", "Genehmigter Plan", "Prognose", "Ist", "Zeitstrahl"):
        assert begriff in html
    assert "01.03.2026" in html and "01.04.2026" in html
    assert 'class="tl__point' in html
    assert "Neuen Planentwurf anlegen" not in html  # Management liest nur
    assert "Ohne Termin und daher nicht bewertet" in html


@pytest.mark.django_db
def test_entwurf_ueber_oberflaeche_bearbeiten_und_genehmigen(client, welt):
    a = welt["a"]
    client.force_login(welt["users"]["pl"])
    url = reverse("milestones:plan", args=[a.public_id, 1])
    m0 = ms(a, "M0")
    response = client.post(
        url,
        {
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "reason": "Start",
            f"ms_{m0.pk}": "2026-02-02",
        },
    )
    assert response.status_code == 302
    assert client.post(reverse("milestones:plan_approve", args=[a.public_id, 1])).status_code == 302
    assert services.approved_version(a).entries.get(milestone=m0).date == D(2026, 2, 2)
    # Genehmigte Version: kein Formular, POST abgewiesen
    html = client.get(url).content.decode()
    assert "unveränderlich" in html and "Entwurf speichern" not in html
    assert (
        client.post(url, {"start_date": "2026-01-01", "end_date": "2026-12-31"}).status_code == 403
    )
