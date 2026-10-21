# ENTWURF: Technik, Umgebungen und Deployment

Status: **Entwurf, nicht beschlossen**. Stand: 21. Oktober 2026. Übersicht und Entscheidungsvorlage: `docs/entwurf-vorbereitung.md`.

> **Hinweis Nacharbeit (21. Oktober 2026):** Ursprünglicher Vorschlag, teilweise überholt. Maßgeblich bei Widersprüchen ist `docs/entwurf-nacharbeit.md` (Revision 2, ebenfalls Entwurf, nicht freigegeben).
Kennzeichnung: **[geprüft]** = am 21.10.2026 in offizieller Dokumentation nachgesehen (Quellen im Prüfprotokoll der Übersicht); **[ungeprüft]** = Annahme, vor Festlegung prüfen.

## 1. Technologievorschlag

| Bereich | Vorschlag | Begründung in einfachen Worten |
| --- | --- | --- |
| Sprache und Framework | Python mit **Django 5.2 LTS** [geprüft], Upgrade auf **6.2 LTS** im Jahr 2027 einplanen | Django bringt Anmeldung, Sitzungen, Schutz gegen gefälschte Formularabsendungen (CSRF), Formulare, Datenbankmigrationen und eine Verwaltungsoberfläche mit. Weniger Einzelteile bedeuten weniger Wartung. Claude kennt Django sehr gut. |
| Oberfläche | Seiten werden auf dem Server aus HTML-Vorlagen erzeugt; eigenes CSS mit Variablen für Farben, Schrift, Abstände; punktuell **htmx 2.x** [geprüft: 2.0.11] für Teilaktualisierungen ohne Neuladen | Du kannst HTML und CSS direkt lesen. Der noch offene Styleguide lässt sich später über die CSS-Variablen umsetzen, ohne Fachlogik anzufassen. Kein separates JavaScript-Projekt nötig. |
| Datenbank | **PostgreSQL 18** [geprüft] | Bewährte relationale Datenbank. Eindeutigkeitsregeln und Sperren, die für Mehrfachzuweisung und Reminder wichtig sind, werden direkt in der Datenbank abgesichert. Auch Tests laufen gegen PostgreSQL. |
| Anmeldung | Django-Anmeldung mit Sitzungs-Cookie (Secure, HttpOnly, SameSite=Lax), Passwort-Hashing **Argon2** über `argon2-cffi` [geprüft], Schutz gegen Passwortraten mit **django-axes** [geprüft: 8.3.1, Django bis 6.0], eigenes Benutzermodell von Anfang an | Keine selbst gebaute Kryptografie. Ein eigenes Benutzermodell lässt sich später kaum nachrüsten, darum sofort. SSO kann später ergänzt werden (z. B. django-allauth [ungeprüft]). |
| Rechte | Eigene, zentrale Rechteregeln im Code plus Datenbankabfragen, die von vornherein nur Erlaubtes liefern | Djangos eingebaute Rechte sind global und kennen keine Projektgrenzen. Details in `entwurf-datenmodell-und-rechte.md`. |
| PDF | **WeasyPrint** [geprüft: 70.0] erzeugt PDFs aus HTML/CSS mit Seitenzahlen und Seitenumbruchregeln | Vorlagen sind HTML, also für dich lesbar. Läuft im Linux-Container. Unter Windows direkt ist die Einrichtung aufwendig [geprüft], deshalb Entwicklung im Container. |
| Hintergrundjobs | Eigener **Scheduler-Prozess** (`manage.py run_scheduler`) mit Datenbanksperre, damit er nur einmal läuft; Reminder werden über einen eindeutigen Schlüssel je Person und Tag gegen Doppelversand geschützt | Django liefert für sein Tasks-Framework keinen Worker für den Produktivbetrieb [geprüft]. Eine Warteschlange (z. B. Celery mit Redis) wäre für ein kleines Team zu viel Infrastruktur. |
| Tests und Qualität | pytest mit pytest-django [geprüft: 4.14.0, Django bis 6.0], factory_boy, ruff, uv mit Sperrdatei für Paketversionen [ungeprüft]; später Playwright für Browsertests [ungeprüft] | Gängige, gut gepflegte Werkzeuge mit festgehaltenen Versionen. |
| Betrieb | Docker-Container: Web, Scheduler, Datenbank; davor **Caddy** für HTTPS [geprüft] | Gleicher Aufbau lokal, auf Dev und auf Prod. Caddy besorgt und erneuert Zertifikate selbst. |

### Alternativen

- **Django 6.1** statt 5.2 LTS: neuer, aber zwei Zusatzpakete nennen 6.1 noch nicht als unterstützt [geprüft]. Wäre nach einem kurzen technischen Test denkbar.
- **TypeScript mit Next.js und React:** sehr verbreitet, aber Anmeldung, Rechte, Migrationen und Verwaltung müssen aus mehreren Bibliotheken zusammengesetzt werden; zusätzlich ein JavaScript-Build. Mehr Wartung, Rechtelogik leicht doppelt.
- **PDF über Headless Chromium (z. B. Gotenberg)** [ungeprüft]: sehr genaue Darstellung, aber ein zusätzlicher großer Container.
- **Warteschlange über das Paket django-tasks mit Datenbank-Backend** [geprüft: Datenbank-Backend separat als `django-tasks-db`]: sinnvoll, sobald es viele Hintergrundaufgaben gibt.

## 2. Lokale Entwicklung unter Windows 11 Home

Vorschlag: **WSL2 mit Ubuntu und Docker Engine innerhalb von WSL**. Das Repository liegt im WSL-Dateisystem, dort arbeiten auch Git und Claude Code.

- Vorteil: identische Linux-Umgebung wie auf dem Server; WeasyPrint läuft ohne Windows-Sonderwege.
- Vorteil: löst nebenbei die Git-Lücke (dauerhaftes Git in WSL statt Codex-Pfad).
- Offen [ungeprüft]: ob und wie die Claude-Desktop-App mit einem Ordner in WSL arbeitet; Alternative wäre die Claude-Code-Kommandozeile direkt in WSL.
- Alternative: Docker Desktop. Für deine private Nutzung kostenfrei [geprüft], aber die Herstellerseite nennt bei den WSL2-Anforderungen Windows 11 Home nicht eindeutig [geprüft].

Das ist eine Installation und wird erst nach deiner Freigabe als Schritt-für-Schritt-Anleitung vorbereitet.

## 3. Umgebungen

| | Lokal | Dev | Prod |
| --- | --- | --- | --- |
| Zweck | Entwickeln und Testen | Vorschau und deine Prüfung | Produktive Nutzung |
| Datenbank | lokal, Wegwerfdaten | eigene Datenbank, nur Beispieldaten | eigene Datenbank |
| Dateien | lokaler Ordner | eigenes Volume | eigenes Volume, gesichert |
| Geheimnisse | `.env` lokal, nicht in Git | auf dem VPS im Dev-Bereich | auf dem VPS im Prod-Bereich, eigener Linux-Benutzer |
| E-Mail | nur Protokoll | Mail-Fänger (z. B. Mailpit [ungeprüft]), nichts wird zugestellt | echter Versand über SMTP-Anbieter |
| Adresse | localhost | `dev.<domain>`, zusätzlich zugangsgeschützt | `app.<domain>` |

Zusätzliche Sicherung in der Anwendung: E-Mail-Modus `log | catch | smtp` und eine Empfänger-Positivliste. Beispieldaten lassen sich nur per eigenem Befehl laden, der in Prod abbricht. Produktive Daten werden nie nach Dev kopiert.

**Vorschlag für den Start: ein VPS mit zwei getrennten Stacks.** Getrennt sind Container-Projekte, Netzwerke, Datenbanken, Volumes, Geheimnisse und Linux-Benutzer; gemeinsam nur Caddy. Dev bekommt CPU- und Speichergrenzen.

- Vorteil: etwa halbe Kosten und halber Pflegeaufwand.
- Nachteil: gemeinsames Ausfall- und Angriffsrisiko. Für persönliche Nutzung und kleines Team vertretbar.
- **Auf zwei Server trennen**, sobald eines eintritt: sensible Kundendaten im Teambetrieb, Dev stört Prod, Dritte erhalten Dev-Zugang, Kunden- oder Compliance-Vorgaben, Experimente auf Betriebssystemebene.

## 4. Deployment-Pipeline mit kontrollierter Prod-Freigabe

**Ausgangslage [geprüft]:** Für private Repositories bieten GitHub Free, Pro und Team keine „Required reviewers“ für Umgebungen. Ein bezahltes Upgrade auf Pro oder Team würde die Freigabe also nicht lösen. Deshalb liegt die Freigabe bewusst **auf dem Server bei dir**.

```
Änderung → Pull Request → CI: Prüfungen + Image bauen → GHCR (Image mit festem Digest)
                                                        │
                       Dev zieht automatisch ◄──────────┘
                       (Migration, Neustart, Protokoll)
                                                        │
       Du prüfst auf Dev  →  du startest auf dem VPS: deploy-prod <digest>
                              Prüfung „lief auf Dev“, Sicherung, Migration,
                              Neustart, Gesundheitsprüfung, Protokoll
```

1. **CI (GitHub Actions)** bei jedem Pull Request und auf `main`: Code-Prüfung (ruff), Tests gegen PostgreSQL, Prüfung auf fehlende Migrationen, Image bauen. Auf `main` wird das Image in GHCR abgelegt und mit Commit-SHA sowie unveränderlichem Digest (`sha256:…`) gekennzeichnet. Kosten: im Freikontingent von 2.000 Minuten [geprüft; Ausreichen ungeprüft].
2. **Dev automatisch nach dem Pull-Prinzip:** Ein Zeitgeber auf dem VPS prüft regelmäßig, ob es ein neues `main`-Image gibt, zieht es, führt Migrationen aus und startet neu. GitHub hat dadurch **keinen Zugang zum Server**. Auf dem VPS liegt nur ein Lesetoken für Pakete; GHCR verlangt dafür einen klassischen Token mit `read:packages` [geprüft]. Nachteil: Ein klassischer Token gilt kontoweit für Pakete, darum nur Leserecht, eigener Token, regelmäßig erneuern.
3. **Prod bewusst durch dich:** Du meldest dich per SSH an und führst `deploy-prod <digest>` aus. Das Skript
   - lehnt jeden Digest ab, der nicht zuvor erfolgreich auf Dev lief,
   - sichert vorher Datenbank und Dateien,
   - führt Migrationen aus, startet neu, prüft den Gesundheitsendpunkt,
   - protokolliert Digest, Zeitpunkt und Ergebnis.
   Prod-Zugangsdaten liegen nur auf dem VPS und in deinem Passwortmanager, **nicht in GitHub**.
4. **Datenbankmigrationen** nur vorwärts und in zwei Schritten (erst ergänzen, Entfernen erst in einer späteren Version). So läuft meist auch die vorherige Version noch mit dem neuen Schema.
5. **Zurück zur vorherigen Version:** vorherigen Digest erneut ausrollen; klappt, solange das Schema verträglich ist. **Daten wiederherstellen** ist davon getrennt: Die Sicherung vor dem Deployment verwirft alle Änderungen seitdem und ist ein bewusster Notfallschritt.

**Alternativen:**

- (a) Prod-Deployment per manuell gestartetem GitHub-Workflow mit Prod-Schlüssel als Repository-Geheimnis: bequemer, aber der Schlüssel liegt in GitHub und es gibt keine echte Freigabestufe. Nicht empfohlen.
- (b) Eigener GitHub-Runner auf dem VPS: spart Minuten, aber fremd ausgelöster Workflow-Code liefe auf dem Prod-Server. Für Prod abgelehnt.

## 5. Sicherung und Wiederherstellung

- **Was:** Prod-Datenbank (logischer Export), Prod-Dateien (Uploads, erzeugte PDFs, veröffentlichte Berichtsstände), Container- und Caddy-Konfiguration, verschlüsselte Geheimnisse, Liste der laufenden Image-Digests.
- **Wohin:** verschlüsselt und dedupliziert (z. B. restic oder borg [ungeprüft]) zu einem Speicher bei einem **anderen Anbieter** als dem VPS. Backup-Schlüssel zusätzlich offline. Server-Snapshots des Anbieters nur ergänzend.
- **Wie oft:** täglich und vor jedem Prod-Deployment; Aufbewahrung etwa 7 täglich, 4 wöchentlich, 6 monatlich.
- **Vorschlag Zielwerte:** höchstens 24 Stunden Datenverlust, Wiederherstellung innerhalb eines Arbeitstags. Das ist deine Entscheidung.
- **Wiederherstellungsprobe** vor der Teamfreigabe und danach vierteljährlich, in einer temporären, abgeschotteten Umgebung ohne Mailversand (nicht in Dev, da Prod-Daten nicht nach Dev gehören).
- **Überwachung:** fehlgeschlagene oder ausbleibende Sicherung muss auffallen (Status-Mail oder externer Heartbeat [ungeprüft]).

## 6. Laufender Aufwand und Kosten

**Alle Zahlen sind ungeprüfte Schätzungen**; Preise vor einer Buchung beim Anbieter prüfen. Es wird nichts gebucht.

| Posten | Schätzung |
| --- | --- |
| Ersteinrichtung Server, Pipeline, Sicherung, erste Probe | 1–3 Personentage |
| Laufender Betrieb (Updates, Sicherungskontrolle, Logs) | 2–4 Stunden/Monat, plus 2–3 Stunden/Quartal Wiederherstellungsprobe |
| VPS 2–4 vCPU, 4–8 GB RAM, EU-Standort | ca. 5–20 €/Monat |
| Backup-Speicher bei anderem Anbieter | ca. 1–5 €/Monat |
| SMTP-Anbieter | Freikontingent bis ca. 15 €/Monat |
| Domain | ca. 1–2 €/Monat |
| GitHub Free, GHCR | 0 € [geprüft für die aktuellen Freikontingente] |
| **Summe** | **grob 10–40 €/Monat** |

Zusätzlich zu bedenken: Für VPS-, Mail- und Backup-Anbieter ist ein Auftragsverarbeitungsvertrag nötig, sobald Teamdaten verarbeitet werden; ein EU-Standort wird empfohlen.

## 7. Offene Betriebsentscheidungen (für später, nicht blockierend für den ersten lokalen Abschnitt)

1. Domain und VPS-Anbieter. *Empfehlung: eigene Domain, Anbieter mit EU-Standort und AV-Vertrag.*
2. SMTP-Anbieter und Absender. *Empfehlung: Transaktionsmail-Anbieter in der EU, Versand über eigene Domain mit SPF, DKIM, DMARC.*
3. Backup-Ziel und Zielwerte. *Empfehlung wie Abschnitt 5.*
