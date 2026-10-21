import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection


@pytest.mark.django_db
def test_health_meldet_erreichbare_datenbank(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


@pytest.mark.django_db
def test_health_meldet_ausfall_ohne_details(client, monkeypatch):
    def kaputt():
        raise RuntimeError("geheimer Verbindungsfehler")

    monkeypatch.setattr("apps.core.views.connection.cursor", kaputt)
    response = client.get("/health/")
    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "error"}


def test_health_erlaubt_nur_get(client):
    assert client.post("/health/").status_code == 405


@pytest.mark.django_db
def test_tests_laufen_gegen_postgresql():
    assert connection.vendor == "postgresql"


def test_eigenes_benutzermodell_ist_aktiv():
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert get_user_model()._meta.label == "accounts.User"


@pytest.mark.django_db
def test_benutzer_wird_in_der_datenbank_gespeichert():
    user = get_user_model().objects.create_user(
        email="beispiel@test.invalid", password="Beispiel-Passwort-123", display_name="Beispiel"
    )
    assert get_user_model().objects.get(pk=user.pk).check_password("Beispiel-Passwort-123")
