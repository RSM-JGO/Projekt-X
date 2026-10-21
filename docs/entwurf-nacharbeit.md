# ENTWURF: Nacharbeit der Architekturentwürfe (Revision 2)

Status: **Entwurf, nicht freigegeben**. Stand: 21. Oktober 2026. Grundlage: die zehn Punkte in `docs/pruefung-architekturentwuerfe.md`.

Die vier ursprünglichen Entwürfe (`entwurf-vorbereitung.md`, `entwurf-technik-und-betrieb.md`, `entwurf-datenmodell-und-rechte.md`, `entwurf-erster-entwicklungsabschnitt.md`) bleiben als ursprünglicher Vorschlag erhalten und tragen nur einen Hinweis auf dieses Dokument. **Wo sich die Aussagen widersprechen, gilt dieses Dokument.** Nicht genannte Teile der Entwürfe gelten unverändert weiter als Entwurf.

Kennzeichnung wie in den Entwürfen: **[geprüft]** = in offizieller Dokumentation nachgesehen, **[ungeprüft]** = Annahme, vor Festlegung prüfen.

## Übersicht

| Nr. | Prüfpunkt | Betroffene Stellen | Kurz: neue Aussage |
| --- | --- | --- | --- |
| 1 | Einrichtung nicht erneut aufrollen | Vorbereitung §1, Technik §2, E5 | Git ist eingerichtet und nachgewiesen; daraus folgt kein Umzug nach WSL. |
| 2 | Desktop-Arbeitsweise erhalten | Technik §2, E5 | Zuerst die Option mit Repository unter Windows und Claude Desktop prüfen, Abschnitt A. |
| 3 | Docker-Home-Aussage präzisieren | Technik §2, Prüfprotokoll | Eignung am konkreten Rechner prüfen, weder Ausschluss noch Zusage, Abschnitt A. |
| 4 | Styleguide vor Oberfläche | Erster Abschnitt, Vorbereitung §3, E6 | Keine ungestaltete Oberfläche. V06 vor jeder Oberfläche, Fundament ohne Oberfläche parallel, Abschnitt B. |
| 5 | Bedienbarer Prod-Prozess | Technik §4, E4 | Kein regelmäßiger SSH-Befehl. Manuell gestarteter Workflow und Pull-Variante bewertet, Abschnitt C. |
| 6 | Rollenmodell konsistent | Datenmodell §2–3, B2, E3 | Keine globale Fachrolle; Projektanlage-Befugnis getrennt; mehrere Projektrollen je Person, Abschnitt D. |
| 7 | Persönliche Aufgaben vollständig | Datenmodell §2–3 | Expliziter Eigentümer, Sichtbarkeitsregeln, Dateien nur über Bezugsobjekt, Abschnitt E. |
| 8 | Projekttermine historisieren | Datenmodell §2 Planung | Projektzeitraum, Vorgang und Meilenstein mit Plan, Prognose und Ist, Abschnitt F. |
| 9 | Reminder nicht überversprechen | Datenmodell Reminder, Vorbereitung Frage 5 | Zustand „unklar“, begrenzte Wiederholung, Sichtbarkeit; Frage 5 entfällt, Abschnitt G. |
| 10 | Phasen nicht umbaufrei versprechen | Datenmodell Erweiterungspunkt, Vorbereitung §3 | Erweiterungspunkt ja, Umbaufreiheit nein, Abschnitt H. |

## A. Lokale Entwicklungsumgebung (Punkte 1–3)

**Ausgangslage:** Git for Windows ist regulär installiert und in einer neu gestarteten Claude-Sitzung nachgewiesen (`docs/einrichtungsstand.md`, `docs/arbeitsstand.md`). Claude Desktop arbeitet bereits mit dem Windows-Ordner `C:\Users\jango\Documents\Projektmanagement-Software`. Die Aussagen „Git nur über Codex-Pfad“ (Vorbereitung §1) und „WSL löst die Git-Lücke“ (Technik §2) sind überholt.

**Unverändert:** Die Anwendung soll in Linux-Containern laufen, lokal wie auf dem Server. Gründe: WeasyPrint ist unter Linux einfach, unter Windows aufwendig [geprüft]. Außerdem verhält sich die lokale Umgebung dann wie der Server.

| Option | Beschreibung | Vorteil | Nachteil / offen |
| --- | --- | --- | --- |
| **L1 (Vorschlag)** | Repository bleibt im Windows-Ordner, Claude Desktop wie heute. Container über Docker Desktop mit WSL2-Backend. Claude startet `docker compose` aus der Windows-Sitzung. | Bestehende, nachgewiesene Arbeitsweise bleibt; keine zweite Git-Installation | Eignung von Docker Desktop auf diesem Rechner prüfen. Dateizugriff aus Containern auf Windows-Ordner kann langsamer sein [ungeprüft] |
| L2 | Repository im WSL-Dateisystem, Claude Desktop mit WSL-Sitzung (laut Claude-Dokumentation vorgesehen [geprüft, Quelle in der Prüfung]) | Schnellerer Dateizugriff, Linux-Werkzeuge direkt | Umzug des Arbeitsordners; Git-Anmeldung und Desktop-Zugang in WSL erst nachweisen |
| L3 | Docker Engine direkt in WSL ohne Docker Desktop | Keine Docker-Desktop-Lizenzfrage | Mehr Handarbeit; Repository-Ort wie L1 oder L2 zu klären |

**Docker unter Windows 11 Home:** Die Herstellerseite nennt Linux-Container für Windows Home und Education. Zugleich listet sie bei den Anforderungen bestimmte Editionen auf [geprüft, Quelle in der Prüfung]. Daraus folgt weder ein Ausschluss noch eine geprüfte Eignung. Docker Desktop ist für private Nutzung und kleine Firmen kostenfrei [geprüft].

**Prüfschritte vor der Entscheidung.** Sie verändern nichts und werden erst nach Auftrag ausgeführt:

1. Windows-Version und Build sowie WSL-Version und -Status auslesen.
2. Prüfen, ob die Hardware-Virtualisierung aktiv ist.
3. Die Ergebnisse mit den aktuellen Docker-Desktop-Anforderungen vergleichen.
4. Erst danach die Installation als Schritt-für-Schritt-Anleitung vorbereiten. Ein lauffähiger Start mit Datenbankcontainer gilt als Nachweis.

**Nebenbefund:** Die geplanten Befehle im Entwurf zum ersten Abschnitt sollten über ein Makefile gebündelt werden. `make` ist unter Windows nicht vorhanden. Bei L1 ist dafür ein Windows-taugliches Skript oder ein anderer Befehlsbündler nötig. Das wird zusammen mit L1 bis L3 entschieden.

## B. Styleguide vor Oberfläche (Punkt 4)

Der Vorschlag „schlichte, ungestaltete Oberfläche“ im ersten Abschnitt entfällt. Neue Reihenfolge:

1. **V06 Gestaltungsproben:** klickbarer Prototyp mit gekennzeichneten Beispieldaten. Er deckt Navigation, Informationsdichte und zentrale Komponenten ab: Aufgabenliste, Board, Kalender, Zeitplan, Dashboard. Das entspricht dem „nächsten sinnvollen Schritt“ der Produktgrundlage. Hier ist auch nachzuweisen, dass Board-, Kalender- und Zeitplaninteraktion mit der vorgeschlagenen Technik bedienbar umsetzbar ist.
2. **V07a Fundament ohne Benutzeroberfläche** (kann parallel zu V06 laufen): Datenmodell, Migrationen, Rechteregeln, schreibende Dienste und Beispieldaten. Der Nachweis erfolgt durch automatisierte Tests gegen PostgreSQL. Die Abnahmekriterien 3 bis 11 des ursprünglichen Entwurfs werden auf Ebene der Dienste und Rechteregeln geprüft, ohne gestaltete Seiten. Ausnahme ist Kriterium 1 (Seiten ohne Anmeldung), weil es Seiten voraussetzt.
3. **V07b Oberfläche des ersten Abschnitts:** Anmeldung, Projekt- und Aufgabenseiten. Sie entstehen erst nach Bestätigung von V06 und mit den dort festgelegten Gestaltungsmitteln (CSS-Variablen, Komponenten).

Ein Branding wird nicht erfunden. Die Aufteilung V07a/b ist ein Vorschlag und wird im Backlog erst nach Benutzerentscheidung übernommen.

## C. Bedienbarer Prod-Prozess (Punkt 5)

**Anforderung:** Der Benutzer gibt Prod bewusst frei, ohne regelmäßig Serverbefehle einzugeben. Prod erhält genau die auf Dev geprüfte Version (`docs/releaseprozess.md`). Der SSH-Befehl `deploy-prod <digest>` ist damit nicht mehr der Standardweg. Er bleibt nur als Notfallzugang.

**Gemeinsam für alle Varianten:** Auf dem Server liegt ein festes Prod-Skript mit folgenden Eigenschaften:

- **Nur geprüfte Versionen:** Das Skript nimmt nur einen Image-Digest an, der auf Dev **als geprüft vermerkt** ist. „Lief auf Dev“ allein reicht nicht, weil Dev jedes neue `main`-Image automatisch übernimmt. Der Prüfvermerk liegt auf dem Server und verweist auf den Release-Nachweis nach `docs/releaseprozess.md`. Die Eingabe wird streng auf das Format `sha256:` plus Hexzeichen geprüft. Bei P2 wird die Zuordnung Tag → Commit → Digest festgehalten.
- **Sperre:** Es läuft höchstens ein Deployment zugleich. Doppelklick, wiederholte Abfrage und paralleler Dev-Pull werden abgewiesen oder warten.
- **Sicherung:** Vor der Migration sichert das Skript Datenbank und Dateien. Schlägt die Sicherung fehl, **bricht es ab**.
- **Rückfall:** Ein Rückfall auf den vorherigen Digest läuft über denselben Weg, solange das Schema verträglich ist. Eine Datenwiederherstellung bleibt ein gesonderter Notfallschritt.
- **Nachweis:** Nach dem Ausrollen folgt eine Gesundheitsprüfung. Maßgeblich ist das Serverprotokoll mit Digest, Zeitpunkt und Ergebnis; es wird in den Release-Nachweis übernommen. Die Gesundheitsprüfung ersetzt **nicht** die fachliche Nachprüfung auf Prod.
- **Freigabe:** Ein Klick oder Tag startet das Deployment, ist aber keine dokumentierte Benutzerfreigabe. Die Freigabe wird gesondert im Release-Nachweis festgehalten.
- **Konfiguration:** Unterschiede zwischen Dev und Prod, etwa Mailmodus, Adressen und Secrets, werden je Release benannt.
- **Lesezugriff:** Auch Prod braucht ein eigenes Lesetoken für GHCR.
- **Kontoschutz:** Zwei-Faktor-Anmeldung für das GitHub-Konto und Branchschutz für `main`. Tag-Schutz unter GitHub Free [ungeprüft].

Die Bewertung „Variante (a) nicht empfohlen“ in `entwurf-technik-und-betrieb.md` §4 ist damit überholt. Grund: Der Schlüssel kann auf das Prod-Skript beschränkt werden.

| Variante | Bedienung | Rechte und Secrets | Schutz bei Fehlbedienung oder fremdem Zugriff |
| --- | --- | --- | --- |
| **P1 Manuell gestarteter GitHub-Workflow** (`workflow_dispatch` [geprüft, Quelle in der Prüfung]) | Benutzer klickt in GitHub „Run workflow“ und wählt die Version; das Ergebnis steht im Workflow-Protokoll | Ein Deploy-Schlüssel liegt als Repository-Secret in GitHub. Auf dem Server ist er auf genau das Prod-Skript beschränkt, zum Beispiel per festem SSH-Befehl, also ohne freie Shell [ungeprüft für die konkrete Servereinrichtung]. Starten kann jede Person mit Schreibrecht am Repository. | **Keine** unabhängige Freigabesperre: Bei privaten Repositories unter GitHub Free gibt es keine „Required reviewers“ [geprüft]. Wer Schreibrecht hat oder das GitHub-Konto übernimmt, kann jede Version ausrollen, die auf Dev lief. Workflow-Code wird nur aus `main` genommen. |
| **P2 Freigabe per Release-Markierung, Server holt ab** | Benutzer erstellt in GitHub ein Release oder einen Tag für die geprüfte Version. Der Prod-Server fragt regelmäßig nach und rollt aus. | GitHub erhält keinen Zugang zum Server. Auf dem Server liegt nur ein Lesetoken, wie beim Dev-Pull-Prinzip. | Ebenfalls keine unabhängige Sperre; Releases und Tags anlegen kann jede Person mit Schreibrecht. Rückmeldung erst nach dem nächsten Abfrageintervall; das Ergebnis muss gesondert sichtbar gemacht werden, etwa per Status-Mail [ungeprüft]. |
| P3 SSH-Befehl (ursprünglicher Vorschlag) | Benutzer meldet sich am Server an | Kein Prod-Secret in GitHub | Stärkste Trennung, aber nicht die gewünschte Bedienung; nur als Notfallzugang |

**Bewertung (Entwurf, vom Releasemanager geprüft):** Empfehlung für den Start mit einem Einzelnutzer ist **P1**. Das gilt unter drei Bedingungen: fester SSH-Befehl, strenge Digest-Prüfung, Zwei-Faktor-Schutz. Gründe: P1 lässt sich einfach bedienen und gibt sofort sichtbare Rückmeldung. Bei einer Kontoübernahme ist der Schaden ähnlich wie bei P2, wenn der Schlüssel auf das Skript beschränkt ist. P2 ist die Ausweichlösung, falls sich diese Beschränkung auf dem konkreten Server nicht nachweisen lässt. Beide sind ein **manueller Start, keine abgesicherte Freigabestufe**. Solange nur der Benutzer Schreibrecht hat, sind beide vertretbar. Vor der Teamfreigabe ist neu zu entscheiden, wer Schreibrecht erhält. Die Pipeline wird erst mit dem Dev-Server konkretisiert und blockiert die lokale Entwicklung nicht.

## D. Rollenmodell (Punkt 6)

Die Begriffe „eine globale Rolle“ und „Projektrolle“ ersetzen sich durch drei getrennte Bausteine:

| Baustein | Inhalt | Regel |
| --- | --- | --- |
| **Administrator-Kennzeichen** am Benutzer | Systemverwaltung: Benutzerkonten, Mitgliedschaften (protokolliert), Lesen aller Projekte nach E7 | Die einzige globale Rolle. Kein Freigaberecht und keine fremden persönlichen Aufgaben (E7, weiterhin Vorschlag). |
| **Befugnis „Projekte anlegen“** am Benutzer | Erlaubt das Anlegen neuer Projekte | Vergibt der Administrator. Die Befugnis gewährt **keinen** Zugriff auf bestehende Projekte. Wer anlegt, wird automatisch Projektleiter des neuen Projekts. |
| **Befugnis „Projekte löschen“** am Benutzer | Logisches Löschen von Projekten mit Anzeige der betroffenen Inhalte (Produktgrundlage: „gesonderte Berechtigung“) | Vergibt der Administrator. Vorschlag: zunächst nur Administratoren. |
| **Projektmitgliedschaft mit einer oder mehreren Projektrollen** (Projektleiter, Mitarbeiter, Management) | Was jemand in einem Projekt darf | Eine Person kann in verschiedenen Projekten verschiedene Rollen und in einem Projekt mehrere Rollen haben. Die Rechte ergeben sich als Vereinigung der Rollen. Eine aktive Mitgliedschaft hat mindestens eine aktive Rolle. Rollenzeiträume liegen innerhalb der Mitgliedschaft. Je Projekt gibt es mindestens einen aktiven Projektleiter mit aktivem Konto. Austritt, Rollenentzug und Kontodeaktivierung prüfen diese Regel. |

Datenmodell-Änderung: `User.globale Rolle` entfällt zugunsten von `is_admin` und `can_create_projects`. `ProjectMembership` (Projekt, Benutzer, Beginn, Ende) erhält `ProjectRoleAssignment` (Mitgliedschaft, Rolle, Beginn, Ende, vergeben von). Je Mitgliedschaft und Rolle gibt es höchstens eine aktive Zuordnung. Rollenänderungen werden protokolliert.

**Management**, korrigierte Zeilen der Rechtematrix:

- sieht in zugeordneten Projekten Dashboard, Meilensteinübersicht und veröffentlichte Statusberichte samt deren PDF;
- hat **keinen** pauschalen Zugriff auf Aufgabenanhänge, Uploads oder Dokumententwürfe;
- erhält Zugriff auf weitere Dokumente nur, wenn sie ausdrücklich für das Reporting bereitgestellt sind; ob es diese Bereitstellung gibt, ist offen.

Die Zeile „Datei herunterladen: Management ja (P)“ entfällt. Gilt eine Person in einem Projekt zusätzlich als Mitarbeiter, hat sie dort die Mitarbeiterrechte.

**Zuweisung:** Aufgaben lassen sich nur Personen mit aktiver Rolle Projektleiter oder Mitarbeiter zuweisen. Eine reine Management-Rolle reicht nicht, damit über eine Zuweisung keine Schreibrechte entstehen.

**Administrator in Projektinhalten:** Die alte Matrix gibt dem Administrator Schreibrechte, E7 nur Lese- und Mitgliedschaftsrechte. Das ist im ursprünglichen Entwurf widersprüchlich. Vorschlag: Der Administrator liest alles und verwaltet Mitgliedschaften. Korrekturen an Aufgaben sind nur als protokollierte Ausnahme erlaubt, Freigaben nie. Die Entscheidung fällt in V05; die Admin-Zeilen der alten Matrix gelten bis dahin als nicht festgelegt.

Die vier Benutzerrollen der Produktgrundlage bleiben damit erhalten: Administrator global, die drei anderen projektbezogen. Die detaillierte Rechtematrix bleibt Aufgabe von V05.

## E. Persönliche Aufgaben, Dateien und Erweiterungsbedarf (Punkt 7)

**Aufgabe**, ergänzte Felder und Regeln:

- `owner` (Eigentümer) ist Pflicht für **persönliche Aufgaben** (ohne Projekt): die anlegende Person, Wechsel nur durch sie selbst. Projektaufgaben haben keinen Eigentümer; für sie gelten Projektrechte und Zuweisungen.
- Persönliche Aufgaben sieht und bearbeitet nur der Eigentümer, auch kein Administrator. Zuweisungen an andere Personen sind in der ersten Fassung **nicht** möglich. Ob persönliche Aufgaben geteilt werden dürfen, ist offen (Produktgrundlage: „Sichtbarkeit persönlicher Aufgaben“).
- Ob eine persönliche Aufgabe in eine Projektaufgabe umgewandelt werden kann, ist offen. Falls ja, braucht sie dabei Bucket und Projektrechte; der Verlauf bleibt erhalten.
- In „Meine Aufgaben“ sind drei Herkünfte unterscheidbar: persönliche Aufgaben, mir zugewiesene Projektaufgaben und Aufgaben in von mir geleiteten Projekten (Produktgrundlage, Persönlicher Arbeitsplatz).

**Dateien:** `StoredFile` gehört zu genau **einem Bezugsobjekt**, etwa Aufgabe, Dokumentversion, veröffentlichter Berichtsstand oder Projekt. Für jede Art von Bezugsobjekt gibt es ein **eigenes Dateirecht**; das Leserecht am Bezugsobjekt wird nicht einfach übernommen. Beispiel: Management darf ein Projekt lesen, aber nicht automatisch dessen Projektdateien, sondern nur Berichts-PDFs (Abschnitt D). Anhänge einer persönlichen Aufgabe sieht nur deren Eigentümer. Eine Datei ohne gültiges Bezugsobjekt ist für niemanden abrufbar, höchstens für den Betrieb zur Bereinigung. **Fehlende Projektzuordnung bedeutet nie freie Zugänglichkeit.** Wird das Bezugsobjekt logisch gelöscht, ist auch die Datei nicht mehr abrufbar.

**Erweiterungsbedarf**, noch nicht modelliert, aber im Gesamtmodell vorzusehen:

- **Kommentar:** Aufgabe, Autor, Text, Zeitpunkt, bearbeitet oder logisch gelöscht. Sichtbar wie die Aufgabe; Kommentare bleiben erhalten (Produktgrundlage).
- **Stakeholder:** Projekt, Name, Organisation, fachliche Rolle. Ausdrücklich **kein** Benutzerkonto und kein Zugriff.
- **Steckbriefdaten:** strukturierte Projektfelder wie Ziele, Erfolgskriterien, Auftraggeber, Annahmen, Rahmenbedingungen und erste Risiken. Sie werden von Dokumentvorlagen wiederverwendet. Pflichtfelder und Auswahl sind offen.

## F. Termine und Planversionen (Punkt 8)

**Begriffe (Vorschlag):**

| Begriff | Art | Termine |
| --- | --- | --- |
| Projektzeitraum | Zeitraum des Projekts | Beginn und Ende |
| Vorgang | geplanter Zeitraum innerhalb des Projekts, etwa für Timeline oder Zeitplan | Beginn und Ende |
| Meilenstein | **Ereignis** | ein Termin |

Für jeden dieser Termine gelten dieselben vier Ebenen: ursprünglicher Plan, aktuell genehmigter Plan, Prognose und Ist.

**Datenmodell-Änderung:**

- `PlanItem` verweist auf **genau ein** Ziel: den Projektzeitraum, einen Vorgang oder einen Meilenstein. Die Datenbank prüft, dass genau ein Verweis gesetzt ist. Zeiträume tragen geplanten Beginn und geplantes Ende („Ende nicht vor Beginn“ am Planeintrag), Meilensteine nur einen geplanten Termin. Der ursprüngliche Entwurf gab Meilensteinen fälschlich Beginn und Ende.
- Je Planversion gibt es genau einen Eintrag für den Projektzeitraum und höchstens einen je Vorgang oder Meilenstein. Der **ursprüngliche Plan eines Objekts** ist die erste freigegebene Planversion, die es enthält. Das gilt auch für Meilensteine, die erst später hinzukommen.
- Prognose und Ist werden für Projektbeginn und -ende, Vorgangsbeginn und -ende sowie Meilensteine geführt. Jede Änderung erzeugt einen `DateChange`-Eintrag. `DateChange` erhält ein Feld „Terminpunkt“ (Beginn, Ende oder Termin) und verweist wie `PlanItem` auf genau ein Ziel: Projekt, Vorgang, Meilenstein oder Aufgabenfälligkeit.
- `Project.Start/Ende` sind keine frei überschreibbaren Felder mehr. Angezeigt wird der aktuell genehmigte Planwert, jede Änderung läuft über eine neue Planversion. Ohne freigegebene Planversion gilt der Projektzeitraum als „noch nicht genehmigt“ und wird nicht als planmäßig bewertet.
- Ob Vorgänge schon in der ersten Fassung gebraucht werden, ist offen. Der Begriff ist ein Vorschlag und an der Timeline der Produktgrundlage zu prüfen.

## G. Reminder (Punkt 9)

Eine eindeutige Zeile je Benutzer, Art und Tag verhindert, dass **mehrere Jobs** dieselbe Sammelmail erzeugen. Sie garantiert **nicht**, dass die Mail genau einmal zugestellt wird. Bricht die Verbindung nach dem Senden ab, etwa durch einen SMTP-Timeout oder Prozessabbruch, ist offen, ob der Anbieter die Mail angenommen hat. Selbst eine Annahme durch den Anbieter ist noch keine Zustellung im Postfach.

**Zustände von `ReminderDelivery` (überarbeitet):**

| Zustand | Bedeutung | Folge |
| --- | --- | --- |
| VORBEREITET | Zeile angelegt, Inhalt festgelegt, noch kein Sendeversuch | Darf nach Abbruch erneut versucht werden |
| SENDEVERSUCH | Übergabe an den Mailanbieter begonnen, vor dem Senden gespeichert | Bleibt die Zeile hier stehen, wird sie UNKLAR |
| GESENDET | Anbieter hat angenommen | Abgeschlossen |
| ÜBERSPRUNGEN | Keine überfälligen Aufgaben oder Erinnerung deaktiviert | Abgeschlossen |
| FEHLGESCHLAGEN | Eindeutig nicht angenommen, zum Beispiel Verbindung vor dem Senden verweigert | Automatisch begrenzt wiederholbar (Anzahl und Abstand festlegen), danach sichtbar |
| UNKLAR | Annahme durch den Anbieter weder bestätigt noch ausgeschlossen | **Kein** automatischer Neuversand, sichtbar in einer Betriebsübersicht für den Administrator |

Jede Sammelmail erhält eine feste, aus der Zeile abgeleitete Nachrichtenkennung (Message-ID). So lässt sie sich später zuordnen. Fehlerzustände und Versuche werden protokolliert. Später ist zu prüfen, ob der gewählte Mailanbieter Idempotenzschlüssel oder einen Versandabgleich per Abfrage oder Rückmeldung anbietet. Damit ließen sich UNKLAR-Fälle automatisch auflösen [ungeprüft, abhängig vom Anbieter].

Die offene Frage 5 aus `entwurf-vorbereitung.md` („höchstens einmal“ oder „mindestens einmal“) entfällt in dieser Form. Der Benutzer entscheidet später nur, wer UNKLAR-Fälle sieht und ob eine manuelle Nachsendung angeboten wird.

## H. Phasenmodell (Punkt 10)

Das Phasenmodell bleibt offen und wird nicht angelegt. Als Erweiterungspunkt ist vorgesehen, dass Aufgaben, Vorgänge und Meilensteine später optional auf eine Phase verweisen können. Je nach Fachentscheidung, etwa zu Phasenfreigaben, Phasenabschlussdokumenten, Berichten oder Rechten je Phase, **können Anpassungen an bestehenden Modulen, Daten und Migrationen nötig werden**. Der ursprüngliche Satz „muss dafür nicht umgebaut werden“ gilt nicht mehr.

## Überarbeitete Entscheidungsvorlage

Die sieben Punkte E1 bis E7 werden nicht als Paket entschieden. Neu gegliedert:

| Nr. | Art | Entscheidung | Vorschlag | Zeitpunkt |
| --- | --- | --- | --- | --- |
| T1 | Technik | Grundrichtung | Django mit PostgreSQL, serverseitig erzeugtes HTML/CSS mit gezielten interaktiven Komponenten, Linux-Container für Betrieb und lokale Ausführung. Paketversionen (ehemals E2) erst nach T2 festlegen. | jetzt |
| T2 | Entwicklungsumgebung | Lokale Containerumgebung | L1 nach den Prüfschritten in Abschnitt A; L2 als Alternative | nach T1 und Prüfschritten |
| P | Produktregeln | B1 bis B6, E7, offene Fragen 1–4, Abschnitte D und E | im Rahmen von V05 einzeln | vor V07a |
| R | Reihenfolge | V06 Gestaltungsproben und V07a Fundament parallel, danach V07b | Abschnitt B | jetzt |
| H | Hosting und Pipeline | VPS-Aufteilung (ehemals E4) und Prod-Variante P1 oder P2 | Abschnitt C | mit dem Dev-Server, nicht blockierend |
