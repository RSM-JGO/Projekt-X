"""Versionsanzeige (Backlog F16).

Version aus genau einer Quelle: pyproject.toml. Commit beim Start aus git ermittelt; ohne git
"unbekannt". Uncommittete Änderungen (ohne .env* und run/) ergeben den Zusatz "geändert".
Vorbereitet für Release-Pakete ohne git: PX_VERSION_INFO="<version> <commit>" überschreibt beides.
"""

import functools
import os
import subprocess
import tomllib

from django.conf import settings

UNBEKANNT = "unbekannt"


def _git(*args):
    """Führt git im Projektordner aus; None bei Fehler oder fehlendem git."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout if result.returncode == 0 else None


def read_version():
    with open(settings.BASE_DIR / "pyproject.toml", "rb") as handle:
        return tomllib.load(handle)["project"]["version"]


def compute_version_info(git=_git, environ=None):
    environ = os.environ if environ is None else environ
    instance = getattr(settings, "PX_INSTANCE", "dev")
    override = (environ.get("PX_VERSION_INFO") or "").split()
    if len(override) == 2:
        return {"version": override[0], "commit": override[1], "dirty": False, "instance": instance}

    version = read_version()
    head = git("rev-parse", "--short", "HEAD")
    commit = head.strip() if head and head.strip() else UNBEKANNT
    dirty = False
    if commit != UNBEKANNT:
        status = git("status", "--porcelain", "--", ".", ":(exclude).env*", ":(exclude)run/")
        dirty = bool(status and status.strip())
    return {"version": version, "commit": commit, "dirty": dirty, "instance": instance}


@functools.cache
def version_info():
    """Einmal je Prozess ermittelt (beim ersten Aufruf nach dem Start)."""
    return compute_version_info()


def version_label(info=None):
    """Kurzform für die Fußzeile, z. B. "Version: 0.1.0-2f9337e" (* = ungespeicherte Änderungen)."""
    info = info or version_info()
    return f"Version: {info['version']}-{info['commit']}" + ("*" if info["dirty"] else "")


def version_tooltip(info=None):
    info = info or version_info()
    text = f"Umgebung: {info['instance']}"
    return text + ("; ungespeicherte Änderungen" if info["dirty"] else "")
