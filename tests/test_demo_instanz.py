"""Etappe 3: Demo-Instanz (Einstellungen, check --deploy, statische Dateien, /admin, seed_demo).

Einstellungen werden beim Start geladen. Deshalb prüfen die Tests die Demo-Konfiguration in
einem Unterprozess mit einer Beispiel-Konfigurationsdatei (ohne Datenbankverbindung).
"""

import json
import os
import secrets
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

ROOT = Path(__file__).resolve().parent.parent
BASIS = {
    "PX_INSTANCE": "demo",
    "DJANGO_DEBUG": "0",
    "DB_NAME": "projektx_demo",
    "DB_USER": "projektx_demo",
    "DB_PASSWORD": "nur-ein-testwert",
    "DJANGO_ALLOWED_HOSTS": "beispiel-8100.euw.devtunnels.ms,127.0.0.1,testserver",
    "CSRF_TRUSTED_ORIGINS": "https://beispiel-8100.euw.devtunnels.ms",
    "PX_BEHIND_PROXY": "1",
    "SECURE_HSTS_SECONDS": "3600",
}
SYSTEM_VARS = ("SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "TEMP", "TMP", "COMSPEC", "USERPROFILE")


def _env_datei(tmp_path, **werte):
    inhalt = BASIS | {"DJANGO_SECRET_KEY": secrets.token_urlsafe(64)} | werte
    datei = tmp_path / ".env.demo"
    datei.write_text("".join(f"{k}={v}\n" for k, v in inhalt.items()), encoding="utf-8")
    return datei


def _run(tmp_path, args, **werte):
    """Startet Python mit sauberer Umgebung; nur PX_ENV_FILE zeigt auf die Beispieldatei."""
    env = {k: os.environ[k] for k in SYSTEM_VARS if k in os.environ}
    env["PX_ENV_FILE"] = str(_env_datei(tmp_path, **werte))
    env["PX_STATIC_ROOT"] = str(tmp_path / "staticfiles")
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )


PROBE = r"""
import json, os, sys
sys.path.insert(0, "src")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.conf import settings
from django.urls import Resolver404, resolve
try:
    resolve("/admin/")
    admin = True
except Resolver404:
    admin = False
print(json.dumps({
    "instance": settings.PX_INSTANCE,
    "debug": settings.DEBUG,
    "session_secure": settings.SESSION_COOKIE_SECURE,
    "csrf_secure": settings.CSRF_COOKIE_SECURE,
    "proxy_header": settings.SECURE_PROXY_SSL_HEADER,
    "trusted": settings.CSRF_TRUSTED_ORIGINS,
    "hsts": settings.SECURE_HSTS_SECONDS,
    "preload": settings.SECURE_HSTS_PRELOAD,
    "frame": settings.X_FRAME_OPTIONS,
    "referrer": settings.SECURE_REFERRER_POLICY,
    "nosniff": settings.SECURE_CONTENT_TYPE_NOSNIFF,
    "ssl_redirect": settings.SECURE_SSL_REDIRECT,
    "storage": settings.STORAGES["staticfiles"]["BACKEND"],
    "whitenoise": "whitenoise.middleware.WhiteNoiseMiddleware" in settings.MIDDLEWARE,
    "email": settings.EMAIL_BACKEND,
    "admin_routed": admin,
}))
"""


def _probe(tmp_path, **werte):
    result = _run(tmp_path, ["-c", PROBE], **werte)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_demo_einstellungen(tmp_path):
    s = _probe(tmp_path)
    assert s["instance"] == "demo" and s["debug"] is False
    assert s["session_secure"] and s["csrf_secure"] and s["ssl_redirect"]
    assert s["proxy_header"] == ["HTTP_X_FORWARDED_PROTO", "https"]
    assert s["trusted"] == ["https://beispiel-8100.euw.devtunnels.ms"]
    assert s["hsts"] == 3600 and s["preload"] is False
    assert (s["frame"], s["referrer"], s["nosniff"]) == ("DENY", "same-origin", True)
    assert s["storage"] == "whitenoise.storage.CompressedManifestStaticFilesStorage"
    assert s["whitenoise"] is True
    assert s["email"].endswith("console.EmailBackend")  # kein Mailversand
    assert s["admin_routed"] is False


def test_ohne_proxy_keine_proxy_header(tmp_path):
    assert _probe(tmp_path, PX_BEHIND_PROXY="0")["proxy_header"] is None


@pytest.mark.parametrize(
    ("werte", "meldung"),
    [
        ({"DJANGO_DEBUG": "1"}, "nur in der Instanz dev"),
        ({"DB_NAME": "projektx_dev"}, "Entwicklungsdatenbank"),
        ({"PX_INSTANCE": "test"}, "dev, demo oder prod"),
        ({"DJANGO_SECRET_KEY": "HIER_EINTRAGEN"}, "Platzhalter"),
    ],
)
def test_unsichere_demo_konfiguration_startet_nicht(tmp_path, werte, meldung):
    result = _run(tmp_path, ["-c", PROBE], **werte)
    assert result.returncode != 0
    assert meldung in result.stderr


def test_check_deploy_ohne_warnungen(tmp_path):
    result = _run(tmp_path, ["manage.py", "check", "--deploy", "--fail-level", "WARNING"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "System check identified no issues" in result.stdout


def test_check_deploy_meldet_fehlende_https_weiterleitung(tmp_path):
    """Gegenprobe: Ohne HTTPS-Weiterleitung schlägt die Prüfung an (W008)."""
    result = _run(
        tmp_path, ["manage.py", "check", "--deploy", "--fail-level", "WARNING"], PX_SSL_REDIRECT="0"
    )
    assert result.returncode != 0
    assert "security.W008" in result.stdout + result.stderr


CLIENT = r"""
import json, os, sys
sys.path.insert(0, "src")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.templatetags.static import static
from django.test import Client
c = Client()
css = static("css/app.css")
r_css = c.get(css, secure=True)
ergebnis = {
    "css_url": css,
    "css_status": r_css.status_code,
    "css_cache": r_css.headers.get("Cache-Control", ""),
    "css_gzip": c.get(css, secure=True, HTTP_ACCEPT_ENCODING="gzip").headers.get(
        "Content-Encoding", ""
    ),
    "logo": c.get(static("img/logo-projekt-x.webp"), secure=True).status_code,
    "admin": c.get("/admin/", secure=True).status_code,
    "http_redirect": c.get("/projekte/").status_code,
}
UUID = "00000000-0000-0000-0000-000000000000"
for pfad in ["/", "/projekte/", "/arbeitsplatz/", f"/aufgaben/{UUID}/"]:
    r = c.get(pfad, secure=True)
    ergebnis[pfad] = [r.status_code, r.headers.get("Location", "")]
print(json.dumps(ergebnis))
"""


def test_statische_dateien_ueber_whitenoise_und_anmeldepflicht(tmp_path):
    collect = _run(tmp_path, ["manage.py", "collectstatic", "--noinput"])
    assert collect.returncode == 0, collect.stderr
    static_root = tmp_path / "staticfiles"
    manifest = json.loads((static_root / "staticfiles.json").read_text(encoding="utf-8"))
    hashed = manifest["paths"]["css/app.css"]
    assert hashed != "css/app.css" and (static_root / (hashed + ".gz")).exists()

    result = _run(tmp_path, ["-c", CLIENT])
    assert result.returncode == 0, result.stderr
    r = json.loads(result.stdout.strip().splitlines()[-1])
    assert r["css_url"].endswith(hashed)
    assert r["css_status"] == 200 and "immutable" in r["css_cache"]
    assert r["css_gzip"] == "gzip"
    assert r["logo"] == 200
    assert r["admin"] == 404
    assert r["http_redirect"] == 301  # HTTP wird auf HTTPS umgeleitet
    for pfad in ["/projekte/", "/arbeitsplatz/", "/aufgaben/00000000-0000-0000-0000-000000000000/"]:
        status, ziel = r[pfad]
        assert status == 302 and ziel.startswith("/anmelden/")
    assert r["/"][0] == 302


# ---------- In-Prozess: /admin in dev, seed_demo je Instanz ----------


@pytest.mark.django_db
def test_admin_in_dev_erreichbar(client):
    response = client.get("/admin/")
    assert response.status_code == 302 and "/admin/login/" in response.url


@pytest.mark.django_db
def test_seed_demo_in_demo_instanz_ohne_debug_erlaubt(settings, monkeypatch):
    from django.contrib.auth import get_user_model

    settings.DEBUG = False
    settings.PX_INSTANCE = "demo"
    monkeypatch.setenv("DEMO_PASSWORD", "Demo-Passwort-fuer-Tests-1")
    call_command("seed_demo")
    User = get_user_model()
    admins = list(User.objects.filter(is_admin=True))
    assert [u.email for u in admins] == ["admin@beispiel.invalid"]
    assert "Vorführkonto" in admins[0].display_name
    assert not User.objects.filter(is_staff=True).exists()
    assert not User.objects.filter(is_superuser=True).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("debug", [True, False])
def test_seed_demo_in_prod_immer_gesperrt(settings, monkeypatch, debug):
    from django.contrib.auth import get_user_model

    settings.DEBUG = debug
    settings.PX_INSTANCE = "prod"
    monkeypatch.setenv("DEMO_PASSWORD", "Demo-Passwort-fuer-Tests-1")
    with pytest.raises(CommandError, match="prod"):
        call_command("seed_demo")
    assert not get_user_model().objects.exists()
