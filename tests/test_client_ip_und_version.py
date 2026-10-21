"""Client-IP hinter dem Tunnel (Etappe 3) und Versionsanzeige (F16)."""

import pytest
from django.test import RequestFactory
from django.urls import reverse

from apps.accounts.lockout import client_ip
from apps.core import version

PASSWORT = "Test-Passwort-fuer-Tests-123"


def _req(remote="127.0.0.1", xff=None):
    meta = {"REMOTE_ADDR": remote}
    if xff is not None:
        meta["HTTP_X_FORWARDED_FOR"] = xff
    return RequestFactory().get("/", **meta)


# ---------- Client-IP ----------


def test_ohne_proxy_gilt_remote_addr(settings):
    settings.PX_BEHIND_PROXY = False
    assert client_ip(_req(xff="203.0.113.7")) == "127.0.0.1"


def test_hinter_proxy_gilt_letzter_eintrag(settings):
    settings.PX_BEHIND_PROXY = True
    assert client_ip(_req(xff="203.0.113.7")) == "203.0.113.7"
    # Vom Besucher gefälschte Einträge stehen links, der Tunnel hängt die echte IP rechts an
    assert client_ip(_req(xff="10.9.9.9, 198.51.100.4")) == "198.51.100.4"
    assert client_ip(_req(remote="::1", xff="2001:db8::5")) == "2001:db8::5"


@pytest.mark.parametrize("xff", [None, "", "kein-ip", "1.2.3.4, nonsense"])
def test_hinter_proxy_ungueltiger_header_faellt_auf_remote_addr_zurueck(settings, xff):
    settings.PX_BEHIND_PROXY = True
    assert client_ip(_req(xff=xff)) == "127.0.0.1"


def test_header_von_fremder_verbindung_wird_ignoriert(settings):
    settings.PX_BEHIND_PROXY = True
    assert client_ip(_req(remote="192.0.2.50", xff="203.0.113.7")) == "192.0.2.50"


def _login(client, email, xff):
    return client.post(
        "/anmelden/", {"username": email, "password": "falsch"}, HTTP_X_FORWARDED_FOR=xff
    )


@pytest.mark.django_db
def test_sperre_trifft_echte_besucher_ip_hinter_tunnel(client, settings, make_user):
    settings.PX_BEHIND_PROXY = True
    make_user("tunnel@test.invalid", password=PASSWORT)
    for _ in range(4):
        assert _login(client, "tunnel@test.invalid", "203.0.113.7").status_code == 200
    assert _login(client, "tunnel@test.invalid", "203.0.113.7").status_code == 429
    # Ein anderer Besucher über denselben Tunnel ist nicht gesperrt
    response = client.post(
        "/anmelden/",
        {"username": "tunnel@test.invalid", "password": PASSWORT},
        HTTP_X_FORWARDED_FOR="198.51.100.4",
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_ohne_proxy_hilft_gefaelschter_header_nicht(client, settings, make_user):
    settings.PX_BEHIND_PROXY = False
    make_user("lokal@test.invalid", password=PASSWORT)
    for i in range(5):
        _login(client, "lokal@test.invalid", f"203.0.113.{i}")
    response = client.post(
        "/anmelden/",
        {"username": "lokal@test.invalid", "password": PASSWORT},
        HTTP_X_FORWARDED_FOR="198.51.100.4",
    )
    assert response.status_code == 429


# ---------- Versionsanzeige (F16) ----------


def _fake_git(head="a1b2c3d\n", status=""):
    def git(*args):
        if args[0] == "rev-parse":
            return head
        return status

    return git


def test_version_aus_pyproject():
    assert version.read_version() == "0.1.0"


def test_version_sauber():
    info = version.compute_version_info(git=_fake_git(), environ={})
    assert info == {"version": "0.1.0", "commit": "a1b2c3d", "dirty": False, "instance": "dev"}
    assert version.version_label(info) == "Version: 0.1.0-a1b2c3d"
    assert version.version_tooltip(info) == "Umgebung: dev"


def test_version_geaendert():
    info = version.compute_version_info(git=_fake_git(status=" M src/x.py\n"), environ={})
    assert info["dirty"] is True
    assert version.version_label(info) == "Version: 0.1.0-a1b2c3d*"
    assert version.version_tooltip(info) == "Umgebung: dev; ungespeicherte Änderungen"


def test_version_ohne_git_unbekannt():
    info = version.compute_version_info(git=lambda *a: None, environ={})
    assert info["commit"] == "unbekannt" and info["dirty"] is False
    assert version.version_label(info) == "Version: 0.1.0-unbekannt"


def test_git_status_schliesst_env_und_run_aus():
    aufrufe = []

    def git(*args):
        aufrufe.append(args)
        return "abc1234\n" if args[0] == "rev-parse" else ""

    version.compute_version_info(git=git, environ={})
    status = next(a for a in aufrufe if a[0] == "status")
    assert ":(exclude).env*" in status and ":(exclude)run/" in status


def test_version_ueberschreibbar_fuer_release_pakete(settings):
    settings.PX_INSTANCE = "demo"
    info = version.compute_version_info(
        git=lambda *a: pytest.fail("git darf nicht aufgerufen werden"),
        environ={"PX_VERSION_INFO": "0.2.0 f00ba12"},
    )
    assert version.version_label(info) == "Version: 0.2.0-f00ba12"
    assert version.version_tooltip(info) == "Umgebung: demo"


def test_echter_git_aufruf_liefert_commit_oder_unbekannt():
    info = version.compute_version_info(environ={})
    assert info["commit"] == "unbekannt" or len(info["commit"]) >= 7


@pytest.mark.django_db
def test_versionsanzeige_nur_angemeldet(client, make_user):
    label = version.version_label()
    tooltip = version.version_tooltip()
    assert label.startswith("Version: 0.1.0-")
    assert label not in client.get(reverse("accounts:login")).content.decode()
    client.force_login(make_user())
    html = client.get(reverse("projects:list")).content.decode()
    assert f'<span class="version-info" title="{tooltip}">{label}' in html
    assert f'<span class="sr-only"> ({tooltip})</span>' in html
    assert "Umgebung: dev" in tooltip
    assert label in client.get(reverse("tasks:workplace")).content.decode()
