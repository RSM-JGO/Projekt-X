# Installationsliste lokaler Windows-Arbeitsplatz (zur Freigabe)

Status: **vom Benutzer am 21.10.2026 freigegeben**. uv 0.13.4 und Python 3.13.16 sind installiert und nachgewiesen. PostgreSQL 18 installiert der Benutzer selbst; das steht noch aus. Stand: 21. Oktober 2026. Grundlage: `docs/entwurf-windows-betrieb.md`, Abschnitt 2.

Rechner: Windows 11 Home, Build 26200 (`docs/pruefung-entwicklungsrechner.md`). Bereits vorhanden und nachgewiesen: Git for Windows und Claude Desktop.

## Was installiert werden soll

| Nr. | Programm | Zweck | Herkunft | Adminrechte | Was sich am System ändert | Rückgängig machen |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **uv** (aktuelle Version) | Verwaltet Python-Version, virtuelle Umgebung und Paketversionen des Projekts | winget-Paket `astral-sh.uv` des Herstellers Astral [geprüft] | voraussichtlich nein [ungeprüft] | Programmdatei im Benutzerprofil, Eintrag im Suchpfad | `winget uninstall astral-sh.uv` |
| 2 | **Python 3.13** über uv | Laufzeit für Django | `uv python install 3.13` lädt den offiziellen Python-Build [geprüft für den Befehl] | nein (bestätigt) | Python-Ordner `C:\Users\jango\.uv\python` (Benutzer-Umgebungsvariable `UV_PYTHON_INSTALL_DIR`, gesetzt wegen der App-Virtualisierung von Claude Desktop, siehe `einrichtungsstand.md`). Der vorhandene Microsoft-Store-Platzhalter `python.exe` bleibt unverändert. | `uv python uninstall 3.13`, dann die Umgebungsvariable entfernen |
| 3 | **PostgreSQL 18** (Server und Kommandozeilenwerkzeuge) | Datenbank für Entwicklung und Tests | Windows-Installer von EDB, verlinkt auf postgresql.org/download/windows [geprüft] | **ja** | Windows-Dienst `postgresql-x64-18` mit automatischem Start, Datenordner, Port 5432; ggf. eine Firewall-Regel [ungeprüft] | Deinstallation über Windows-Einstellungen; Datenordner danach manuell löschen |

Bei PostgreSQL werden die Zusatzkomponenten **pgAdmin** und **Stack Builder** nicht ausgewählt. pgAdmin ist eine grafische Oberfläche und für Claude nicht nötig; Sie können sie später bei Wunsch nachinstallieren.

## Wichtig bei PostgreSQL

- **Sie führen den Installer selbst aus**, weil er ein Passwort für das Datenbank-Hauptkonto `postgres` verlangt. Claude gibt keine Passwörter ein. Bewahren Sie es in Ihrem Passwortmanager auf.
- Für die Anwendung legen wir anschließend ein **eigenes Entwicklungskonto** mit eigener Datenbank an. Dessen Testzugangsdaten stehen nur in der lokalen `.env` (nicht in Git).
- Nach der Installation prüft Claude, dass die Datenbank nur auf diesem Rechner erreichbar ist (`listen_addresses` und Firewall-Regel) [ungeprüft, wie der Installer das voreinstellt]. Bei Bedarf schlägt Claude eine Einschränkung auf `localhost` vor, die Sie vorher freigeben.

## Ablauf nach Ihrer Freigabe

1. Claude installiert **uv** per winget. Falls Windows nach Adminrechten fragt, bestätigen Sie das.
2. Claude installiert **Python 3.13** über uv.
3. **Sie** installieren PostgreSQL 18 mit dem Installer. Claude nennt Ihnen vorher den genauen Download-Link und die zu wählenden Optionen.
4. Claude weist die Funktion nach (`entwurf-windows-betrieb.md` Abschnitt 2, Schritte 1–5) und dokumentiert das Ergebnis in `docs/einrichtungsstand.md`.

Ein **Neustart** ist voraussichtlich nicht nötig [ungeprüft]. Falls doch, löst Claude ihn nicht selbst aus.

## Ausdrücklich nicht enthalten

- **Projektpakete** wie Django, Waitress und Testwerkzeuge. Sie werden nur in den Projektordner (`.venv`) installiert, nicht ins System. Die genaue Liste mit Versionen folgt beim Projektstart mit der Django-Versionsentscheidung (W-B) zur gesonderten Freigabe.
- **PDF-Werkzeuge** (MSYS2/Pango oder Playwright-Browser): erst für den PDF-Prototyp (W-C).
- **Tunnel- oder Demo-Software** für die externe Ansicht: erst mit der Entscheidung W-D und nach Prüfung des Anbieters.
- WSL, Docker, Linux-Container, IIS und Windows-Dienst-Wrapper.
