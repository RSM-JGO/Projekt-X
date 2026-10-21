# Auftrag: Externe Demo-Ansicht (Etappe 3)

Status: Vom Benutzer am 21.10.2026 beauftragt (Microsoft Dev Tunnels, whitenoise, eigene Demo-Datenbank). **Umgesetzt, von außen geprüft und vom Benutzer am 21.10.2026 abgenommen.** Enthält zusätzlich F16 Versionsanzeige. Stand: 21. Oktober 2026. Grundlage: `docs/entwurf-windows-betrieb.md` Abschnitt 4a, Zielbild des Benutzers „MVP lokal **und** von außen ansehbar“.

## Ziel

Ausgewählte Personen können Projekt X von außen ansehen und ausprobieren. Sie melden sich mit Demo-Konten an und sehen ausschließlich Beispieldaten. Das ist **kein** produktiver Betrieb. Die Demo läuft nur, solange der PC des Benutzers läuft.

## Umfang

1. **Eigene Demo-Instanz** auf dem PC, getrennt von der Entwicklung:
   - eigene Datenbank `projektx_demo` mit eigener Rolle `projektx_demo`; der Benutzer legt beides selbst an, wie zuvor bei `projektx`;
   - eigene Konfigurationsdatei `.env.demo`, nicht in Git;
   - eigener Geheimschlüssel und eigenes Demo-Passwort;
   - eigener Port 8100, nur an `127.0.0.1`.
2. **Betriebseinstellungen:**
   - `DEBUG` aus;
   - sichere Cookies, `CSRF_TRUSTED_ORIGINS` und `ALLOWED_HOSTS` auf die Tunneladresse;
   - Proxy-Header für HTTPS;
   - `/admin` in der Demo abgeschaltet;
   - kein Mailversand.
3. **Statische Dateien** (Gestaltung, Logo) über Waitress ausliefern. Dafür ist ein neues Paket nötig: **`whitenoise`**, gesonderte Freigabe.
4. **Beispieldaten in der Demo:** `seed_demo` wird für eine ausdrücklich als Demo gekennzeichnete Instanz erlaubt. In Dev oder späterem Prod bleibt es gesperrt.
5. **Start und Stopp per Skript:** `scripts\demo.ps1` startet Waitress und Tunnel und beendet beide zusammen.
6. **Tunnel** zum Internet, gemäß der Auswahl unten. Er wird nur nach Freigabe des Benutzers installiert.

## Tunnel-Auswahl (Entscheidung des Benutzers nötig)

| Option | Anmeldung | Adresse | Bewertung |
| --- | --- | --- | --- |
| **Microsoft Dev Tunnels** (`devtunnel`) | Microsoft- oder GitHub-Konto; der Benutzer meldet sich selbst an | Dauerhafte Tunnel-ID möglich, Adresse bleibt gleich | Läuft unter Windows. Anonymer Zugriff lässt sich zeitlich begrenzen (1 Stunde bis 30 Tage). Firmen können ihn per Gruppenrichtlinie sperren, das ist für später beim Arbeitgeber relevant. Kostenlose Limits geprüft: 5 GB Datenverkehr pro Monat, 10 Tunnel, 1500 Anfragen pro Minute und Port ([Limits](https://learn.microsoft.com/azure/azure-resource-manager/management/azure-subscription-service-limits#dev-tunnels-limits)). Lizenzbedingungen werden beim ersten Anmelden angezeigt und vom Benutzer selbst bestätigt. |
| Cloudflare Quick Tunnel (`cloudflared`) | kein Konto | Zufällige `trycloudflare.com`-Adresse, bei jedem Start neu | Am schnellsten. Laut Anbieter nur zum Testen, ohne Verfügbarkeitszusage. Eine feste Adresse braucht ein Konto und eine eigene Domain. |
| Tailscale Funnel | Tailscale-Konto | Feste `…ts.net`-Adresse | Kostenloser Personal-Tarif. Nur die Ports 443, 8443 und 10000; Bandbreite begrenzt. |

**Empfehlung:** **Microsoft Dev Tunnels**. Die Adresse bleibt gleich, die Anmeldung läuft über Ihr GitHub-Konto, und es passt zur Windows-Umgebung. Die Limits des kostenlosen Angebots prüfe ich vor der Installation.

Quellen:
- [Microsoft Dev Tunnels FAQ](https://learn.microsoft.com/azure/developer/dev-tunnels/faq)
- [Dev Tunnels CLI](https://learn.microsoft.com/azure/developer/dev-tunnels/cli-commands)
- [Dev Tunnels Policies](https://learn.microsoft.com/azure/developer/dev-tunnels/policies)
- [Tailscale Funnel](https://tailscale.com/kb/1223/funnel)
- Cloudflare Quick Tunnels, nur über Drittquellen geprüft: [Leitfaden](https://flaviocopes.com/cloudflare-tunnel/), [Quick-Tunnel-Anleitung](https://stackharbor.com/en/knowledge-base/cf-quick-tunnel-trycloudflare-guide/)

## Abnahmekriterien

1. Die Demo hat eine eigene Datenbank und Konfiguration. Die Entwicklungsdaten bleiben unverändert und sind aus der Demo nicht erreichbar, weil die Demo-Rolle keine Rechte auf `projektx_dev` hat.
2. `manage.py check --deploy` meldet für die Demo-Konfiguration keine Warnungen. Begründete Ausnahmen werden dokumentiert.
3. Über die Tunneladresse:
   - Jede Seite und jede Datei verlangt die Anmeldung;
   - `/admin` ist nicht erreichbar;
   - Gestaltung und Logo werden angezeigt;
   - Anmeldung, Projekte und Aufgaben funktionieren.
4. Fehlversuche bei der Anmeldung werden auch über den Tunnel begrenzt. Gesperrt wird die echte Besucher-IP, nicht pauschal der Tunnel.
5. Demo-Konten haben keine Administratorrechte, außer einem ausdrücklich benannten Vorführkonto, falls gewünscht.
6. Start und Stopp erfolgen mit je einem Befehl. Nach dem Stopp ist von außen nichts mehr erreichbar.
7. *(F16)* Jede angemeldete Seite und `/health/` zeigen Version, Commit und Umgebung, also „demo“. Uncommittete Änderungen sind als „geändert“ erkennbar.
8. Alle bisherigen Tests bleiben grün, und neue Tests decken die Demo-Einstellungen ab.

## Nicht enthalten

Dauerbetrieb, gemieteter Server, eigene Domain, echte Daten und E-Mail-Versand.

## Prüfnachweis (21.10.2026)

- **Tunnel:** `projektx-demo-jago.eun1`, angelegt mit dem GitHub-Konto des Benutzers, anonymer Zugriff erlaubt, Ablauf 30 Tage nach der letzten Nutzung.
- **Öffentliche Adresse:** https://vflm0d5d-8100.eun1.devtunnels.ms. Beim ersten Aufruf zeigt Microsoft eine Warnseite „Weiter“.
- **Gefundene und behobene Ursachen:**
  - Dev Tunnels reicht als Host `localhost:8100` weiter, die öffentliche Adresse kommt in `X-Forwarded-Host`. Behoben mit `USE_X_FORWARDED_HOST` hinter dem Proxy.
  - Waitress verwirft Forwarded-Header ohne vertrauenswürdigen Proxy, das führte zu einer Weiterleitungsschleife. Behoben: Waitress vertraut nur `127.0.0.1` als Proxy, also dem lokalen Tunnel.
- **Tatsächlich gesendete Header**, mit einem Echo-Server geprüft: `X-Forwarded-Proto=https`, `X-Forwarded-Host`, `X-Forwarded-For` und `X-Real-IP` mit der echten Besucher-IP.
- **Von außen geprüft:**
  - `/health/` antwortet mit 200 (version 0.1.0, instance demo).
  - Anonyme Aufrufe von `/projekte/` und `/arbeitsplatz/` landen auf `/anmelden/` und zeigen keine Projektdaten.
  - `/admin/` liefert 404, auch angemeldet.
  - CSS, JS und Logo werden ausgeliefert (200).
  - Die Anmeldung als Beispielkonto funktioniert, `/projekte/` liefert 200, der Fußbereich zeigt „Projekt X 0.1.0 · 2f9337e (geändert) · demo“.
  - Die Cookies `sessionid` und `csrftoken` sind `Secure`, `sessionid` ist außerdem `HttpOnly`.
  - Ein Fehlversuch wird mit der echten Besucher-IP erfasst, nicht mit 127.0.0.1. Die Sperren wurden danach zurückgesetzt.
- **Lokal geprüft:**
  - `check --deploy` ohne Befund, eine begründete Ausnahme W021.
  - Die Demo-Rolle hat keinen Zugriff auf `projektx_dev`.
  - Tests: 508 grün.
- **Nicht geprüft:** Darstellung im Browser über den Tunnel (der eingebaute Browser durfte die Adresse nicht öffnen), Mobilansicht über den Tunnel, Dauerbetrieb.
- **Nachtrag nach dem Browsertest des Benutzers:** Die Anmeldung im Browser schlug zunächst mit CSRF 403 fehl.
  - **Ursache:** Dev Tunnels schreibt den `Origin`-Header des Browsers auf `http://localhost:8100` um, auch mit `--origin-header unchanged`. Das Protokoll zeigte: „Origin checking failed - http://localhost:8100“.
  - **Lösung:** `http://localhost:8100` steht zusätzlich in `CSRF_TRUSTED_ORIGINS` der Demo.
  - **Bewertung:** Weil der Tunnel jede Herkunft umschreibt, ist die Herkunftsprüfung hinter diesem Tunnel ohnehin nicht aussagekräftig. Der eigentliche CSRF-Schutz bleibt wirksam: Token im Formular und Cookie, dazu SameSite=Lax.
  - Für einen späteren Serverbetrieb ohne Tunnel ist das nicht übernehmen.
  - **Nachweis:** Eine Anmeldung wie im Browser, mit `Origin` und `Referer`, führt jetzt auf `/projekte/` (200).
