# ENTWURF: Erster Entwicklungsabschnitt (Vorschlag für V07)

Status: **Entwurf, nicht beauftragt**. Stand: 21. Oktober 2026. Voraussetzung: Entscheidungen E1 bis E7 in `docs/entwurf-vorbereitung.md` und eine eingerichtete lokale Entwicklungsumgebung.

> **Hinweis Nacharbeit (21. Oktober 2026):** Ursprünglicher Vorschlag, teilweise überholt. Maßgeblich bei Widersprüchen ist `docs/entwurf-nacharbeit.md` (Revision 2, ebenfalls Entwurf, nicht freigegeben).

## Titel

„Anmeldung, Projektgrenzen und gemeinsame Aufgaben“

## Ziel

Ein kleiner, vollständiger Ablauf mit echter Datenbank, der die riskantesten Grundlagen belastbar nachweist: Anmeldung, Projektgrenzen, Rollenrechte, Mehrfachzuweisung sowie Abschließen und Wiederöffnen mit Verlauf.

## Umfang

- Anmelden und Abmelden mit vorbereiteten Konten.
- Projekt anlegen und bearbeiten (nur Name und Zeitraum).
- Mitglieder mit Projektrolle zuordnen.
- Buckets anlegen.
- Aufgabe anlegen mit Titel, Bucket, Fälligkeit und einer oder mehreren zugewiesenen Personen.
- Aufgabenliste im Projekt mit Filter Offen, Erledigt, Alle.
- „Meine Aufgaben“ über alle Projekte.
- Aufgabe abschließen und wiederöffnen, mit sichtbarem Verlauf.
- Schlichte, ungestaltete Oberfläche; Gestaltung bleibt dem Styleguide vorbehalten.

## Ausdrücklich nicht enthalten

Meilensteine, Planstände, Dashboard, Statusbericht, PDF, Dateien, Kommentare, Board- und Kalenderansicht, Reminder und Mail, Archivieren und Löschen, persönliche Aufgaben ohne Projekt, Passwort-Zurücksetzen per Mail, SSO, Styleguide, Server, Dev-Deployment. Gearbeitet wird nur lokal.

## Abnahmekriterien

1. Ohne Anmeldung liefert keine Seite und kein Endpunkt Projektdaten; es folgt eine Weiterleitung zur Anmeldung.
2. Ein falsches Passwort wird abgewiesen, ohne zu verraten, ob das Konto existiert. Nach dem Abmelden ist die Sitzung ungültig.
3. Eine Person sieht nur Projekte, in denen sie Mitglied ist (Admin: alle). Der direkte Aufruf eines fremden Projekts liefert 404 ohne Daten.
4. Eine Aufgabe aus Projekt A lässt sich durch eine Person, die nur in Projekt B Mitglied ist, per direkter Anfrage weder lesen noch ändern.
5. Ein Projektleiter legt eine Aufgabe mit zwei zugewiesenen Personen an. In der Datenbank gibt es genau einen Aufgabendatensatz; die Aufgabe erscheint im Projekt und in „Meine Aufgaben“ beider Personen.
6. Personen, die nicht Mitglied des Projekts sind, können nicht zugewiesen werden; die Anwendung lehnt das ab.
7. Schließt eine zugewiesene Person die Aufgabe ab, ist sie für alle erledigt. Angezeigt wird, wer wann abgeschlossen hat.
8. Erledigte Aufgaben bleiben über die Filter Erledigt und Alle mit ihren Zuweisungen sichtbar.
9. Der Projektleiter öffnet eine erledigte Aufgabe wieder. Sie ist danach offen; der frühere Abschluss bleibt im Verlauf sichtbar.
10. Ein Mitarbeiter kann nicht wiederöffnen (403 vom Backend). Management kann lesen, aber nichts anlegen oder ändern.
11. Daten bleiben nach einem Neustart der Anwendung und der Datenbank erhalten.
12. Automatisierte Tests decken mindestens die Kriterien 3, 4, 5, 6, 7, 9 und 10 ab und laufen lokal sowie in CI erfolgreich. Beispieldaten sind als solche gekennzeichnet und lassen sich in Prod nicht laden.

## Beispieldaten

- Fünf fiktive Konten mit Zusatz „(Beispiel)“: 1 Admin, 1 Projektleiter, 2 Mitarbeiter, 1 Management.
- „Beispielprojekt A“ und „Beispielprojekt B“. Mitarbeiter 1 in beiden Projekten, Mitarbeiter 2 und Management nur in A.
- Je 2 Buckets und etwa 6 Aufgaben, darunter eine mit zwei zugewiesenen Personen und eine bereits erledigte.

## Geplante Tests

- **Einzeltests:** Rechteregeln; Abschließen setzt Abschlussdaten, Wiederöffnen leert sie und schreibt ein Verlaufsereignis; Zuweisung nur an Mitglieder.
- **Integrationstests gegen echtes PostgreSQL:** zwei Zuweisungen ergeben genau eine Aufgabe; doppelte aktive Zuweisung wird von der Datenbank abgewiesen; „Meine Aufgaben“ beider Personen; Filter; beendete Mitgliedschaft entzieht Zugriff; Persistenz über eine neue Verbindung.
- **Rechtematrix:** fremdes Projekt → 404, Mitarbeiter wiederöffnet → 403, Management sendet Änderung → 403.
- **Gleichzeitigkeit:** zwei gleichzeitige Abschlüsse ergeben genau ein Abschlussereignis.
- **CI:** Tests, Code-Prüfung, Prüfung auf fehlende Migrationen.
- **Nicht vorgesehen in diesem Abschnitt:** Browser-End-to-End-Tests und fachliche Benutzerabnahme; die Abnahme machst du anhand der Kriterien.

## Von Anfang an enthalten, obwohl unscheinbar

Eigenes Benutzermodell, UUIDs nach außen, Änderungsfelder, Aufgabenverlauf, versionierte Migrationen, Sperre für Beispieldaten in Prod, Protokoll für Mitgliedschafts- und Rollenänderungen.

## Geplante Ordnerstruktur

```
pyproject.toml, uv.lock, Dockerfile, compose.yaml, .env.example, Makefile
src/config/                Einstellungen aus Umgebungsvariablen, Adressen
src/apps/<modul>/          models, services, selectors, policies, views, urls, migrations/, templates/
src/templates/             gemeinsame Seitenvorlagen
src/static/css/            tokens.css (Gestaltungsvariablen), base.css
src/pdf_templates/         später: PDF-Vorlagen je Dokumentart und Version
tests/<modul>/, tests/permissions/, tests/e2e/ (später)
seed/demo/                 nur Beispieldaten, klar gekennzeichnet
deploy/                    compose.dev.yaml, compose.prod.yaml, Caddyfile, env-Beispiele, scripts/ (deploy-prod, backup, restore)
.github/workflows/ci.yml
docs/, docs/decisions/
```

Im ersten Abschnitt entstehen davon nur `src/config`, `src/apps/core`, `accounts`, `projects`, `tasks`, die zugehörigen Tests, `seed/demo`, Docker-Dateien für lokal und die CI-Datei. `deploy/` folgt mit dem Dev-Server.

## Geplante Befehle (noch nicht ausführbar, nichts installiert)

| Zweck | Befehl |
| --- | --- |
| Datenbank starten | `docker compose up -d db` |
| Migrationen ausführen | `docker compose run --rm web python manage.py migrate` |
| Admin-Konto anlegen | `docker compose run --rm web python manage.py create_admin` |
| Beispieldaten laden (bricht in Prod ab) | `docker compose run --rm web python manage.py seed_demo` |
| Anwendung starten | `docker compose up web` |
| Tests | `docker compose run --rm web pytest` |
| Code-Prüfung | `docker compose run --rm web ruff check` und `ruff format --check` |
| Fehlende Migrationen prüfen | `docker compose run --rm web python manage.py makemigrations --check` |

Die Befehle werden im Makefile gebündelt und nach der Einrichtung in der README dokumentiert.

## Übergaben im Abschnitt

Entwickler setzt um → Tester prüft gegen die Kriterien → Reviewer prüft Rechte, Objektzugriffe und Nachweise → du nimmst fachlich ab. Erst danach gilt der Abschnitt als erledigt.
