"""Etappe 4a, Review-Korrekturen 1–7 (Nachricht der Projektleitung vom 22.10.2026)."""

import datetime
import re

import pytest
from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse

from apps.milestones import services
from apps.milestones.models import Approval, Deliverable, Milestone
from apps.projects import services as project_services

D = datetime.date


def ms(project, code):
    return Milestone.objects.get(project=project, code=code)


def deliv(project, code, title):
    return Deliverable.objects.get(milestone__project=project, milestone__code=code, title=title)


def genehmigen(welt, termine, start=None, ende=None):
    a, pl = welt["a"], welt["users"]["pl"]
    draft = services.draft_version(a) or services.create_plan_draft(
        actor=pl, project=a, reason="Neu"
    )
    services.update_plan_draft(
        actor=pl,
        project=a,
        version=draft,
        start_date=start or a.start_date,
        end_date=ende or a.end_date,
        milestone_dates=[(ms(a, c), d) for c, d in termine.items()],
    )
    return services.approve_plan_version(actor=pl, project=a, version=draft)


# ---------- 1: geänderte Fehlliste verlangt erneute ausdrückliche Bestätigung ----------


@pytest.mark.django_db
def test_geaenderte_fehlliste_setzt_bestaetigung_zurueck(client, welt):
    a, pl = welt["a"], welt["users"]["pl"]
    m0 = ms(a, "M0")
    url = reverse("milestones:approve", args=[a.public_id, m0.public_id])
    gesehen = ",".join(str(m["id"]) for m in services.missing_required(m0))
    # Zwischen Öffnen und Absenden wird ein Pflichtdokument nachgereicht
    services.set_deliverable_status(
        actor=pl, project=a, deliverable=deliv(a, "M0", "Projektsteckbrief"), status="VORHANDEN"
    )
    client.force_login(pl)
    data = {
        "light": "GRUEN",
        "decision": "Ja",
        "decided_on": services.today().isoformat(),
        "missing_ids": gesehen,
        "confirm_missing": "on",
    }
    response = client.post(url, data)
    html = response.content.decode()
    assert response.status_code == 200 and "geändert" in html
    assert not Approval.objects.exists()
    checkbox = re.search(r'<input[^>]*name="confirm_missing"[^>]*>', html).group(0)
    assert "checked" not in checkbox
    neu = ",".join(str(m["id"]) for m in services.missing_required(m0))
    assert f'name="missing_ids" value="{neu}"' in html
    # Erst mit erneuter Bestätigung der aktuellen Liste
    assert client.post(url, data | {"missing_ids": neu}).status_code == 302
    assert [m["title"] for m in Approval.objects.get().missing_required] == ["Stakeholderliste"]


# ---------- 2: ohne Termin im Menü nie ✓/grün ----------


@pytest.mark.django_db
def test_menue_ohne_termin_nie_gruen(client, welt):
    a, pl = welt["a"], welt["users"]["pl"]
    for title in ("Projektsteckbrief", "Erste Einschätzung der Kritikalität"):
        services.set_deliverable_status(
            actor=pl, project=a, deliverable=deliv(a, "M0", title), status="VORHANDEN"
        )
    assert services.period_locked(a) is False  # vor der ersten Plangenehmigung
    client.force_login(pl)
    html = client.get(reverse("projects:detail", args=[a.public_id])).content.decode()
    menu = html[html.index('<div class="app-nav__sub subnav"') :]
    steckbrief = re.search(r"<li>(?:(?!</li>)[\s\S])*Steckbrief &amp; Auftrag[\s\S]*?</li>", menu)
    eintrag = steckbrief.group(0)
    assert "tone-mint" not in eintrag and "✓" not in eintrag
    assert "nicht bewertet" in eintrag


# ---------- 3: ausgeblendete Meilensteine blockieren den Planentwurf nicht ----------


@pytest.mark.django_db
def test_ausgeblendeter_meilenstein_im_entwurf_sichtbar_und_korrigierbar(client, welt):
    a, pl = welt["a"], welt["users"]["pl"]
    m5 = ms(a, "M5")
    draft = services.draft_version(a)
    services.update_plan_draft(
        actor=pl,
        project=a,
        version=draft,
        start_date=a.start_date,
        end_date=a.end_date,
        milestone_dates=[(m5, D(2026, 12, 1))],
    )
    services.set_milestone_hidden(actor=pl, project=a, milestone=m5, hidden=True)
    client.force_login(pl)
    url = reverse("milestones:plan", args=[a.public_id, draft.number])
    html = client.get(url).content.decode()
    assert (
        "M5 Abschlussfreigabe (ausgeblendet)" in html and '<details class="hidden-entries"' in html
    )

    basis = {"start_date": "2026-01-01", "end_date": "2026-10-31", "reason": "Kürzer"}
    # M5 (ausgeblendet) liegt außerhalb des neuen Zeitraums: Hinweis statt stillem Scheitern
    response = client.post(url, basis | {f"ms_{m5.pk}": "2026-12-01"})
    assert (
        response.status_code == 200
        and "M5: Der Termin liegt außerhalb" in response.content.decode()
    )
    # Im Formular korrigierbar (hier: Termin entfernen)
    assert client.post(url, basis | {f"ms_{m5.pk}": ""}).status_code == 302
    assert not draft.entries.filter(milestone=m5).exists()
    assert (
        client.post(
            reverse("milestones:plan_approve", args=[a.public_id, draft.number])
        ).status_code
        == 302
    )


# ---------- 4: Datenbank verhindert abweichenden Projektzeitraum ----------


@pytest.mark.django_db
def test_direkter_orm_zugriff_kann_zeitraum_nicht_abweichen_lassen(welt):
    a = welt["a"]
    a.start_date = D(2025, 6, 1)
    a.save()  # vor der ersten Genehmigung erlaubt
    genehmigen(welt, {}, start=D(2026, 1, 1), ende=D(2026, 12, 31))
    a.refresh_from_db()
    a.end_date = D(2027, 6, 30)
    with pytest.raises(Exception, match="weicht vom genehmigten Plan ab"), transaction.atomic():
        a.save()
    with pytest.raises(Exception, match="weicht vom genehmigten Plan ab"), transaction.atomic():
        type(a).objects.filter(pk=a.pk).update(start_date=D(2026, 2, 1))
    a.refresh_from_db()
    assert (a.start_date, a.end_date) == (D(2026, 1, 1), D(2026, 12, 31))
    a.name = "Name bleibt änderbar"
    a.save()
    # Über den Genehmigungsservice weiterhin möglich
    genehmigen(welt, {}, start=D(2026, 1, 1), ende=D(2027, 3, 31))
    a.refresh_from_db()
    assert a.end_date == D(2027, 3, 31)


# ---------- 5: bearbeiteter Entwurfszeitraum wird nicht still überschrieben ----------


@pytest.mark.django_db
def test_bearbeiteter_entwurfszeitraum_bleibt_mit_hinweis(client, welt):
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
    client.force_login(pl)
    response = client.post(
        reverse("projects:edit", args=[a.public_id]),
        {"name": a.name, "start_date": "2026-01-01", "end_date": "2027-01-31"},
        follow=True,
    )
    assert "wurde nicht überschrieben" in response.content.decode()
    period = draft.entries.get(kind="ZEITRAUM")
    assert (period.start_date, period.end_date) == (D(2026, 3, 1), D(2026, 9, 30))


@pytest.mark.django_db
def test_unveraenderter_entwurf_folgt_dem_projektzeitraum(welt):
    a, pl = welt["a"], welt["users"]["pl"]
    saved = project_services.update_project(actor=pl, project=a, end_date=D(2027, 1, 31))
    assert not saved.draft_period_kept
    assert services.draft_version(a).entries.get(kind="ZEITRAUM").end_date == D(2027, 1, 31)


# ---------- 6: Migration ist eigenständig ----------


def test_datenmigration_importiert_keinen_anwendungscode():
    from pathlib import Path

    import apps.milestones.migrations as pkg

    source = (
        Path(pkg.__file__).parent / "0003_standard_catalog_and_existing_projects.py"
    ).read_text(encoding="utf-8")
    imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    assert imports == ["from django.db import migrations"]
    assert "apps.get_model" in source


# ---------- 7a: bei gültiger Freigabe nur Korrektur ----------


@pytest.mark.django_db
def test_gueltige_freigabe_nur_per_korrektur_ersetzbar(client, welt):
    a, pl = welt["a"], welt["users"]["pl"]
    Deliverable.objects.filter(milestone__project=a, milestone__code="M0").update(
        status="VORHANDEN"
    )
    m0 = ms(a, "M0")

    def erfassen(light="GRUEN", **extra):
        return services.grant_approval(
            actor=pl,
            project=a,
            milestone=m0,
            light=light,
            decision="x",
            decided_on=services.today(),
            conditions="Auflage" if light == "ORANGE" else "",
            **extra,
        )

    gruen = erfassen()
    with pytest.raises(ValidationError) as exc:
        erfassen("ROT")
    assert exc.value.code == "valid_approval_exists"
    orange = erfassen("ORANGE", replaces=gruen)
    with pytest.raises(ValidationError):
        erfassen()
    rot = erfassen("ROT", replaces=orange)
    erfassen()  # nach Rot ist eine neue Freigabe zulässig
    assert Approval.objects.count() == 4 and rot.replaces == orange

    client.force_login(pl)
    html = client.get(
        reverse("milestones:detail", args=[a.public_id, m0.public_id])
    ).content.decode()
    assert "Freigabe erfassen" not in html and "Aktuelle Freigabe korrigieren" in html


@pytest.mark.django_db
def test_nach_abgelaufener_freigabe_neue_freigabe_zulaessig(welt):
    a, pl = welt["a"], welt["users"]["pl"]
    Deliverable.objects.filter(milestone__project=a, milestone__code="M0").update(
        status="VORHANDEN"
    )
    gestern = services.today() - datetime.timedelta(days=1)
    for decided, valid in (
        (gestern - datetime.timedelta(days=3), gestern),
        (services.today(), None),
    ):
        services.grant_approval(
            actor=pl,
            project=a,
            milestone=ms(a, "M0"),
            light="GRUEN",
            decision="x",
            decided_on=decided,
            valid_until=valid,
        )
    assert Approval.objects.count() == 2


# ---------- 7b: Korrektur friert die Fehlliste zum Korrekturzeitpunkt ein ----------


@pytest.mark.django_db
def test_korrektur_friert_fehlliste_zum_korrekturzeitpunkt_ein(client, welt):
    a, pl = welt["a"], welt["users"]["pl"]
    m0 = ms(a, "M0")
    ids = [m["id"] for m in services.missing_required(m0)]
    alt = services.grant_approval(
        actor=pl,
        project=a,
        milestone=m0,
        light="GRUEN",
        decision="x",
        decided_on=services.today(),
        confirmed_missing=ids,
    )
    Deliverable.objects.filter(milestone=m0).update(status="VORHANDEN")
    neu = services.grant_approval(
        actor=pl,
        project=a,
        milestone=m0,
        light="ORANGE",
        decision="y",
        conditions="z",
        decided_on=services.today(),
        replaces=alt,
    )
    alt.refresh_from_db()
    assert len(alt.missing_required) == 2 and neu.missing_required == []
    client.force_login(pl)
    url = reverse("milestones:approve", args=[a.public_id, m0.public_id]) + "?korrektur=1"
    assert "zum Zeitpunkt der Korrektur neu eingefroren" in client.get(url).content.decode()
