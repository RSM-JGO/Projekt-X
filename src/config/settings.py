"""Einstellungen für Projekt X.

Alle umgebungsabhängigen Werte (Datenbank, Geheimnisse, Debug) kommen aus Umgebungsvariablen
bzw. einer Konfigurationsdatei, die nicht in Git liegt. Welche Datei geladen wird, bestimmt
PX_ENV_FILE (Standard: .env). Bereits gesetzte Umgebungsvariablen haben Vorrang.

Instanzen (PX_INSTANCE): dev (Standard, Entwicklung), demo (externe Demo mit Beispieldaten),
prod (späterer Betrieb). DEBUG ist nur in dev erlaubt.
"""

import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = Path(os.environ.get("PX_ENV_FILE") or ".env")
if not ENV_FILE.is_absolute():
    ENV_FILE = BASE_DIR / ENV_FILE
load_dotenv(ENV_FILE)


def env(name, default=None):
    value = os.environ.get(name, default)
    if value is None:
        raise ImproperlyConfigured(f"Umgebungsvariable {name} fehlt (siehe .env.example).")
    return value


def env_bool(name, default="0"):
    return env(name, default) == "1"


def env_list(name, default=""):
    return [item.strip() for item in env(name, default).split(",") if item.strip()]


PX_INSTANCE = env("PX_INSTANCE", "dev")
if PX_INSTANCE not in ("dev", "demo", "prod"):
    raise ImproperlyConfigured("PX_INSTANCE muss dev, demo oder prod sein.")


SECRET_KEY = env("DJANGO_SECRET_KEY")
if SECRET_KEY == "HIER_EINTRAGEN" or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY ist ein Platzhalter oder zu kurz (mind. 50 Zeichen)."
    )
DEBUG = env_bool("DJANGO_DEBUG")
if DEBUG and PX_INSTANCE != "dev":
    raise ImproperlyConfigured("DJANGO_DEBUG=1 ist nur in der Instanz dev erlaubt.")
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
# Läuft hinter einem Reverse Proxy bzw. Tunnel (Demo): Proxy-Header werden ausgewertet
PX_BEHIND_PROXY = env_bool("PX_BEHIND_PROXY")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "axes",
    "apps.core",
    "apps.accounts",
    "apps.audit",
    "apps.projects",
    "apps.tasks",
    "apps.milestones",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Muss am Ende stehen (Sperre nach Fehlversuchen)
    "axes.middleware.AxesMiddleware",
]

if not DEBUG:
    # Demo/Prod: statische Dateien direkt aus der Anwendung (auch unter Waitress), direkt
    # nach SecurityMiddleware. In dev liefert runserver sie selbst aus (unverändert).
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "src" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.environment",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", "localhost"),
        "PORT": env("DB_PORT", "5432"),
    }
}
if PX_INSTANCE == "demo" and DATABASES["default"]["NAME"].endswith("_dev"):
    raise ImproperlyConfigured("Die Demo darf nicht die Entwicklungsdatenbank verwenden.")

# Eigenes Benutzermodell von Anfang an; später kaum nachrüstbar
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = Path(env("PX_STATIC_ROOT", str(BASE_DIR / "staticfiles")))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Lokal wird keine E-Mail versendet, nur protokolliert
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
STATICFILES_DIRS = [BASE_DIR / "src" / "static"]

# ---------- Anmeldung ----------
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "projects:list"
LOGOUT_REDIRECT_URL = "accounts:login"

# Argon2 als Standard; die übrigen nur zum Prüfen älterer Hashes
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# django-axes zuerst, damit gesperrte Anmeldungen gar nicht erst geprüft werden
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Sperre nach 5 Fehlversuchen für 15 Minuten, gezählt je E-Mail-Adresse und IP-Adresse;
# zusätzlich nach 30 Fehlversuchen je IP-Adresse allein.
# Die Sperre greift auch für nicht existierende Konten, verrät also keine Kontoexistenz.
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_USERNAME_CALLABLE = "apps.accounts.lockout.lockout_username"
AXES_HANDLER = "apps.accounts.lockout.LoginLockoutHandler"
# Zusätzliche Sperre je IP-Adresse allein (eigener Handler, siehe apps/accounts/lockout.py)
LOGIN_IP_FAILURE_LIMIT = 30
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = "accounts/gesperrt.html"
AXES_VERBOSE = False
# Client-IP für die Sperre: hinter dem Tunnel aus X-Forwarded-For, sonst REMOTE_ADDR
# (django-ipware ist nicht installiert, daher eigene Funktion; siehe apps/accounts/lockout.py)
AXES_CLIENT_IP_CALLABLE = "apps.accounts.lockout.client_ip"

# ---------- Statische Dateien ----------
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Dev: Dateien direkt aus src/static. Demo/Prod: komprimiert und mit Inhalts-Hash im Namen
    # (vorher collectstatic), ausgeliefert von WhiteNoise.
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        if DEBUG
        else "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# ---------- Sicherheit außerhalb der Entwicklung (Demo/Prod) ----------
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
if PX_BEHIND_PROXY:
    # Annahme: Der Tunnel (Microsoft Dev Tunnels) beendet HTTPS und setzt X-Forwarded-Proto.
    # Waitress lauscht nur an 127.0.0.1, daher erreicht diesen Header nur der Tunnel.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # Dev Tunnels reicht als Host "localhost:<port>" weiter, die öffentliche Adresse steht in
    # X-Forwarded-Host; ALLOWED_HOSTS prüft weiterhin gegen die erlaubten Namen.
    USE_X_FORWARDED_HOST = True
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Klein gewählt für die Demo; kein preload, weil die Tunneladresse keine eigene Domain ist
    SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", "3600"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", "1")
    SECURE_HSTS_PRELOAD = False
    # Weiterleitung auf HTTPS. Hinter dem Tunnel greift sie dank X-Forwarded-Proto nicht
    # (Aufrufe kommen bereits als HTTPS an). Abschaltbar, falls der Tunnel den Header nicht
    # setzt (dann Endlosweiterleitung); dann wäre security.W008 eine begründete Ausnahme.
    SECURE_SSL_REDIRECT = env_bool("PX_SSL_REDIRECT", "1")
    # Health-Check bleibt lokal per HTTP abrufbar (Startskript prüft damit Waitress)
    SECURE_REDIRECT_EXEMPT = [r"^health/$"]
    # security.W021: HSTS-Preload ist eine dauerhafte Browser-Liste und für eine
    # Tunneladresse ohne eigene Domain nicht sinnvoll (bewusste Ausnahme).
    SILENCED_SYSTEM_CHECKS = ["security.W021"]
