"""Serverseitig prüfbare Oberflächenmerkmale (die Optik im Browser ist hier nicht getestet)."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_seitenrahmen_mit_logo_umschalter_und_abmelden_per_post(client, welt):
    client.force_login(welt["users"]["pl"])
    html = client.get(reverse("projects:detail", args=[welt["a"].public_id])).content.decode()
    assert "img/logo-projekt-x.webp" in html
    assert "data-theme-toggle" in html
    assert f'method="post" action="{reverse("accounts:logout")}"' in html
    assert "csrfmiddlewaretoken" in html
    assert reverse("tasks:workplace") in html  # Mein Arbeitsplatz ist seit V07b verlinkt
    assert "Designvorschau" not in html
    assert "cdn" not in html.lower()


@pytest.mark.django_db
@pytest.mark.parametrize("debug", [True, False])
def test_hinweis_entwicklungsumgebung_nur_bei_debug(client, settings, debug):
    settings.DEBUG = debug
    html = client.get(reverse("accounts:login")).content.decode()
    assert ("Entwicklungsumgebung" in html) is debug


@pytest.mark.django_db
def test_lesende_rollen_sehen_keine_bearbeiten_schaltflaechen(client, welt):
    client.force_login(welt["users"]["mgmt"])
    html = client.get(reverse("projects:detail", args=[welt["a"].public_id])).content.decode()
    assert "Projekt bearbeiten" not in html
    assert "Mitglied hinzufügen" not in html
    assert "Mats Arbeiter" in html  # Mitglieder sind lesbar


@pytest.mark.django_db
def test_startseite_leitet_auf_projektuebersicht(client, welt):
    client.force_login(welt["users"]["ma"])
    response = client.get("/")
    assert response.status_code == 302
    assert response.url == reverse("projects:list")
