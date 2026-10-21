"""Rechtematrix: Rolle x Aktion x (eigenes/fremdes Projekt) mit erwarteten Statuscodes.

Abnahmekriterien V07a: 1 (Anmeldung nötig), 4 (Öffnen nur als Mitglied), 5 (Anlegen nur mit
Befugnis), 8 (Mitarbeiter/Management: 403 bei schreibenden Anfragen). Entscheidung 004: Der
Administrator darf alles; Nicht-Mitglieder erhalten 403 „Kein Zugriff auf dieses Projekt“,
unbekannte Projekte 404.
"""

import pytest
from django.urls import reverse

from apps.audit.models import AuditLog
from apps.projects.models import ProjectRole

OK, REDIRECT, FORBIDDEN, NOT_FOUND = 200, 302, 403, 404
LOGIN = "login"  # Weiterleitung zur Anmeldung
KEIN = "kein_zugriff"  # 403 mit Seite „Kein Zugriff auf dieses Projekt“

PROJECT_ACTIONS = [
    "detail_get",
    "edit_get",
    "edit_post",
    "member_add_get",
    "member_add_post",
    "member_roles_get",
    "member_roles_post",
    "member_remove_get",
    "member_remove_post",
]

PL_RECHTE = {
    "detail_get": OK,
    "edit_get": OK,
    "edit_post": REDIRECT,
    "member_add_get": OK,
    "member_add_post": REDIRECT,
    "member_roles_get": OK,
    "member_roles_post": REDIRECT,
    "member_remove_get": OK,
    "member_remove_post": REDIRECT,
}
NUR_LESEN = {a: FORBIDDEN for a in PROJECT_ACTIONS} | {"detail_get": OK}
KEIN_ZUGRIFF = {a: KEIN for a in PROJECT_ACTIONS}
ANONYM = {a: LOGIN for a in PROJECT_ACTIONS}

# (Person, Bereich) -> erwartete Ergebnisse je Aktion
MATRIX = {
    ("anonym", "eigen"): ANONYM,
    ("anonym", "fremd"): ANONYM,
    ("admin", "eigen"): PL_RECHTE,
    ("admin", "fremd"): PL_RECHTE,
    ("pl", "eigen"): PL_RECHTE,
    ("pl", "fremd"): KEIN_ZUGRIFF,
    ("ma", "eigen"): NUR_LESEN,
    ("ma", "fremd"): KEIN_ZUGRIFF,
    ("mgmt", "eigen"): NUR_LESEN,
    ("mgmt", "fremd"): KEIN_ZUGRIFF,
    ("creator", "eigen"): KEIN_ZUGRIFF,  # Befugnis "Projekte anlegen" gibt keinen Zugriff
    ("creator", "fremd"): KEIN_ZUGRIFF,
    ("nobody", "eigen"): KEIN_ZUGRIFF,
    ("nobody", "fremd"): KEIN_ZUGRIFF,
}

FALLE = [
    (person, bereich, aktion, erwartet)
    for (person, bereich), aktionen in MATRIX.items()
    for aktion, erwartet in aktionen.items()
]


def _anfrage(welt, bereich, aktion):
    """Liefert (Methode, URL, Daten) für eine Aktion im eigenen (A) oder fremden (B) Projekt."""
    users, m = welt["users"], welt["memberships"]
    project = welt["a"] if bereich == "eigen" else welt["b"]
    target = m["ma"] if bereich == "eigen" else m["ma_b"]
    pid = project.public_id
    if aktion == "detail_get":
        return "get", reverse("projects:detail", args=[pid]), None
    if aktion == "edit_get":
        return "get", reverse("projects:edit", args=[pid]), None
    if aktion == "edit_post":
        data = {
            "name": "Geändert",
            "description": "neu",
            "start_date": "2026-03-01",
            "end_date": "2026-12-31",
        }
        return "post", reverse("projects:edit", args=[pid]), data
    if aktion == "member_add_get":
        return "get", reverse("projects:member_add", args=[pid]), None
    if aktion == "member_add_post":
        data = {"user": users["nobody"].pk, "roles": [ProjectRole.MITARBEITER]}
        return "post", reverse("projects:member_add", args=[pid]), data
    if aktion == "member_roles_get":
        return "get", reverse("projects:member_roles", args=[pid, target.pk]), None
    if aktion == "member_roles_post":
        data = {"roles": [ProjectRole.MITARBEITER, ProjectRole.MANAGEMENT]}
        return "post", reverse("projects:member_roles", args=[pid, target.pk]), data
    if aktion == "member_remove_get":
        return "get", reverse("projects:member_remove", args=[pid, target.pk]), None
    if aktion == "member_remove_post":
        return "post", reverse("projects:member_remove", args=[pid, target.pk]), {}
    raise AssertionError(aktion)


@pytest.mark.django_db
@pytest.mark.parametrize(("person", "bereich", "aktion", "erwartet"), FALLE)
def test_rechtematrix_projektaktionen(client, welt, person, bereich, aktion, erwartet):
    if person != "anonym":
        client.force_login(welt["users"][person])
    methode, url, daten = _anfrage(welt, bereich, aktion)
    vorher = AuditLog.objects.count()

    response = getattr(client, methode)(url, daten) if daten is not None else client.get(url)

    if erwartet == LOGIN:
        assert response.status_code == 302
        assert response.url.startswith(reverse("accounts:login"))
    elif erwartet == KEIN:
        assert response.status_code == 403
        assert "Kein Zugriff auf dieses Projekt" in response.content.decode()
    else:
        assert response.status_code == erwartet
    if erwartet in (LOGIN, KEIN, FORBIDDEN, NOT_FOUND):
        # Keine Daten preisgegeben, nichts geändert
        assert b"Geheime Beschreibung" not in response.content
        assert AuditLog.objects.count() == vorher
    if methode == "post" and erwartet == REDIRECT:
        assert AuditLog.objects.count() == vorher + 1
        # Admin-Aktionen in Projekten ohne eigene Projektleitung sind gekennzeichnet
        assert AuditLog.objects.latest("id").as_admin is (person == "admin")


ANLEGEN = {
    "anonym": (LOGIN, LOGIN),
    "admin": (OK, REDIRECT),
    "pl": (OK, REDIRECT),
    "creator": (OK, REDIRECT),
    "ma": (FORBIDDEN, FORBIDDEN),
    "mgmt": (FORBIDDEN, FORBIDDEN),
    "nobody": (FORBIDDEN, FORBIDDEN),
}


@pytest.mark.django_db
@pytest.mark.parametrize(("person", "erwartet"), ANLEGEN.items())
def test_rechtematrix_projekt_anlegen(client, welt, person, erwartet):
    if person != "anonym":
        client.force_login(welt["users"][person])
    url = reverse("projects:create")
    data = {"name": "Neu", "start_date": "2026-01-01", "end_date": "2026-02-01"}
    for response, soll in ((client.get(url), erwartet[0]), (client.post(url, data), erwartet[1])):
        if soll == LOGIN:
            assert response.status_code == 302
            assert response.url.startswith(reverse("accounts:login"))
        else:
            assert response.status_code == soll


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("person", "mit_zugriff"),
    [
        ("admin", {"Projekt A", "Projekt B"}),
        ("pl", {"Projekt A"}),
        ("ma", {"Projekt A"}),
        ("mgmt", {"Projekt A"}),
        ("pl_b", {"Projekt B"}),
        ("creator", set()),
        ("nobody", set()),
    ],
)
def test_projektuebersicht_zeigt_alle_projekte_fremde_nur_mit_eckdaten(
    client, welt, person, mit_zugriff
):
    client.force_login(welt["users"][person])
    response = client.get(reverse("projects:list"))
    assert response.status_code == 200
    html = response.content.decode()
    overview = response.context["overview"]
    assert {row["project"].name for row in overview["accessible"]} == mit_zugriff
    alle = {"Projekt A": welt["a"], "Projekt B": welt["b"]}
    ohne_zugriff = set(alle) - mit_zugriff
    assert {row["name"] for row in overview["others"]} == ohne_zugriff

    for name in alle:
        assert name in html  # alle Projekte sind in der Übersicht sichtbar
    for name in ohne_zugriff:
        project = alle[name]
        # Kein Link, keine Beschreibung, keine öffentliche ID
        assert str(project.public_id) not in html
        assert project.description not in html
        row = next(r for r in overview["others"] if r["name"] == name)
        # Im Kontext stehen nur die erlaubten Eckdaten
        assert set(row) == {"name", "start_date", "end_date", "leads"}
        assert [lead.display_name for lead in row["leads"]] == [
            "Pia Leiterin" if name == "Projekt A" else "Paul B"
        ]
    if ohne_zugriff:
        assert "kein Zugriff" in html
    for name in mit_zugriff:
        assert str(alle[name].public_id) in html


@pytest.mark.django_db
def test_fremde_mitglieder_erscheinen_nicht_in_der_uebersicht(client, welt):
    """Für Projekt A (fremd) erscheinen nur Projektleitung, nicht Mitarbeiter oder Management."""
    client.force_login(welt["users"]["ma_b"])
    html = client.get(reverse("projects:list")).content.decode()
    assert "Pia Leiterin" in html
    assert "Mats Arbeiter" not in html
    assert "Mona Management" not in html


@pytest.mark.django_db
@pytest.mark.parametrize("url_name", ["projects:list", "projects:create", "home"])
def test_ohne_anmeldung_weiterleitung(client, url_name):
    response = client.get(reverse(url_name), follow=True)
    assert response.redirect_chain[-1][0].startswith(reverse("accounts:login"))
    assert response.status_code == 200


UNBEKANNT = "00000000-0000-0000-0000-000000000000"


@pytest.mark.django_db
@pytest.mark.parametrize("person", ["admin", "pl", "nobody"])
@pytest.mark.parametrize(
    "pfad",
    ["", "bearbeiten/", "mitglieder/neu/", "mitglieder/1/rollen/", "mitglieder/1/entfernen/"],
)
def test_unbekannte_projekt_id_ist_404(client, welt, person, pfad):
    client.force_login(welt["users"][person])
    assert client.get(f"/projekte/{UNBEKANNT}/{pfad}").status_code == 404


@pytest.mark.django_db
def test_mitgliedschaft_aus_anderem_projekt_ist_404(client, welt):
    """Eine Mitgliedschafts-ID aus Projekt B ist über die URL von Projekt A nicht erreichbar."""
    client.force_login(welt["users"]["pl"])
    fremd = welt["memberships"]["ma_b"]
    url = reverse("projects:member_remove", args=[welt["a"].public_id, fremd.pk])
    assert client.post(url).status_code == 404
    fremd.refresh_from_db()
    assert fremd.is_active


@pytest.mark.django_db
def test_beendete_mitgliedschaft_sieht_projekt_nicht_mehr(client, welt):
    from apps.projects import services

    services.remove_member(
        actor=welt["users"]["pl"], project=welt["a"], membership=welt["memberships"]["ma"]
    )
    client.force_login(welt["users"]["ma"])
    assert client.get(reverse("projects:detail", args=[welt["a"].public_id])).status_code == 403
