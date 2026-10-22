# Umzug auf einen neuen Rechner und ein neues GitHub-Konto

Stand 22.10.2026. Ziel: Projekt X mit **kompletter Git-Historie**, **Datenbanken** und **lokalen Einstellungen** auf einem neuen Windows-PC weiterführen. Dort wird mit **VS Code und GitHub Copilot (mit Claude)** gearbeitet, und es gibt ein **neues GitHub-Konto**.

## Was wohin gehört

| Inhalt | Wo heute | Weg zum neuen PC |
| --- | --- | --- |
| Code und Dokumente mit Historie | Git (lokal und altes GitHub-Konto) | Datei `projektx.bundle` im Umzugsordner, danach Upload ins neue Konto |
| Entwicklungsdatenbank `projektx_dev` (Beispieldaten und Projekt „Test“) | PostgreSQL lokal | `projektx_dev.dump` im Umzugsordner |
| Demo-Datenbank `projektx_demo` | PostgreSQL lokal | `projektx_demo.dump` im Umzugsordner |
| Lokale Einstellungen mit Passwörtern | `.env`, `.env.demo` (nicht in Git) | **Sie** kopieren beide Dateien selbst in den Umzugsordner. Ich kopiere keine Passwortdateien. |
| Rollout-Handbuch (Word) | Ihr Downloads-Ordner | selbst kopieren (gehört nicht in Git) |
| Demo-Tunnel (Microsoft Dev Tunnels) | am alten GitHub-Konto | auf dem neuen PC neu anlegen, die Adresse ändert sich |

Der Umzugsordner liegt auf dem alten PC unter `C:\Users\jango\Documents\ProjektX-Umzug`. Übertragen Sie ihn per USB-Stick oder privatem Speicher. Er enthält Passwörter; bitte **nicht** öffentlich teilen.

## Schritt 1 – Neues GitHub-Konto (Sie)

1. Neues Konto auf github.com anlegen und die Zwei-Faktor-Anmeldung einschalten.
2. **Neues leeres, privates Repository** anlegen, z. B. `projektmanagement-software`, **ohne** README, .gitignore oder Lizenz.
3. Die Adresse notieren, z. B. `https://github.com/NEUER-NAME/projektmanagement-software.git`.

## Schritt 2 – Programme auf dem neuen PC installieren (Sie, einmalig)

1. **Git for Windows** (git-scm.com).
2. **VS Code** mit den Erweiterungen **GitHub Copilot** und **Python**; in VS Code mit dem neuen GitHub-Konto anmelden.
3. **PostgreSQL 18** (EDB-Installer, Komponenten: Server und Command Line Tools). Ein eigenes `postgres`-Passwort vergeben.
4. **uv** in PowerShell: `winget install --id=astral-sh.uv -e --source winget`
5. Benutzer-Umgebungsvariable setzen, wie auf dem alten PC; das Demo-Skript erwartet sie: `[Environment]::SetEnvironmentVariable('UV_PYTHON_INSTALL_DIR', "$env:USERPROFILE\.uv\python", 'User')`. Danach ein **neues** PowerShell-Fenster öffnen.
6. Python 3.13: `uv python install 3.13`

## Schritt 3 – Projekt holen

Das Projekt liegt bereits mit kompletter Historie im neuen Repository https://github.com/RSM-JGO/Projekt-X (am 22.10.2026 vom alten PC hochgeladen). Auf dem neuen PC in PowerShell:

```powershell
cd $env:USERPROFILEDocuments
git clone https://github.com/RSM-JGO/Projekt-X.git Projektmanagement-Software
cd Projektmanagement-Software
git config user.name "RSM-JGO"
git config user.email "ID+RSM-JGO@users.noreply.github.com"
```

Die noreply-Adresse steht in GitHub unter Settings → Emails. Das Git-Paket `projektx.bundle` im Umzugsordner ist nur noch eine Reserve.

## Schritt 4 – Einstellungen und Datenbanken

1. `.env` und `.env.demo` aus dem Umzugsordner in den Projektordner kopieren.
2. In PowerShell bei der Datenbank anmelden: `& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -U postgres -h localhost`
3. Diese Befehle einzeln eingeben. Als Passwörter am einfachsten dieselben wie in `.env` (`DB_PASSWORD`) bzw. `.env.demo` verwenden, dann muss nichts angepasst werden:

```sql
ALTER SYSTEM SET listen_addresses = 'localhost';
CREATE ROLE projektx LOGIN CREATEDB;
\password projektx
CREATE DATABASE projektx_dev OWNER projektx;
CREATE ROLE projektx_demo LOGIN;
\password projektx_demo
CREATE DATABASE projektx_demo OWNER projektx_demo;
REVOKE CONNECT ON DATABASE projektx_dev FROM PUBLIC;
GRANT CONNECT ON DATABASE projektx_dev TO projektx;
REVOKE CONNECT ON DATABASE projektx_demo FROM PUBLIC;
\q
```

4. In einer **Administrator**-PowerShell den Datenbankdienst neu starten: `Restart-Service postgresql-x64-18`
5. Die Sicherungen einspielen. Bei jeder Zeile wird das jeweilige Datenbankpasswort abgefragt:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\pg_restore.exe' -h localhost -U projektx -d projektx_dev --no-owner ..\ProjektX-Umzug\projektx_dev.dump
& 'C:\Program Files\PostgreSQL\18\bin\pg_restore.exe' -h localhost -U projektx_demo -d projektx_demo --no-owner ..\ProjektX-Umzug\projektx_demo.dump
```

## Schritt 5 – Prüfen, ob alles läuft

```powershell
uv sync
uv run python manage.py migrate
uv run pytest
uv run python manage.py runserver
```

- `migrate` sollte „No migrations to apply“ melden.
- Die Tests sollten alle grün sein (Stand beim Umzug: 872).
- Unter http://127.0.0.1:8000 erscheint die Anmeldung. Beispielprojekte und Ihr Projekt „Test“ sind vorhanden.

## Schritt 6 – Demo wieder einrichten (optional)

1. `winget install --id Microsoft.devtunnel -e --source winget` und anschließend `devtunnel user login -g` mit dem **neuen** GitHub-Konto.
2. Einen neuen Tunnel anlegen: `devtunnel create projektx-demo-NEU --allow-anonymous --expiration 30d` und `devtunnel port create projektx-demo-NEU -p 8100 --protocol http`
3. In `.env.demo` drei Einträge anpassen:
   - `PX_TUNNEL_ID`: die Tunnel-ID;
   - `DJANGO_ALLOWED_HOSTS`: die neue Adresse `…-8100.<region>.devtunnels.ms`;
   - `CSRF_TRUSTED_ORIGINS`: `https://` plus die neue Adresse, dazu wie bisher `http://localhost:8100`.

   Die Adresse zeigt `scripts\demo.ps1 start` beim ersten Start in `run\demo-tunnel.log`.
4. Starten: `powershell -ExecutionPolicy Bypass -File scripts\demo.ps1 start`

## Schritt 7 – Mit Copilot weiterarbeiten

- Öffnen Sie in VS Code den Projektordner. Copilot liest `.github/copilot-instructions.md` und `AGENTS.md`, die beide auf `CLAUDE.md` verweisen.
- Die Rollen aus `.claude/agents/` sind in Copilot **keine** automatischen Unteragenten. Sie dienen als Leitfaden: Fragen Sie Copilot zum Beispiel „Arbeite als Reviewer nach `.claude/agents/reviewer.md`“.
- **Einstieg für den ersten Chat:** „Lies AGENTS.md, CLAUDE.md und docs/arbeitsstand.md und setze beim nächsten Schritt fort (Etappe 4b Steckbrief & Auftrag).“

## Danach auf dem alten PC (wenn alles läuft)

- Das alte GitHub-Repository bei Bedarf archivieren oder löschen. Erst danach, wenn der neue PC nachweislich funktioniert.
- Den alten Demo-Tunnel löschen: `devtunnel delete projektx-demo-jago.eun1`
- Den Umzugsordner nach erfolgreicher Übertragung löschen, weil er Passwörter enthält.
