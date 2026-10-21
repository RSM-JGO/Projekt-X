# IT-Projektmanagementplattform

Vorbereitungsstand vom 21. Oktober 2026. Noch keine Anwendungsimplementierung.

## Einstieg

1. `docs/produktgrundlage.md`: Anforderungen, Vorschläge und offene Produktentscheidungen.
2. `docs/vorbereitung-und-betrieb.md`: Codeablage, Betrieb, Architekturvorbereitung und Reihenfolge.
3. `CLAUDE.md`: Arbeitsregeln für Claude Code.
4. `.claude/agents/`: Rollen für Produktberatung, Architektur, Entwicklung, Test und Review.
5. `docs/claude-startauftrag.md`: Erster Auftrag für die Vorbereitung, noch ohne Implementierung.
6. `docs/backlog.md`: Gemeinsames PO-Backlog und nächster Arbeitsabschnitt.
7. `docs/rollen-und-uebergaben.md`: Zuständigkeiten und Übergaben der sechs Claude-Rollen.
8. `docs/styleguide-briefing.md`: Vorbereitung der noch offenen visuellen Gestaltung.
9. `docs/einrichtungsstand.md`: Nachgewiesener Claude-Zugriff, Versionsstand und lokale Werkzeuglücken.
10. `docs/arbeitsstand.md` und `docs/uebergabe-an-claude.md`: Wiederaufnahme und Weiterarbeit im zentralen Projektleiter-Chat.
11. `docs/pruefung-architekturentwuerfe.md`: Erforderliche Nacharbeit vor Architekturfreigabe.
12. `docs/releaseprozess.md`: Aufgaben des Releasemanagers und vorgeschlagener Releaseablauf.
13. `docs/entwurf-nacharbeit.md`: Überarbeiteter Architekturentwurf (Revision 2, nicht freigegeben) mit neu gegliederter Entscheidungsvorlage.
14. `docs/entwurf-windows-betrieb.md`: Windows-Entwicklung, Windows-Betrieb, Pipeline und externe Demo (Revision 3, Entwurf).
15. `docs/installationsliste-windows.md`: Lokale Installationen zur Freigabe durch den Benutzer.

Der lokale Ordner ist die Arbeitskopie. Das private GitHub-Repository https://github.com/jago1698/projektmanagement-software ist erstellt und als origin verbunden. Die Grundvorbereitung ist hochgeladen. Claude kann die Unterlagen lesen und bestätigt alle acht geladenen Rollen einschließlich Projektleitung und Releasemanager. Lokal eingerichtet sind Python 3.13 (über uv), PostgreSQL 18 und ein Django-5.2-Grundgerüst ohne Oberfläche (Nachweise in docs/einrichtungsstand.md). Server, Domain, E-Mail-Dienst und Deployment-Pipeline sind noch nicht eingerichtet. Aktueller Arbeitsstand: docs/arbeitsstand.md.

## Lokale Entwicklung (Windows, PowerShell)

Voraussetzungen: uv, Python 3.13 über uv, PostgreSQL 18 mit Rolle `projektx` und Datenbank `projektx_dev`. Außerdem eine ausgefüllte `.env` nach dem Muster von `.env.example`.

| Zweck | Befehl |
| --- | --- |
| Pakete installieren | `uv sync` |
| Datenbank migrieren | `uv run python manage.py migrate` |
| Entwicklungsserver | `uv run python manage.py runserver` |
| Start über Waitress | `$env:PYTHONPATH='src'; uv run waitress-serve --listen=127.0.0.1:8000 config.wsgi:application` |
| Tests | `uv run pytest` |
| Codeprüfung | `uv run ruff check` und `uv run ruff format --check` |
| Fehlende Migrationen | `uv run python manage.py makemigrations --check --dry-run` |
| Administrator anlegen (fragt E-Mail, Name, Passwort) | `uv run python manage.py create_admin` (optional `--mit-django-admin` für /admin) |
| Beispieldaten laden: Konten, Projekte, Buckets, Aufgaben (nur mit `DJANGO_DEBUG=1`, Passwort aus `DEMO_PASSWORD`, mehrfach ausführbar) | `uv run python manage.py seed_demo` |

Gesundheitsprüfung: http://127.0.0.1:8000/health/
