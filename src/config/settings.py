"""Einstellungen für Projekt X.

Alle umgebungsabhängigen Werte (Datenbank, Geheimnisse, Debug) kommen aus
Umgebungsvariablen bzw. der lokalen Datei .env, die nicht in Git liegt.
"""

import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def env(name, default=None):
    value = os.environ.get(name, default)
    if value is None:
        raise ImproperlyConfigured(f"Umgebungsvariable {name} fehlt (siehe .env.example).")
    return value


SECRET_KEY = env("DJANGO_SECRET_KEY")
if SECRET_KEY == "HIER_EINTRAGEN" or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY ist ein Platzhalter oder zu kurz (mind. 50 Zeichen)."
    )
DEBUG = env("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")]

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
STATIC_ROOT = BASE_DIR / "staticfiles"

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
