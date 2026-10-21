# Gemeinsames PO Backlog

Stand: 21. Oktober 2026. Die Entwicklungsreihenfolge ist ein Vorschlag. Dieses Backlog ersetzt nicht die Produktgrundlage. Noch keine Anwendungsfunktion ist implementiert.

Status: Offen, In Arbeit, Zur Prüfung, Erledigt. Ein technischer Nachweis und eine fachliche Benutzerabnahme sind getrennt zu dokumentieren.

## Vorbereitung

| ID | Aufgabe | Status | Abnahmekriterium |
| --- | --- | --- | --- |
| V09 | Releasemanager ergänzen | Erledigt | Rollendatei, Zuständigkeiten und Releaseprozess vorhanden; am 21.10.2026 als geladener Unteragent erkannt und mit einem Prüfauftrag ausgeführt |
| V08 | Zentrale Projektleitung und Übergabe an Claude | In Arbeit | Projektleitungsmodus, sieben geladene Rollen und Arbeitsstand nachgewiesen; technische Grundrichtung, Entwicklungsumgebung und erster vollständiger Arbeitsablauf vor endgültiger Übergabe noch offen |
| V01 | Claude-Arbeitsregeln und sechs Rollen vorbereiten | Erledigt | Dateien vorhanden; Claude bestätigt alle sechs als geladene aufrufbare Unteragenten; einzelner Probelauf noch nicht erfolgt |
| V02 | GitHub-Konto und privates Repository verbinden | Erledigt | Privates Repository angelegt, origin verbunden, bestätigte noreply-Identität eingerichtet und erster Commit erfolgreich hochgeladen |
| V03 | Claude mit lokalem Projektordner verbinden | Erledigt | Benutzer hat Workspace freigegeben; Claude liest die Unterlagen und benennt alle sechs geladenen Rollen |
| V04 | Architektur und Betriebsrahmen abstimmen | In Arbeit (T1 bestätigt; Windows-Entwurf Revision 3 in docs/entwurf-windows-betrieb.md; Installationsfreigabe sowie W-B bis W-E offen) | Begründete Technikauswahl, Systemgrenzen, Datenmodell und Entwicklungsbefehle dokumentiert |
| V05 | Berechtigungsmodell konkretisieren | In Arbeit (vier Grundregeln beschlossen, docs/decisions/003-produktregeln-erster-ablauf.md; Detailmatrix offen) | Rechte für alle vier Rollen, Projektgrenzen, Dateien und Freigaben überprüfbar beschrieben |
| V06 | Styleguide abstimmen | In Arbeit (Designvorschau unter design/; Gestaltung vom Benutzer grundsätzlich akzeptiert, einfacher Hell/Dunkel-Umschalter umgesetzt; Aufbau, besonders des Arbeitsplatzes, noch zu überarbeiten, vom Benutzer auf später gelegt) | Klickbare lokale Vorschau mit Beispieldaten, Projekt X, modernen Pastellakzenten und Hell/Dunkel; danach Benutzerfeedback und Bestätigung |
| V07 | Ersten Entwicklungsabschnitt definieren | In Arbeit (beauftragt; Erledigt: V07a und V07b vom Benutzer abgenommen (478 Tests grün, Browser- und Reviewprüfung bestanden)) | Kleiner vollständiger Ablauf mit Abnahmekriterien und geeigneten Prüfungen beauftragt |

## Geplante Reihenfolge (vom Benutzer am 21.10.2026 bestätigt)

1. V07b gemeinsame Aufgaben abschließen und abnehmen.
2. Arbeitsplatz-Aufbau anhand der echten Version überarbeiten.
3. Externe Demo-Ansicht: eigene Demo-Instanz, Sicherheitseinstellungen, Tunnel-Anbieter nach Benutzerfreigabe (docs/entwurf-windows-betrieb.md 4a).
4. Meilensteine und Termine mit Plan, Prognose, Ist und Freigabe.
5. Aufgaben erweitern: Kommentare, Anhänge, Board, Kalender, Priorität, Status „In Arbeit“, Buckets archivieren (Priorität und In Arbeit vom Benutzer am 21.10.2026 bestätigt).
6. Management-Übersicht.
7. Statusbericht und PDF, vorher PDF-Prototyp W-C.
8. Tägliche Erinnerungsmails.

Nebenbei: GitHub-Upload nur nach Freigabe, CI, später Umzug auf den Server des Arbeitgebers. Jede Etappe: Kriterien, Umsetzung, Prüfung und Review, Benutzerabnahme, Commit.

## Fachlicher Funktionsvorrat

Alle Einträge sind offen. Die Liste bündelt Themen, enthält aber noch keine vollständig entwicklungsfertigen Tickets.

- F01: Anmeldung, Benutzer und projektbezogene Berechtigungen.
- F02: Projekte anlegen, bearbeiten, archivieren und berechtigt löschen; Steckbrief.
- F03: Aufgaben mit Mehrfachzuweisung, Buckets, Kommentaren, Anhängen und abgeschlossenen Aufgaben.
- F04: Persönlicher Arbeitsplatz und projektübergreifende Aufgabenansichten.
- F05: Meilensteine, Planstände, Prognosen und nachvollziehbare Verschiebungen.
- F06: Projektstatus, Statushistorie und Managementdashboard.
- F07: Erfassungsmasken, Dokumentvorlagen, gespeicherte Dokumentstände und PDF-Downloads.
- F08: Monatlicher Projektstatusbericht als PDF.
- F09: Wiedervorlagen und persönliche Reminder mit täglichen Sammelmails.
- F10: Allgemeine Dateiablage mit berechtigten Uploads und Downloads.
- F11: Risiken, Probleme, Entscheidungen und Maßnahmen; Detailumfang noch konkretisieren.
- F12: Allgemeines Phasenmodell und Abschlussdokumente; ausdrücklich noch nicht festgelegt.
- F13: Betrieb, Sicherung, Wiederherstellung und Teamfreigabe.
- F15: Getrennte Dev-/Prod-Umgebungen und Deployment-Pipeline; technische Ausgestaltung offen.
- F14: Budget und Kosten; spätere Erweiterung.

## Vorlage für ein entwicklungsfertiges Ticket

- ID und Titel.
- Ziel und Anwender.
- Umfang und Abgrenzung.
- Abhängigkeiten und zugehörige Entscheidung.
- Abnahmekriterien als beobachtbares Verhalten.
- Benötigte Beispieldaten und Prüfungen.
- Umsetzungs- und Testergebnis.
- Offene Befunde und fachliche Abnahme.
