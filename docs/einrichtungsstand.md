# Einrichtungsstand

Stand: 21. Oktober 2026.

## Nachgewiesen

- GitHub-Konto jago1698 und privates Repository https://github.com/jago1698/projektmanagement-software vorhanden.
- Lokales Repository auf main; origin zeigt auf das private Repository.
- Lokale Commit-Identität mit GitHub-Namen und bestätigter noreply-Adresse eingerichtet.
- Erster Commit 46ba935 erstellt und erfolgreich nach origin/main hochgeladen; main verfolgt origin/main.
- Claude-Code-Sitzung „Projektordner Einrichtungsprüfung“ im Ordner C:\Users\jango\Documents\Projektmanagement-Software gestartet.
- Benutzer hat Workspace-Vertrauen selbst bestätigt.
- Claude hat die Projektunterlagen gelesen und alle sechs Unteragenten als tatsächlich aufrufbare Agententypen erkannt. Ein Probelauf der einzelnen Rollen ist noch nicht erfolgt.

## Reguläre Git Installation

Git for Windows wurde über winget (Paket Git.Git) installiert. Installer-Hashprüfung und Installation waren erfolgreich.

- Version: 2.55.0.windows.5, die zum Installationszeitpunkt von winget angebotene Version.
- Installationspfad: `C:\Program Files\Git\cmd\git.exe`.
- `C:\Program Files\Git\cmd` ist dauerhaft im Windows-Systemsuchpfad eingetragen.
- Mit dem aus den Windows-Einstellungen frisch geladenen Suchpfad löst `git` auf diese Installation auf; `git --version` funktioniert.
- Die neue Installation kann das Projekt öffnen; main war bei der Prüfung mit origin/main synchron.
- Claude nach Abschluss der Architekturaufgabe vollständig beendet und neu gestartet.
- Neue Claude-Sitzung „Git-Erkennung nach Neustart prüfen“ bestätigt: Git wird ohne vollständige Pfadangabe gefunden, Version 2.55.0.windows.5, Installationspfad C:\Program Files\Git\cmd\git.exe. Die Einrichtungslücke ist damit auch in Claude behoben.

Der zuvor genutzte Codex-interne Git-Pfad ist für die reguläre Entwicklung nicht mehr vorgesehen. Es wurden keine globalen Git-Autorenangaben geändert; die bestätigte Identität bleibt projektbezogen.

Claudes Einrichtungsbericht wurde teilweise vor dem ersten Commit erstellt. Seine Aussage „noch kein Commit“ ist inzwischen überholt. Das ist kein Fehler im Repository.

## Lokale Python-Umgebung (Freigabe des Benutzers vom 21.10.2026, docs/installationsliste-windows.md)

- **uv 0.13.4** per `winget install --id=astral-sh.uv -e --source winget` installiert. Paketquelle war nur `winget`; die Quelle `msstore` wurde nicht verwendet und ihre Vereinbarungen wurden nicht akzeptiert. Installationspfad: `C:\Users\jango\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe`, also nicht im virtualisierten Claude-Ordner. Für die Abhängigkeit `Microsoft.VCRedist.2015+.x64` wurde keine Installation gemeldet.
- **Python 3.13.16** per `uv python install 3.13` heruntergeladen. Danach meldete uv einen Fehler beim Anlegen der Verknüpfung für die Hauptversion. Ursache: Claude Desktop läuft als paketierte Windows-App, und Schreibzugriffe nach `%APPDATA%` landen virtualisiert in `C:\Users\jango\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\uv\python\`.
  - Innerhalb von Claude startet Python (`python.exe --version` meldet 3.13.16).
  - Außerhalb von Claude ist diese Installation voraussichtlich nicht sichtbar [ungeprüft]. Virtuelle Umgebungen würden auf diesen Pfad verweisen.
  - **Korrektur mit Zustimmung des Benutzers:**
    - Die virtualisierte Installation wurde per `uv python uninstall 3.13` entfernt.
    - Die Benutzer-Umgebungsvariable `UV_PYTHON_INSTALL_DIR=C:\Users\jango\.uv\python` ist dauerhaft gesetzt.
    - Python 3.13.16 wurde dort neu installiert, und die Startdatei `C:\Users\jango\.local\bin\python3.13.exe` wurde mit `--force` erneuert.
  - **Nachweis:**
    - `python.exe` meldet 3.13.16 (64 Bit, OpenSSL 3.5.9).
    - Die Module `ssl` und `sqlite3` lassen sich laden.
    - Die Verknüpfung `cpython-3.13-windows-x86_64-none` zeigt korrekt auf 3.13.16.
    - Im virtualisierten Claude-Ordner gibt es keine Kopie (`LocalCache\Local\.uv` fehlt).
    - Eine Prüfung aus einem normalen Windows-Terminal außerhalb von Claude steht noch aus.
  - `C:\Users\jango\.local\bin` ist bewusst **nicht** im Suchpfad. Das Projekt nutzt `uv run`, ein direkter `python`-Aufruf ist nicht nötig.
  - **Rückgängig machen:** `uv python uninstall 3.13`, dann die Umgebungsvariable `UV_PYTHON_INSTALL_DIR` in den Windows-Benutzereinstellungen entfernen.
  - **Merkpunkt für Werkzeuge, die Claude installiert:** Schreibzugriffe nach `%APPDATA%` und `%LOCALAPPDATA%` können virtualisiert werden. Installationsorte deshalb jedes Mal prüfen.
- **PostgreSQL 18.6**, vom Benutzer selbst mit dem EDB-Installer installiert; das Passwort für `postgres` hat nur der Benutzer. Prüfung durch Claude am 21.10.2026, nur lesend:
  - Der Dienst `postgresql-x64-18` läuft, Starttyp automatisch, Dienstkonto `NT AUTHORITY\NetworkService`, Datenordner `C:\Program Files\PostgreSQL\18\data`.
  - `pg_isready -h localhost -p 5432` meldet, dass Verbindungen angenommen werden.
  - `listen_addresses = '*'`: Der Port 5432 lauscht auf **allen** Netzwerkadressen (`0.0.0.0` und `::`).
  - `pg_hba.conf` erlaubt Anmeldungen nur von `127.0.0.1/32` und `::1/128`, jeweils mit `scram-sha-256`. Anfragen von anderen Rechnern werden abgewiesen.
  - Die Windows-Firewall ist in allen Profilen aktiv. Eine eingehende Freigabe für PostgreSQL oder Port 5432 wurde nicht gefunden. Die Abfrage per `Get-NetFirewallRule` war ohne Adminrechte unvollständig; `netsh` lieferte keinen Treffer.
  - **Bewertung:** Ein Zugriff von anderen Rechnern ist durch Firewall und `pg_hba.conf` doppelt blockiert.
  - **Zusätzliche Absicherung, vom Benutzer selbst ausgeführt (21.10.2026):** In einer Administrator-PowerShell hat er `psql -U postgres` geöffnet und dann ausgeführt:
    - `ALTER SYSTEM SET listen_addresses = 'localhost'`;
    - `CREATE ROLE projektx LOGIN CREATEDB` (ohne Superuser-Recht);
    - Passwort per `\password projektx`;
    - `CREATE DATABASE projektx_dev OWNER projektx`;
    - `Restart-Service postgresql-x64-18`.
    
    Alle Befehle meldeten Erfolg; ein Bildschirmfoto wurde nicht abgelegt.
  - **Nachprüfung durch Claude:**
    - Der Dienst läuft.
    - `postgresql.auto.conf` enthält `listen_addresses = 'localhost'`.
    - Port 5432 lauscht nur noch auf `127.0.0.1` und `::1`.
    - `pg_isready` meldet, dass Verbindungen angenommen werden.
  - `.env.example` (versioniert, nur Platzhalter) und `.env` (laut `git check-ignore` ignoriert) sind angelegt. Der Benutzer trägt `DB_PASSWORD` selbst ein.
  - **Anmeldetest am 21.10.2026 erfolgreich:** Claude hat sich mit den Werten aus `.env` als `projektx` an `projektx_dev` angemeldet. Das Passwort wurde über eine Umgebungsvariable übergeben, die danach gelöscht wurde; es wurde nicht angezeigt.
    - Ergebnis: `current_user=projektx`, `current_database=projektx_dev`, Superuser `f`, CREATEDB `t`, Server 18.6, Verbindung über `::1`.
    - Lokale Python- und Datenbankumgebung damit eingerichtet.

## Django-Grundgerüst (Freigabe des Benutzers vom 21.10.2026)

- Pakete nur in `.venv` des Projekts per `uv sync`: Django 5.2.18 (LTS), psycopg 3.3.6 (binary), waitress 3.0.2, python-dotenv 1.2.4; zum Entwickeln pytest 9.1.1, pytest-django 4.14.0, ruff 0.17.1. Versionen gesperrt in `uv.lock`. `.venv\pyvenv.cfg` verweist auf `C:\Users\jango\.uv\python\…`, also nicht auf den virtualisierten Claude-Ordner.
- Aufbau:
  - `pyproject.toml` und `manage.py` im Projektordner;
  - `src/config` mit den Einstellungen; alle umgebungsabhängigen Werte kommen aus `.env`;
  - `src/apps/core` mit dem Gesundheitsendpunkt `/health/`;
  - `src/apps/accounts` mit dem eigenen Benutzermodell `accounts.User`, von Anfang an angelegt;
  - `tests/`.
- `.env` wurde um `DJANGO_SECRET_KEY` (lokal zufällig erzeugt, nicht angezeigt), `DJANGO_DEBUG=1` und `DJANGO_ALLOWED_HOSTS` ergänzt. `.env.example` enthält dafür nur Platzhalter.
- **Nachweis am 21.10.2026:**
  - `manage.py migrate` hat alle Migrationen auf `projektx_dev` angewendet, einschließlich `accounts.0001_initial`.
  - `manage.py check` meldet keine Probleme; `makemigrations --check` meldet keine fehlenden Migrationen.
  - `pytest`: 6 Tests bestanden, gegen PostgreSQL. Geprüft werden der Gesundheitsendpunkt (Erfolg sowie Ausfall mit 503 ohne Fehlerdetails), nur GET, die Datenbank ist PostgreSQL, das Benutzermodell und das Speichern eines Benutzers.
  - Kurzreview durch reviewer: keine harten Fehler. Umgesetzt wurden weitere `.gitignore`-Einträge, eine Ablehnung von Platzhalter oder zu kurzem `DJANGO_SECRET_KEY`, ein Protokolleintrag bei Datenbankausfall im Gesundheitsendpunkt und ein Test für den 503-Fall. Offen sind die Sicherheitseinstellungen für den Betrieb (sichere Cookies, `CSRF_TRUSTED_ORIGINS`, Proxy-Header, HSTS), spätestens vor Demo oder Prod, und die Produktfrage, ob die E-Mail-Adresse eindeutig sein muss.
  - `ruff check` und `ruff format --check` sind sauber.
  - Über Waitress (`127.0.0.1:8001`) antwortet `/health/` mit HTTP 200 `{"status": "ok", "database": "ok"}`, eine unbekannte Adresse mit 404. Der Server wurde danach beendet.
- Noch nicht vorhanden: Anmeldung, Oberfläche, fachliche Module, CI.

## Noch offen

- Vier Architekturentwürfe sind lokal gespeichert und fachlich noch nicht freigegeben: entwurf-vorbereitung.md, entwurf-technik-und-betrieb.md, entwurf-datenmodell-und-rechte.md und entwurf-erster-entwicklungsabschnitt.md. Deren ursprüngliche Bestandsaufnahme entstand vor der Git-Installation und ist hinsichtlich Git überholt; maßgeblich ist dieser Einrichtungsstand.
- Tech-Stack, Architektur und Datenmodell abstimmen.
- Styleguide gemeinsam festlegen.
- Dev-/Prod-Trennung und Deployment-Pipeline konkretisieren und später umsetzen.
- Anwendung und Betriebsumgebungen sind noch nicht implementiert.
