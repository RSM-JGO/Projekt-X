# ENTWURF: Windows-Entwicklung und Windows-Betrieb (Revision 3)

Status: **Entwurf, nicht freigegeben**. Stand: 21. Oktober 2026.

**Grundlagen:**
- `docs/decisions/001-technische-grundrichtung.md`
- `docs/decisions/002-windows-server.md`
- `docs/entwurf-nacharbeit.md`

**Geltungsbereich:** Dieses Dokument ersetzt die Abschnitte A (lokale Entwicklung) und C (Prod-Prozess) von `entwurf-nacharbeit.md`. Ebenso ersetzt es alle Linux-, WSL-, Container-, Bash- und Digest-Annahmen der älteren Entwürfe. Die fachlichen Abschnitte B und D bis H von `entwurf-nacharbeit.md` gelten unverändert als Entwurf.

**Kennzeichnung:** **[geprüft]** heißt am 21.10.2026 in offizieller Dokumentation nachgesehen; die Quellen stehen am Ende. **[ungeprüft]** heißt Annahme, die vor der Festlegung zu prüfen ist.

## 1. Rahmen

**Zielbild, Präzisierung des Benutzers vom 21.10.2026:**

1. **MVP:** eine lokale Umgebung **und** eine Möglichkeit, dass andere Personen das MVP von außen ansehen können. Die Lösung dafür beschreibt Abschnitt 4a.
2. **Später:** Umzug auf eine Umgebung des Arbeitgebers, einen virtuellen Windows-Server (Entscheidung 002).

- Entwickelt und getestet wird **lokal auf Windows 11 Home**. Serverzugang, Serverversion und produktive Pipeline des Arbeitgebers sind keine Voraussetzung für den Start.
- Es gibt **keine** WSL, keine Linux-Container und kein Docker.
- Der Projektordner bleibt `C:\Users\jango\Documents\Projektmanagement-Software`. Claude Desktop und Git for Windows bleiben wie eingerichtet.
- **Grundsatz:** Lokal und auf dem Server laufen dieselben Bausteine: Python, Django, PostgreSQL und Waitress, jeweils nativ unter Windows. Dadurch bleiben Unterschiede zwischen Entwicklung und Betrieb klein, auch ohne Container.

## 2. Lokale Entwicklungsumgebung

| Baustein | Vorschlag | Begründung | Status |
| --- | --- | --- | --- |
| Python-Verwaltung | **uv**, installiert per `winget install --id=astral-sh.uv -e` | Ein Werkzeug für Python-Version, virtuelle Umgebung und gesperrte Paketversionen (`uv.lock`) | Installationsweg [geprüft]; Adminrechte [ungeprüft] |
| Python | Von uv verwaltet: `uv python install 3.13` | Keine systemweite Python-Installation. Der vorhandene Microsoft-Store-Platzhalter `python.exe` bleibt unberührt. Die Projektversion steht in `.python-version`. | Befehl [geprüft]; Python 3.12–3.14 passt zu Django 5.2 LTS und 6.1 [geprüft] |
| Django-Version | Entscheidung beim Projektstart, siehe Abschnitt 8 | Aktuell ist 6.1; 5.2 LTS erhält Sicherheitsupdates bis April 2028 | offen |
| Datenbank | **PostgreSQL 18** über den EDB-Windows-Installer als lokaler Windows-Dienst, nur auf `localhost` erreichbar | Gleiche Datenbank wie später auf dem Server. Auch Tests laufen gegen PostgreSQL. | Installer für Version 13 bis 18 [geprüft]; offiziell auf Windows Server getestet, Desktop-Windows „in der Regel lauffähig“ [geprüft]; Windows 11 Home [ungeprüft] |
| Anwendungsserver lokal | Django-Entwicklungsserver (`runserver`); zusätzlich ein Probelauf mit **Waitress** | Waitress läuft unter Windows [geprüft] und soll später auch der Produktionsserver sein | — |
| Befehle | `uv run python manage.py …`, gebündelt in einem PowerShell-Skript `scripts\dev.ps1` | `make` ist unter Windows nicht vorhanden; PowerShell ist es | — |
| Geheimnisse | `.env` im Projektordner, in `.gitignore`; nur `.env.example` mit Platzhaltern in Git | wie bisher | — |
| E-Mail lokal | nur Protokoll (Konsolen-Backend von Django) | lokal wird nichts versendet | — |

**Datenbankkonten:**
- Die Anwendung nutzt eine eigene Rolle **ohne** Superuser-Recht, mit `CREATEDB`, damit Tests ihre Testdatenbank anlegen können.
- Das Superuser-Passwort setzt der Benutzer selbst bei der Installation; es kommt nie in Git.
- Der EDB-Installer braucht Adminrechte.
- `listen_addresses` und `pg_hba.conf` werden nach der Installation auf reinen `localhost`-Zugriff geprüft. Der Installer setzt `listen_addresses` möglicherweise standardmäßig auf `*` [ungeprüft].

**Alternative für die Datenbank:** PostgreSQL als ZIP-Archiv ohne Dienst und ohne Adminrechte, manuell gestartet [ungeprüft]. Das ändert weniger am System, ist aber im Alltag umständlicher. Sie kommt nur in Frage, falls der Installer auf Windows 11 Home Probleme macht.

**Nachweis der Einrichtung** (Entscheidung 001: eine Installation allein ist kein Nachweis):

1. `uv --version` und `uv run python --version` liefern die erwarteten Versionen.
2. Der PostgreSQL-Dienst läuft, und ein Verbindungstest mit der Anwendungsrolle auf eine eigene Entwicklungsdatenbank gelingt. Die Datenbank ist nur über `localhost` erreichbar.
3. Ein minimales Django-Projekt startet, führt Migrationen gegen PostgreSQL aus und beantwortet eine Testanfrage.
4. Ein automatischer Test läuft gegen PostgreSQL.
5. Derselbe Start funktioniert über Waitress.

## 3. PDF-Erzeugung unter Windows

Die PDF-Erzeugung wird erst mit Statusbericht und Dokumenten gebraucht, nicht im ersten Abschnitt (V07a/b). **Sie wird deshalb jetzt nicht installiert.** Die Entscheidung fällt über einen kleinen Technikprototyp mit einer Beispielseite (Kopf- und Fußzeile, Seitenzahlen, Tabelle über mehrere Seiten, Pastellfarben).

| Option | Funktionsweise | Vorteil | Nachteil |
| --- | --- | --- | --- |
| **W1 WeasyPrint als Python-Bibliothek** | Bibliothek plus Pango über **MSYS2** (`pacman -S mingw-w64-ucrt-x86_64-pango`) [geprüft] | Sehr gute Druckregeln (Seitenzahlen, Umbrüche), reines HTML/CSS | Zusätzliche MSYS2-Umgebung auf Arbeitsplatz und Server; Pfad zu den Programmbibliotheken muss stimmen |
| W2 WeasyPrint als eigenständige EXE | Die Anwendung ruft das Programm auf | Kein MSYS2 | Die Hersteller-Doku warnt vor regelmäßigen Fehlalarmen von Virenscannern [geprüft]. Für einen beruflichen Server ungünstig. |
| **W3 Headless Chromium über Playwright** | Die Anwendung druckt die HTML-Seite mit einem mitgelieferten Browser in ein PDF [ungeprüft] | Native Windows-Unterstützung, sehr genaue Darstellung | Großer Browser-Download; Druckregeln wie Seitenzahlen nur eingeschränkt; Browserprozess auf dem Server |

**Vorschlag:** W1 und W3 im Prototyp vergleichen, W2 nicht weiter verfolgen. Abnahmekriterium ist auch ein Lauf **unter Waitress als nicht interaktives Dienstkonto**, denn genau dort scheitern typischerweise der MSYS2-DLL-Pfad (W1) und Chromium (W3). Außerdem müssen die Schriften ins PDF eingebettet sein. Bewertet werden Druckbild, Einrichtungsaufwand, Verhalten auf dem späteren Server und Updatepflege. Unabhängig von der Wahl gilt: Veröffentlichte PDFs werden als Datei mit Prüfsumme gespeichert und später nicht neu erzeugt. Ein veröffentlichter Berichtsstand bleibt dadurch unverändert.

## 4a. Externe Ansicht des MVP (Demo)

**Zweck:** Ausgewählte Personen sehen sich den Zwischenstand an und geben Rückmeldung. Das ist **kein** produktiver Betrieb.

**Feste Regeln für jede Variante:**
- Eine **eigene Demo-Instanz** mit eigener Datenbank, eigenem Dateiordner und eigener Konfiguration. Sie ist weder die Entwicklungsdatenbank noch später Prod.
- Ausschließlich gekennzeichnete **Beispieldaten**. Keine echten Projekt- oder Firmendaten und keine echten Uploads.
- Anmeldung ist Pflicht, mit eigenen Demo-Konten; es gibt keine öffentlich lesbaren Seiten.
- Kein echter Mailversand, nur Protokoll.
- Läuft über Waitress, nicht über den Django-Entwicklungsserver. `DEBUG` ist aus, die Geheimnisse sind eigene.
- Die Demo bekommt nur ein freigegebenes Release-Paket nach Abschnitt 5, keinen beliebigen Arbeitsstand.
- Bei D1 auf dem Entwicklungs-PC gilt zusätzlich: eigener Datenbankbenutzer, eigener Port und eigenes Dienstkonto [ungeprüft für Windows 11 Home]; der Tunnel zeigt nur auf diesen Port.
- Demo-Daten gelangen nie nach Dev oder Prod.
- **Netz:** Waitress lauscht nur an `127.0.0.1` auf dem Demo-Port. `ALLOWED_HOSTS` und `CSRF_TRUSTED_ORIGINS` stehen auf der Tunneladresse. Proxy-Einstellungen (`trusted_proxy` in Waitress, `SECURE_PROXY_SSL_HEADER` in Django) und Secure-Cookies sind gesetzt.
- **Datenbank:** Die Demo hat eine eigene Datenbankrolle ohne Rechte auf die Entwicklungsdatenbank. Das ist nötig, weil beide auf demselben PostgreSQL laufen.

**Nachweis vor jeder Freigabe nach außen:**
1. `manage.py check --deploy` meldet keine Warnungen.
2. Anonyme Aufrufe aller Seiten und Dateipfade werden zur Anmeldung umgeleitet.
3. `/admin` ist nicht erreichbar.
4. Demo-Konten haben keine Administratorrechte und starke Passwörter. Fehlversuche bei der Anmeldung werden begrenzt.
5. Optional ist zusätzlich eine Zugriffsregel beim Tunnelanbieter eingerichtet.
- Eine Freigabe nach außen erfolgt erst nach ausdrücklicher Zustimmung des Benutzers zum konkreten Dienst (CLAUDE.md: externe Dienste und Veröffentlichung vorher abstimmen).

| Variante | Funktionsweise | Vorteil | Nachteil | Kosten |
| --- | --- | --- | --- | --- |
| **D1 Tunnel vom eigenen PC** (z. B. Cloudflare Tunnel, Tailscale Funnel oder ngrok [alle ungeprüft]) | Ein kleines Programm auf dem PC stellt eine ausgehende Verbindung her; der Anbieter vergibt eine HTTPS-Adresse | Kein Server nötig, sofort möglich, keine Portfreigabe am Router | Nur erreichbar, solange der PC läuft; der Datenverkehr läuft über den Anbieter; ein Programm wird zusätzlich installiert | meist Freikontingent [ungeprüft] |
| D2 Privates Netz nur für Eingeladene (z. B. Tailscale-Einladung [ungeprüft]) | Gäste installieren selbst eine App und treten dem privaten Netz bei | Nicht öffentlich im Internet | Gäste müssen Software installieren; für Firmenrechner oft nicht erlaubt | meist Freikontingent [ungeprüft] |
| D3 Kleiner gemieteter Windows-Server für die Demo | Die Demo läuft dauerhaft auf einem eigenen virtuellen Windows-Server | Immer erreichbar; gleichzeitig Generalprobe für den späteren Arbeitgeber-Server | Windows-Lizenz macht Server teurer als Linux; Einrichtung und Pflege | grob 15–40 €/Monat [ungeprüft] |

**Vorschlag:** Für die ersten Vorführungen **D1**, weil es ohne Server und mit wenig Aufwand möglich ist. Sobald Gäste unabhängig vom eigenen PC zugreifen sollen, folgt **D3**. Dann übt die Demo zugleich den Windows-Server-Betrieb (Abschnitte 4 und 5) und erleichtert den späteren Umzug. Anbieter und Kosten werden vor einer Entscheidung geprüft; es wird nichts gebucht.

## 4. Betrieb auf dem Windows-Server des Arbeitgebers (Ausblick, nicht blockierend)

Die genaue Windows-Server-Version ist unbekannt. Die folgenden Punkte sind Vorschläge, die mit dem späteren Server und gegebenenfalls der beruflichen IT abzustimmen sind.

| Thema | Vorschlag | Offen |
| --- | --- | --- |
| Webserver | Waitress als Anwendungsserver. Davor eine Schicht für HTTPS, weil Waitress kein TLS beherrscht [geprüft]: **IIS** mit Weiterleitung (ARR/URL Rewrite) [ungeprüft] oder Caddy für Windows [ungeprüft]. Statische Dateien über WhiteNoise oder IIS. | IIS ist im Firmenumfeld meist üblich und passt zu vorhandenen Zertifikaten; Entscheidung mit der IT |
| Dienste | Waitress und Scheduler laufen je als **Windows-Dienst** über einen Dienst-Wrapper (z. B. WinSW oder NSSM [ungeprüft]): automatischer Start, Neustart bei Absturz, Protokolldateien. | Wahl des Wrappers |
| Dienstkonten | Jede Instanz (Dev, Prod) bekommt ein eigenes, nicht interaktives Dienstkonto mit Rechten nur auf die eigenen Ordner und die eigene Datenbank. | Lokale virtuelle Konten oder Domänenkonten, abhängig von der IT |
| Hintergrundjobs | Bisheriges Prinzip: ein eigener Scheduler-Dienst (`manage.py run_scheduler`) mit Datenbanksperre. Alternative: die **Windows-Aufgabenplanung** ruft täglich einen Django-Befehl auf. `ReminderDelivery` in der Datenbank verhindert in beiden Fällen, dass mehrere Läufe dieselbe Sammelmail erzeugen. Unklare Zustellungen bleiben möglich und werden sichtbar gemacht (`entwurf-nacharbeit.md`, Abschnitt G). Die Aufgabenplanung darf keinen parallelen Start zulassen. | Dienst oder Aufgabenplanung; ob ein ausgefallener Lauf, etwa durch einen Serverneustart, nachgeholt wird; Zeitzone des „Tages“ (Vorschlag: persönliche Zeitzone, Standard Europe/Berlin) |
| Dateiablage | Eigener NTFS-Ordner je Instanz **außerhalb** des Webverzeichnisses, nur für das Dienstkonto beschreibbar. Download ausschließlich über Django mit Rechteprüfung. | Laufwerk und Kontingent |
| Konfiguration und Geheimnisse | Je Instanz eine Konfigurationsdatei außerhalb des Programmordners, mit Lese-ACL nur für das Dienstkonto, oder Dienst-Umgebungsvariablen [ungeprüft]. Nichts davon kommt in Git. | — |
| E-Mail | Dev: Mail-Fänger oder nur Protokoll; Prod: SMTP des späteren Anbieters bzw. der Firma. Mail-Modus und Empfänger-Positivliste wie bisher vorgeschlagen. | Mail-Fänger unter Windows [ungeprüft] |
| Sicherung | `pg_dump` der Datenbank, Kopie des Dateiordners und der Konfiguration (ohne Klartext-Geheimnisse) auf ein externes Ziel, täglich und vor jedem Prod-Update. Wiederherstellungsprobe in einer getrennten Instanz ohne Mailversand. | Ziel, Verschlüsselungswerkzeug, Zielwerte; ggf. Vorgaben der Firmen-IT |
| Dev und Prod | Zwei Server oder zwei getrennte Instanzen auf einem Server. Getrennt sind in jedem Fall Datenbank, Ordner, Dienstkonto, Konfiguration, Port und Website. | laut Entscheidung 002 offen |

## 5. Pipeline und Releases unter Windows

Container-Digests entfallen. An ihre Stelle tritt ein **versioniertes Release-Paket**.

1. **CI (GitHub Actions)** läuft auf **Windows-Runnern**, damit dieselbe Plattform getestet wird. Sie prüft Code, führt Tests gegen PostgreSQL aus und prüft auf fehlende Migrationen. Ob PostgreSQL auf dem Runner vorinstalliert ist oder im Workflow eingerichtet werden muss, ist [ungeprüft]. Kosten: GitHub Free bietet 2.000 Minuten pro Monat für private Repositories; Windows-Minuten sind teurer bepreist als Linux-Minuten [geprüft]. Ob das Kontingent reicht, ist [ungeprüft].
2. **Release-Paket:** Auf `main` erzeugt CI eine ZIP-Datei mit Anwendungscode, gesammelten statischen Dateien, Versionsangabe (Version, Commit) und **allen Python-Abhängigkeiten als fertige Windows-Pakete (Wheels) gemäß `uv.lock`**. Dazu kommt eine **SHA-256-Prüfsumme**. Der Server installiert daraus offline und lädt beim Bereitstellen nichts aus dem Internet nach [ungeprüft für alle Pakete].
   - Benötigte Systembestandteile außerhalb des Pakets werden im Release-Nachweis mit Version benannt und auf Dev und Prod abgeglichen: Python-Version, PostgreSQL-Hauptversion und gegebenenfalls das PDF-Werkzeug.
   - Ablage als GitHub-Release-Anhang [ungeprüft für Größe und Aufbewahrung].
   - Die Prüfsumme übernimmt die Rolle des früheren Digests. Dev, Demo und Prod erhalten **dasselbe ZIP**; es wird nie neu gebaut.
   - Prod und Demo nehmen nur ein Paket an, dessen Prüfsumme auf Dev **als geprüft vermerkt** ist. Der Vermerk steht im Release-Nachweis; bei getrennten Servern wird er als signierte oder geschützt abgelegte Liste übertragen [Mechanismus offen].
   - Die Zuordnung Tag → Commit → Prüfsumme wird festgehalten.
3. **Bereitstellung durch ein PowerShell-Skript** auf dem Server, je Instanz. Es behält die bereits geprüften Regeln aus `entwurf-nacharbeit.md` Abschnitt C:
   - Sperre gegen Doppelstart;
   - strenge Formatprüfung der Eingabe und Prüfsummenkontrolle gegen den Dev-Prüfvermerk;
   - Sicherung von Datenbank und Dateien vor der Migration, Abbruch bei fehlgeschlagener Sicherung;
   - Dienst stoppen, Paket in einen neuen Versionsordner entpacken, Abhängigkeiten offline aus dem Paket installieren, Migration ausführen, Dienst starten;
   - Gesundheitsprüfung, danach ein Protokoll mit Prüfsumme, Zeitpunkt und Ergebnis, das in den Release-Nachweis übernommen wird.

   Die Gesundheitsprüfung ersetzt **nicht** die fachliche Nachprüfung. Konfigurationsunterschiede zwischen den Instanzen werden je Release benannt. Der vorherige Versionsordner bleibt erhalten. Ein **Rückfall** läuft über dasselbe Skript mit Prüfsummenkontrolle, solange das Schema verträglich ist.
4. **Auslösen der Prod-Bereitstellung:** Der Benutzer soll keine regelmäßigen Serverbefehle eingeben.
   - **P2 (Abholung):** Eine geplante Aufgabe auf dem Server fragt nach freigegebenen Releases und holt sie ab. Das ist im Windows-Firmenumfeld voraussichtlich günstiger, weil GitHub dafür keine eingehende Verbindung zum Server braucht. Voraussetzungen:
     - ausgehender Zugriff des Servers auf GitHub [ungeprüft, Firmennetz];
     - ein eigenes Lesetoken;
     - Zwei-Faktor-Schutz für das GitHub-Konto und Branchschutz für `main`;
     - eine sichtbare Rückmeldung des Ergebnisses, etwa Status-Mail oder Statusseite [offen].
   - **P1 (Auslösung aus GitHub):** Ein in GitHub gestarteter Workflow würde einen eingehenden Zugang brauchen, etwa OpenSSH-Server für Windows mit festem Befehl oder WinRM [ungeprüft].
   - Die frühere Empfehlung P1 stammte aus dem Linux-Szenario. Sie wird hier **vorläufig zu P2 umgekehrt** und bei Kenntnis des Servers und der Netzregeln endgültig entschieden.
   - Beide Varianten sind ein manueller Start, keine abgesicherte Freigabestufe. Die Benutzerfreigabe wird gesondert im Release-Nachweis dokumentiert (`docs/releaseprozess.md`).
5. **Migrationen und Rückfall** unverändert: nur vorwärts und in zwei Schritten. Ein Rückfall auf den vorherigen Versionsordner ist möglich, solange das Schema verträglich ist. Eine Datenwiederherstellung bleibt ein gesonderter Notfallschritt.

## 6. Was aus den älteren Entwürfen entfällt

- Dockerfile, `compose.yaml` und `deploy/compose.*.yaml`, GHCR und Image-Digests, der Linux-Zeitgeber für den Dev-Pull, das Bash-Skript `deploy-prod`, Caddy als feste Wahl, das Makefile sowie die Pfade `/…`.
- Die Befehlstabelle im Entwurf zum ersten Abschnitt: An die Stelle von `docker compose run --rm web …` tritt `uv run python manage.py …`.
- Die geplante Ordnerstruktur bleibt grundsätzlich gültig. `deploy/` enthält stattdessen PowerShell-Skripte und Beispielkonfigurationen für Windows-Dienste.

## 7. Risiken

- **PostgreSQL auf Windows 11 Home** ist laut Hersteller nicht offiziell getestet. Das wird durch den Nachweis in Abschnitt 2 abgedeckt.
- Die **PDF-Erzeugung** ist unter Windows die größte Unbekannte. Der Prototyp in Abschnitt 3 klärt sie vor der Umsetzung der Berichte.
- **Unterschiede zwischen Windows 11 und Windows Server** (Dienste, Rechte, IIS) werden lokal nicht vollständig abgebildet. Eine Probeinstallation auf einer Dev-Instanz ist vor dem ersten Prod-Release nötig.
- **Firmenvorgaben** zu Virenscanner, Zertifikaten, Konten und Netz können Vorschläge in Abschnitt 4 und 5 ändern.

## 8. Entscheidungen

| Nr. | Entscheidung | Vorschlag | Wann |
| --- | --- | --- | --- |
| W-A | Lokale Installation | uv, von uv verwaltetes Python 3.13 und PostgreSQL 18; siehe `docs/installationsliste-windows.md` | jetzt, Freigabe durch den Benutzer |
| W-B | Django-Version | 5.2 LTS (längste Sicherheitsunterstützung bis April 2028) oder 6.1 (aktuell); entscheiden nach einem Kompatibilitätstest der Zusatzpakete beim Projektstart | beim Projektstart |
| W-C | PDF-Verfahren | W1 oder W3 nach dem Prototyp | vor den Berichten |
| W-D | Externe Demo-Ansicht | D1 Tunnel für die ersten Vorführungen, später D3; Anbieter vor der Wahl prüfen | sobald es etwas zu zeigen gibt (nach V06 bzw. V07b) |
| W-E | Webserver, Dienste und Auslösung der Bereitstellung | Abschnitte 4 und 5 | mit dem Server des Arbeitgebers |

## Quellen der geprüften Aussagen (21.10.2026)

| Aussage | Quelle |
| --- | --- |
| uv per winget `astral-sh.uv`; `uv python install <Version>` | docs.astral.sh/uv (Installation, Install Python) |
| Django 6.1 unterstützt Python 3.12–3.15; 5.2 LTS Python 3.10–3.14 | docs.djangoproject.com (FAQ Installation), bereits in `entwurf-vorbereitung.md` |
| PostgreSQL 13–18 per EDB-Installer, getestet auf Windows Server 2016–2025, Desktop-Windows „in der Regel lauffähig“ | postgresql.org/download/windows |
| Waitress 3.0.2 läuft unter Windows, ohne eigenes TLS | docs.pylonsproject.org/projects/waitress |
| WeasyPrint 70.0 unter Windows: MSYS2/Pango ≥ 1.44 oder eigenständige EXE mit Virenscanner-Warnung | doc.courtbouillon.org/weasyprint (First steps) |
| GitHub Free: 2.000 Actions-Minuten privat; Windows-Runner teurer bepreist | docs.github.com (Billing GitHub Actions) |
