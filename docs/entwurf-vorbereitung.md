# ENTWURF: Vorbereitungsergebnis und Entscheidungsvorlage

Status: **Entwurf zur gemeinsamen Entscheidung**. Nichts davon ist beschlossen. Stand: 21. Oktober 2026.
Grundlage: Auftrag in `docs/claude-startauftrag.md`. Erarbeitet nacheinander von Product Owner, Enterprise-Architekt und Softwarearchitekt; zusammengeführt und technisch nachgeprüft im Hauptdialog.

Bestehende Anforderungsdokumente (`produktgrundlage.md`, `backlog.md`, `vorbereitung-und-betrieb.md`, `styleguide-briefing.md`) wurden **nicht verändert**. Wo dieser Entwurf etwas vorschlägt, das dort offen ist, ist es als Vorschlag gekennzeichnet.

## Zugehörige Entwürfe

| Datei | Inhalt |
| --- | --- |
| `docs/entwurf-technik-und-betrieb.md` | Technologievorschlag, Dev/Prod, Deployment-Pipeline, Prod-Freigabe, Sicherung, Aufwand |
| `docs/entwurf-datenmodell-und-rechte.md` | Module, Datenmodell, Rollenrechte, technische Rechteprüfung |
| `docs/entwurf-erster-entwicklungsabschnitt.md` | Vorschlag für V07 mit Abnahmekriterien, Tests, Ordnerstruktur, Befehlen |

## 1. Bestandsaufnahme (nur gelesen, nichts installiert)

**Projektdateien:** `CLAUDE.md`, `README.md`, `.gitignore`, `.claude/agents/` (sechs Rollen), `docs/` mit Produktgrundlage, Backlog, Betrieb, Rollen, Styleguide-Briefing, Einrichtungsstand, Startauftrag und `docs/decisions/README.md`. Keine Anwendung, keine Abhängigkeiten.

**Git:** `main` ist synchron mit `origin/main`, letzte Commits `c450e72` und `46ba935`. Git funktioniert nur über den Codex-Laufzeitpfad (siehe `einrichtungsstand.md`), nicht über `git` im Suchpfad.

**Lokale Werkzeuge (Windows 11 Home), geprüft per Suchpfad:**

| Werkzeug | Befund |
| --- | --- |
| git | nicht im Suchpfad; nur Codex-Pfad |
| python | nur `WindowsApps\python.exe` gefunden, vermutlich der Microsoft-Store-Platzhalter (nicht ausgeführt, ungeprüft) |
| wsl.exe | vorhanden; installierte Distributionen nicht geprüft |
| node, npm, docker, psql, java, dotnet, gh, code | nicht gefunden |

Folge: Vor dem ersten Entwicklungsabschnitt ist eine lokale Entwicklungsumgebung einzurichten (siehe Entscheidung E5). Das ist eine Installation und wird erst nach deiner Freigabe vorbereitet.

## 2. Bestätigte Anforderungen mit Wirkung auf die Architektur

Kurzfassung; Fundstellen in Klammern (PG = produktgrundlage.md, VB = vorbereitung-und-betrieb.md).

- Webanwendung mit Backend, Datenbank, Dateiablage und Berechtigungen; erst persönlich, später Team auf VPS (PG Ziel).
- Getrennte Dev- und Prod-Umgebung mit Deployment-Pipeline; Daten, Dateien, Secrets und Mail getrennt (PG Ziel, VB Dev und Prod, CLAUDE.md).
- Rolloutplattform wird nicht nachgebaut (PG Ziel).
- Vier Rollen; Freigaben nur durch Projektleiter, nie automatisch durch ein Datum; Management sieht zugeordnete Projekte (PG Benutzerrollen).
- Rechte im Backend, auch bei direktem Datei- und Objektzugriff (CLAUDE.md).
- Mehrfachzuweisung als eine gemeinsame Aufgabe mit gemeinsamem Status; ein Bucket, optional ein Meilenstein; erledigte Aufgaben bleiben sichtbar; Abschluss wer/wann; Wiederöffnen mit Recht (PG Aufgabenmanagement).
- Persönliche Aufgaben ohne Projekt (PG Persönlicher Arbeitsplatz).
- Archivieren; Löschen mit eigenem Recht und Bestätigung (PG Projektbereich).
- Ursprünglicher Plan, genehmigter Plan, Prognose und Ist getrennt und historisiert; Terminänderungen nachvollziehbar (PG Projektstatus).
- Fehlende oder veraltete Daten nie automatisch grün (PG Projektstatus).
- PDF-Download aller erzeugten Dokumente; veröffentlichter Statusbericht unverändert abrufbar (PG Dateien).
- Tägliche Sammelmail zu überfälligen Aufgaben, serverseitig, ohne Doppelversand (PG Reminder, CLAUDE.md).
- Versionierte Datenbankänderungen; Wiederherstellung umfasst Datenbank, Dateien, Konfiguration (CLAUDE.md).

## 3. Was den technischen Aufbau wirklich blockiert

Nur diese Punkte müssen vor dem ersten Code entschieden sein. Für jeden liegt ein Vorschlag vor, mit dem weitergearbeitet werden kann.

| Nr. | Thema | Vorschlag |
| --- | --- | --- |
| B1 | Anmeldung | Eigene Konten der Anwendung, vom Admin angelegt, keine Selbstregistrierung. SSO (z. B. Microsoft) später nachrüstbar. |
| B2 | Aufbau der Rechte | Globale Rolle je Konto plus Projektmitgliedschaft mit Projektrolle. Projektzugriff nur über Mitgliedschaft; Admin liest alles, erteilt aber keine Freigaben. |
| B3 | Aufgabenstatus | Zunächst Offen, In Arbeit, Erledigt; Abschluss und Wiederöffnen als Verlauf; keine Pflicht-Hauptverantwortung. |
| B4 | Löschen | Logisch löschen; endgültiges Bereinigen ist ein gesonderter Admin-Vorgang mit Anzeige der betroffenen Inhalte. |
| B5 | Planfreigabe | Jede Änderung am genehmigten Plan ergibt eine neue, unveränderliche Planversion mit Ursache; einstufige Freigabe durch den Projektleiter. Prognosen ohne Freigabe. |
| B6 | Organisationsrahmen | Eine Organisation, keine Mandanten; Oberfläche Deutsch; Zeitzone Europe/Berlin, Speicherung in UTC. |

**Nicht blockierend, bewusst offen gehalten:**

- **Phasenmodell:** wird nicht modelliert. Später als optionales Objekt am Projekt ergänzbar, ohne Umbau (siehe Datenmodell, Erweiterungspunkt).
- **Styleguide:** Gestaltung liegt ausschließlich in austauschbaren CSS-Variablen und Vorlagen; der erste Abschnitt hat absichtlich eine schlichte, ungestaltete Oberfläche. Kein Branding wird erfunden.
- **Dokumentvorlagen, Steckbrief-Pflichtfelder:** generisches Modell Vorlage → Dokumentstand → PDF.
- **Toleranzen, Statuskennzahlen, Eskalation, Berichtsversand, Word-Export, Budget, Import:** spätere Funktionen auf demselben Fundament.

## 4. Entscheidungsvorlage

Ein konkreter Vorschlag je Punkt. Du kannst jeweils zustimmen, eine Alternative wählen oder ändern. Nach deiner Entscheidung halte ich die Ergebnisse als Entscheidungen in `docs/decisions/` fest.

| Nr. | Entscheidung | Vorschlag | Wichtigste Alternative |
| --- | --- | --- | --- |
| E1 | Technische Grundrichtung | Python + **Django**, Seiten werden auf dem Server erzeugt, **PostgreSQL**, PDF mit **WeasyPrint**, eigener Scheduler-Prozess für Reminder | TypeScript/Next.js mit React: mehr Bauteile, Rechte und Migrationen selbst zusammensetzen |
| E2 | Django-Version | **Start mit Django 5.2 LTS**, geplantes Upgrade auf **6.2 LTS** (erscheint laut Plan April 2027) vor oder kurz nach der Teamfreigabe | Django 6.1, falls ein kurzer technischer Test zeigt, dass alle Zusatzpakete damit laufen |
| E3 | Rechte und Anmeldung | B1 bis B6 wie oben; Rechtematrix aus `entwurf-datenmodell-und-rechte.md` | Admin mit Freigaberecht, oder SSO von Anfang an |
| E4 | Umgebungen und Freigabe | **Ein VPS mit zwei isolierten Stacks** (Dev, Prod). CI baut ein Image; Dev aktualisiert sich automatisch; **Prod nur durch dich per Befehl auf dem Server** mit genau der Version, die auf Dev lief. Prod-Zugangsdaten nicht in GitHub | Zwei getrennte VPS; oder Prod-Deployment aus GitHub Actions (dann liegt der Prod-Schlüssel in GitHub, ohne echte Freigabestufe) |
| E5 | Lokale Entwicklung | **WSL2 (Ubuntu) mit Docker Engine**, Repository und Claude Code arbeiten in WSL; dauerhafte Git-Installation dort | Docker Desktop unter Windows (Unterstützung für Windows 11 Home auf der Herstellerseite nicht eindeutig) |
| E6 | Erster Entwicklungsabschnitt | „Anmeldung, Projektgrenzen, gemeinsame Aufgaben“, nur lokal, 12 Abnahmekriterien | Zuerst klickbarer Oberflächenprototyp ohne Datenhaltung (PG „Nächster sinnvoller Schritt“) |
| E7 | Admin-Sichtbarkeit | Admin liest alle Projekte und verwaltet Mitgliedschaften (protokolliert), sieht **keine** fremden persönlichen Aufgaben, erteilt keine Freigaben | Admin nur mit Mitgliedschaft im Projekt |

**Hinweis zu E2, Abweichung vom Architektenvorschlag:** Der Softwarearchitekt empfahl Django 6.1. Bei der Prüfung im Hauptdialog führten zwei vorgesehene Zusatzpakete auf PyPI Django 6.1 noch nicht als unterstützt (django-axes 8.3.1 und pytest-django 4.14.0 nennen bis Django 6.0). Das kann bloß veraltete Angabe sein, ist aber ein Risiko. 5.2 LTS ist breit unterstützt, erhält Sicherheitsupdates bis April 2028 und der Weg LTS → LTS ist der übliche Pfad. Neu geschriebener Code ohne veraltete Funktionen lässt sich voraussichtlich mit überschaubarem Aufwand auf 6.2 heben.

**Hinweis zu E6:** Die Produktgrundlage nennt einen klickbaren Prototyp als nächsten sinnvollen Schritt. Der Vorschlag hier zieht stattdessen eine kleine echte Funktion vor, weil Rechte, Mehrfachzuweisung und Wiederöffnen nur mit echter Datenhaltung belastbar prüfbar sind. Ein Gestaltungsprototyp zum Styleguide (V06) kann parallel als reine Ansicht mit Beispieldaten entstehen. Das ist deine Produktentscheidung.

## 5. Offene Fragen mit Empfehlung

1. Eigene Konten oder Firmenkonto (SSO)? *Empfehlung: eigene Konten, SSO später.*
2. Wer legt Projekte an, wer löscht endgültig? *Empfehlung: Anlegen Admin und Projektleiter, Löschen nur Admin.*
3. Dürfen Mitarbeiter Aufgaben anlegen, und darf nur der Projektleiter wiederöffnen? *Empfehlung: zweimal ja (Admin zusätzlich zur Korrektur).*
4. Reichen zunächst drei Aufgabenstatus ohne Pflicht-Hauptverantwortung? *Empfehlung: ja.*
5. Reminder lieber „höchstens einmal“ (seltener Ausfall möglich, nie doppelt) oder „mindestens einmal“ (selten doppelt)? *Empfehlung: höchstens einmal, hängende Zustellungen werden sichtbar gemeldet und manuell nachgesendet.*

## 6. Prüfprotokoll technischer Aussagen

Am 21. Oktober 2026 in offizieller Dokumentation geprüft:

| Aussage | Quelle |
| --- | --- |
| Django 6.1.2 aktuell (Support bis Dez. 2027); 5.2 LTS Sicherheitsupdates bis April 2028; 6.2 LTS geplant April 2027, Support bis April 2030 | djangoproject.com/download |
| Django 6.1: Python 3.12–3.15, PostgreSQL ab 15 | Django 6.1 Release Notes |
| Django 5.2: Python 3.10–3.14 (3.14 ab 5.2.8), PostgreSQL ab 14 | Django 5.2 FAQ und Datenbankhinweise |
| Django Tasks-Framework: nur Immediate- und Dummy-Backend für Entwicklung/Test, kein Worker | Django 6.1 Doku „Tasks“ |
| Argon2 in Django über `argon2-cffi`, Standard ist PBKDF2 | Django Doku „Password management“ |
| PostgreSQL 18 neueste unterstützte Hauptversion, Support bis Nov. 2030 | postgresql.org/support/versioning |
| WeasyPrint 70.0, Python ab 3.10, unter Linux Pango ab 1.44; unter Windows aufwendig (MSYS2) | WeasyPrint Doku „First steps“ |
| GitHub Free/Pro/Team: Required reviewers, Wartezeit und eigene Schutzregeln für Umgebungen nur in öffentlichen Repositories; Environment-Secrets bei Free nur öffentlich | docs.github.com, Deployments and environments |
| GitHub Actions Free, privat: 2.000 Minuten und 500 MB je Monat; ohne Zahlungsmittel Sperre statt Kosten; Self-hosted Runner kostenfrei | docs.github.com, Billing GitHub Actions |
| GHCR: Container-Speicher und -Bandbreite derzeit kostenfrei | docs.github.com, Billing GitHub Packages |
| GHCR außerhalb von Actions nur mit klassischem Token (`read:packages`), kein fine-grained Token | docs.github.com, Container registry |
| Caddy: automatisches HTTPS, braucht DNS auf den Server und Ports 80/443 | caddyserver.com/docs/automatic-https |
| Docker Desktop: kostenfrei für privat und kleine Firmen (unter 250 Beschäftigte und unter 10 Mio. USD Umsatz); WSL2-Anforderungen nennen Windows 11 Pro/Enterprise/Education, Home nicht eindeutig | docs.docker.com, Install on Windows |
| django-axes 8.3.1 (MIT), Django-Angabe bis 6.0 | pypi.org |
| pytest-django 4.14.0, Django-Angabe bis 6.0 | pypi.org |
| django-tasks 0.12.0 enthält nur Dummy/Immediate; Datenbank-Backend separat (`django-tasks-db`) | pypi.org |
| htmx 2.0.11 als aktuelle Version; htmx 4.0 veröffentlicht, aber noch nicht als „latest“ markiert | htmx.org |

**Ungeprüft** (vor Festlegung prüfen): Versionen und Kompatibilität von ruff, uv, factory_boy, django-allauth/mozilla-django-oidc, restic/borg, Mailpit, Docker Engine in WSL unter Windows 11 Home; Lizenz von htmx; Preise und AV-Verträge von VPS-, Mail- und Backup-Anbietern; Plan des GitHub-Kontos (vermutlich Free).
