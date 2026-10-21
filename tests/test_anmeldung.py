"""Anmeldung, Benutzermodell und Verwaltungsbefehl create_admin (Kriterien V07a 1, 2, 3)."""

import re

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.urls import reverse

from apps.accounts.forms import LOGIN_FEHLER

PASSWORT = "Test-Passwort-fuer-Tests-123"

User = get_user_model()
LOGIN_URL = "/anmelden/"


def _login(client, email, password):
    return client.post(LOGIN_URL, {"username": email, "password": password})


# ---------- Benutzermodell und E-Mail-Eindeutigkeit (Kriterium 3) ----------


@pytest.mark.django_db
def test_email_wird_normalisiert_gespeichert():
    user = User.objects.create_user(email="  Anna.Muster@Test.INVALID ", display_name="Anna")
    assert user.email == "anna.muster@test.invalid"
    assert not user.has_usable_password()


@pytest.mark.django_db
def test_zweites_konto_mit_anderer_schreibweise_wird_abgelehnt():
    User.objects.create_user(email="anna@test.invalid", display_name="Anna")
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create_user(email="ANNA@Test.Invalid", display_name="Anna 2")
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_datenbank_constraint_greift_auch_ohne_normalisierung():
    """Auch ein Umgehen der Normalisierung (bulk_create) scheitert am Lower(email)-Constraint."""
    User.objects.create_user(email="bert@test.invalid", display_name="Bert")
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.bulk_create([User(email="Bert@TEST.invalid", display_name="Bert 2")])


@pytest.mark.django_db
def test_modellvalidierung_meldet_doppelte_email():
    from django.core.exceptions import ValidationError

    User.objects.create_user(email="carla@test.invalid", display_name="Carla")
    with pytest.raises(ValidationError):
        User(email="CARLA@test.invalid", display_name="Carla 2").full_clean()


@pytest.mark.django_db
def test_email_ist_pflicht():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", display_name="Ohne")


@pytest.mark.django_db
def test_befugnisse_sind_standardmaessig_aus_und_getrennt_vom_django_admin():
    user = User.objects.create_user(email="d@test.invalid", display_name="D")
    assert (user.is_admin, user.can_create_projects, user.can_delete_projects) == (
        False,
        False,
        False,
    )
    su = User.objects.create_superuser(email="su@test.invalid", display_name="SU")
    assert su.is_staff and su.is_superuser and not su.is_admin


@pytest.mark.django_db
def test_passwort_wird_mit_argon2_gehasht():
    user = User.objects.create_user(email="e@test.invalid", password=PASSWORT, display_name="E")
    assert identify_hasher(user.password).algorithm == "argon2"


# ---------- Anmeldung (Kriterien 1 und 2) ----------


@pytest.mark.django_db
def test_anmeldung_mit_anderer_schreibweise_der_email(client, make_user):
    make_user("frida@test.invalid", password=PASSWORT)
    response = _login(client, "FRIDA@Test.invalid", PASSWORT)
    assert response.status_code == 302
    assert response.url == reverse("projects:list")


@pytest.mark.django_db
def test_gleiche_fehlermeldung_bei_falschem_passwort_und_unbekanntem_konto(client, make_user):
    make_user("gus@test.invalid", password=PASSWORT)
    falsch = _login(client, "gus@test.invalid", "falsch-falsch-falsch")
    unbekannt = _login(client, "niemand@test.invalid", "falsch-falsch-falsch")
    for response in (falsch, unbekannt):
        assert response.status_code == 200
        assert response.context["form"].non_field_errors() == [LOGIN_FEHLER]
        assert "_auth_user_id" not in client.session
    # Die Seiten unterscheiden sich nur in der eingegebenen Adresse und im CSRF-Token
    assert _ohne_csrf(falsch.content, b"gus@test.invalid") == _ohne_csrf(
        unbekannt.content, b"niemand@test.invalid"
    )


def _ohne_csrf(content, email):
    content = content.replace(email, b"X")
    return re.sub(rb'name="csrfmiddlewaretoken" value="[^"]+"', b"", content)


@pytest.mark.django_db
def test_deaktiviertes_konto_erhaelt_dieselbe_meldung(client, make_user):
    make_user("hanna@test.invalid", password=PASSWORT, is_active=False)
    response = _login(client, "hanna@test.invalid", PASSWORT)
    assert response.context["form"].non_field_errors() == [LOGIN_FEHLER]


@pytest.mark.django_db
def test_sperre_nach_fuenf_fehlversuchen(client, make_user):
    make_user("ida@test.invalid", password=PASSWORT)
    for _ in range(4):
        assert _login(client, "ida@test.invalid", "falsch").status_code == 200
    fuenfter = _login(client, "ida@test.invalid", "falsch")
    assert fuenfter.status_code == 429
    # Auch das richtige Passwort hilft während der Sperre nicht, auch nicht in anderer Schreibweise
    gesperrt = _login(client, "IDA@test.invalid", PASSWORT)
    assert gesperrt.status_code == 429
    assert "vorübergehend gesperrt".encode() in gesperrt.content
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_sperre_verraet_keine_kontoexistenz(client, make_user):
    make_user("jule@test.invalid", password=PASSWORT)
    for email in ("jule@test.invalid", "unbekannt@test.invalid"):
        responses = [_login(client, email, "falsch") for _ in range(5)]
        assert [r.status_code for r in responses] == [200, 200, 200, 200, 429]


@pytest.mark.django_db
def test_erfolgreiche_anmeldung_setzt_zaehler_zurueck(client, make_user):
    make_user("kai@test.invalid", password=PASSWORT)
    for _ in range(4):
        _login(client, "kai@test.invalid", "falsch")
    assert _login(client, "kai@test.invalid", PASSWORT).status_code == 302
    client.post(reverse("accounts:logout"))
    for _ in range(4):
        assert _login(client, "kai@test.invalid", "falsch").status_code == 200


@pytest.mark.django_db
def test_abmelden_nur_per_post(client, make_user):
    client.force_login(make_user())
    assert client.get(reverse("accounts:logout")).status_code == 405
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_sitzung_nach_abmelden_ungueltig(client, make_user, settings):
    make_user("lara@test.invalid", password=PASSWORT)
    assert _login(client, "lara@test.invalid", PASSWORT).status_code == 302
    alte_sitzung = client.cookies[settings.SESSION_COOKIE_NAME].value
    assert client.get(reverse("projects:list")).status_code == 200

    response = client.post(reverse("accounts:logout"))
    assert response.status_code == 302
    assert response.url == reverse("accounts:login")

    # Alte Sitzungskennung erneut verwenden: kein Zugriff mehr
    client.cookies[settings.SESSION_COOKIE_NAME] = alte_sitzung
    response = client.get(reverse("projects:list"))
    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
def test_abmelden_ohne_csrf_token_wird_abgelehnt(make_user):
    from django.test import Client

    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(make_user())
    assert csrf_client.post(reverse("accounts:logout")).status_code == 403


@pytest.mark.django_db
def test_anmeldeseite_ohne_selbstregistrierung(client):
    response = client.get(LOGIN_URL)
    assert response.status_code == 200
    assert b"Registrieren" not in response.content
    assert client.get("/registrieren/").status_code == 404


# ---------- create_admin ----------


@pytest.mark.django_db
def test_create_admin_legt_administrator_an(monkeypatch):
    monkeypatch.setattr("getpass.getpass", lambda prompt="": "Sehr-Sicheres-Passwort-2026")
    call_command("create_admin", email="Chefin@Test.invalid", name="Chefin")
    user = User.objects.get(email="chefin@test.invalid")
    assert user.is_admin and not user.is_staff and not user.is_superuser
    assert user.check_password("Sehr-Sicheres-Passwort-2026")


@pytest.mark.django_db
def test_create_admin_lehnt_doppelte_email_und_schwaches_passwort_ab(monkeypatch, make_user):
    make_user("vorhanden@test.invalid")
    monkeypatch.setattr("getpass.getpass", lambda prompt="": "Sehr-Sicheres-Passwort-2026")
    with pytest.raises(CommandError):
        call_command("create_admin", email="VORHANDEN@test.invalid", name="X")
    monkeypatch.setattr("getpass.getpass", lambda prompt="": "123")
    with pytest.raises(CommandError):
        call_command("create_admin", email="neu@test.invalid", name="Neu")
    assert not User.objects.filter(email="neu@test.invalid").exists()


# ---------- Sperre je IP-Adresse allein ----------


@pytest.mark.django_db
def test_ip_sperre_nach_vielen_adressen(client, make_user, settings):
    """Viele verschiedene Adressen von einer IP: Sperre beim 30. Fehlversuch, für alle Konten."""
    assert settings.LOGIN_IP_FAILURE_LIMIT == 30
    make_user("opfer@test.invalid", password=PASSWORT)
    for i in range(29):
        assert _login(client, f"versuch{i}@test.invalid", "falsch").status_code == 200
    assert _login(client, "versuch29@test.invalid", "falsch").status_code == 429
    # Auch ein richtiges Passwort für ein anderes Konto ist von dieser IP gesperrt
    assert _login(client, "opfer@test.invalid", PASSWORT).status_code == 429
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_ip_sperre_betrifft_andere_ip_nicht(client, make_user, settings):
    settings.LOGIN_IP_FAILURE_LIMIT = 6
    make_user("olga@test.invalid", password=PASSWORT)
    for i in range(6):
        _login(client, f"x{i}@test.invalid", "falsch")
    assert _login(client, "olga@test.invalid", PASSWORT).status_code == 429
    response = client.post(
        LOGIN_URL,
        {"username": "olga@test.invalid", "password": PASSWORT},
        REMOTE_ADDR="10.0.0.99",
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_unter_ip_grenzwert_bleibt_anmeldung_moeglich(client, make_user, settings):
    settings.LOGIN_IP_FAILURE_LIMIT = 6
    make_user("paul@test.invalid", password=PASSWORT)
    for i in range(5):
        _login(client, f"y{i}@test.invalid", "falsch")
    assert _login(client, "paul@test.invalid", PASSWORT).status_code == 302
