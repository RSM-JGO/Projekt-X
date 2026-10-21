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
3. Erledigt: Externe Demo-Ansicht inkl. F16 Versionsanzeige, vom Benutzer am 21.10.2026 abgenommen (docs/auftrag-demo-ansicht.md).
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
- F11: Risiken, Probleme, Entscheidungen und Maßnahmen.
  - **Konkretisiert durch Wunsch des Benutzers vom 21.10.2026:** Risiken je Projekt aufnehmen und in einer **Risiko-Matrix** pflegen (Eintrittswahrscheinlichkeit × Auswirkung). Felder pro Risiko z. B. Beschreibung, Verantwortliche, Maßnahmen und Status.
  - **Farbregeln:** Rot = hoch, Orange = mittel, Grün = niedrig; ohne Bewertung grau, nie grün.
  - **Verlauf:** Änderungen der Bewertung bleiben nachvollziehbar; spätere Übernahme in Statusberichte.
  - **Offen:** Skala (3×3 oder 5×5), Pflichtfelder, ob Chancen ebenfalls erfasst werden.
  - **Einordnung:** Baustein der Projekt-Journey F19, Umsetzung nach der Konzeptentscheidung.
- F12: Allgemeines Phasenmodell und Abschlussdokumente; ausdrücklich noch nicht festgelegt.
- F13: Betrieb, Sicherung, Wiederherstellung und Teamfreigabe.
- F15: Getrennte Dev-/Prod-Umgebungen und Deployment-Pipeline; technische Ausgestaltung offen.
- F14: Budget und Kosten; spätere Erweiterung.
- F16: Versionsanzeige (Wunsch des Benutzers vom 21.10.2026, vom Product Owner konkretisiert): dezent im Fußbereich jeder angemeldeten Seite und in `/health/`, z. B. „Projekt X 0.1.0 · a1b2c3d · dev“. Die Version kommt aus `pyproject.toml`, der Commit wird beim Start ermittelt, die Umgebung kommt aus der Konfiguration. Zusatz „geändert“ bei uncommitteten Änderungen, „unbekannt“ ohne Commit. Ein automatischer Vergleich mit dem neuesten Release kommt erst mit Release-Quelle und CI. **Eingeordnet in Etappe 3** (Demo), weil Betrachter den gezeigten Stand erkennen sollen.
  - **Änderung durch den Benutzer am 21.10.2026:** schlichteres Format „Version: 0.1.0-2f9337e“. Ungespeicherte Änderungen werden mit „*“ markiert, die Erklärung und die Umgebung stehen im Tooltip.
- F22: Passwort bei der Eingabe anzeigen (Wunsch des Benutzers vom 21.10.2026): Umschalter „anzeigen/verbergen“ am Passwortfeld der Anmeldung und überall, wo Passwörter eingegeben werden. Bedienbar per Tastatur, mit Screenreader-Beschriftung, Standard ist verborgen. Umgesetzt am 21.10.2026 (Anmeldeseite, im Browser geprüft).
- F17: Betriebsübersicht und Monitoring (Wunsch des Benutzers vom 21.10.2026, vom Product Owner konkretisiert, Vorschlag).
  - **Stufen:** 1a Admin-Seite mit App- und DB-Status, Version (F16), letzten Fehlern und Anmeldesperren; 1b mit Etappe 8 der Scheduler-Lauf und Reminder-Zustände einschließlich UNKLAR; 1c mit Server und F13 Sicherung und Wiederherstellungsprobe; 2 externer Verfügbarkeits-Check mit Alarm (externer Dienst nur nach Freigabe); 3 Server-Monitoring beim Arbeitgeber.
  - **Abnahme 1a:** nur Administratoren (Backend 403 bzw. Umleitung zur Anmeldung); fehlende oder veraltete Angaben nie grün; Fehler ohne Geheimnisse; `/health/` bleibt knapp; Tests.
  - **Vorgeschlagene Einordnung:** 1a als kleine Etappe direkt nach Etappe 3, 1b mit Etappe 8, der Rest mit dem Server.
  - **Offene Fragen an den Benutzer:** 1a direkt nach der Demo? Alarmierung per E-Mail, nur in der Ansicht oder über einen externen Dienst?
- F18: Logo-Animation beim Öffnen vor der Anmeldung (Wunsch des Benutzers vom 21.10.2026, vom Product Owner konkretisiert, Vorschlag).
  - **Umfang:** Das Logo baut sich in etwa 1 bis 1,5 s auf, erst die drei X-Segmente in Rot, Grün und Blau, dann der Schriftzug. Nur auf der Anmeldeseite, mit CSS und SVG ohne externe Bibliotheken. Dafür muss das Logo als SVG nachgebaut werden.
  - **Abnahme:** Bei „Bewegung reduzieren“ sofort sichtbar; blockiert die Anmeldung nie und lässt sich überspringen; Hell/Dunkel und offline; Screenreader liest „Projekt X“; ohne JavaScript nutzbar; keine Animation auf angemeldeten Seiten.
  - **Einordnung:** niedrige Priorität, als Zusatz zu Etappe 2 oder direkt nach Etappe 3.
  - **Offene Fragen an den Benutzer:** bei jedem Öffnen oder einmal je Sitzung? SVG-Nachbau mit Vorschau zur Abstimmung?
- F19: Projekt-Journey und Menüstruktur des Projektbereichs (Wunsch des Benutzers vom 21.10.2026, Konzeptaufgabe, vom Product Owner konkretisiert, Vorschlag).
  - **Ziel:** ein geführter Weg von Projektstart bis Abschluss.
  - **Bausteine:** Steckbrief, Stakeholder, RACI, Meilensteine und Termine, Aufgaben, Risiken, Entscheidungen und Freigaben, Statusberichte, Dokumente, Abschluss und Lessons Learned.
  - **Abgrenzung:** Die Journey ordnet nur die Navigation und beschließt kein Phasenmodell (F12 bleibt offen).
  - **Ergebnis:** klickbare Menü- und Journey-Skizze in design/ mit Beispieldaten und eine Entscheidungsvorlage mit 2 Varianten; kein Produktivcode.
  - **Einordnung (Empfehlung PO):** vor Etappe 4, weil die Menüstruktur alle weiteren Projektbereiche prägt.
- F20: Stakeholderregister und -matrix je Projekt: Name, Organisation, fachliche Rolle, Einfluss und Interesse. Ohne Benutzerkonto und ohne Zugriff. Hängt von F19 ab.
- F21: RACI-Matrix: Personen bzw. Stakeholder gegen Bezugsobjekte. Ob sich die Matrix auf Aufgaben, Meilensteine, Entscheidungen oder eigene Arbeitspakete bezieht, ist offen. Hängt von F19 und F20 ab.
- Offene Fragen zu F19 bis F21: Soll die Journey nur Orientierung geben oder auch Schritte vorgeben? Worauf bezieht sich RACI? Kommt F19 vor Etappe 4?

## Vorlage für ein entwicklungsfertiges Ticket

- ID und Titel.
- Ziel und Anwender.
- Umfang und Abgrenzung.
- Abhängigkeiten und zugehörige Entscheidung.
- Abnahmekriterien als beobachtbares Verhalten.
- Benötigte Beispieldaten und Prüfungen.
- Umsetzungs- und Testergebnis.
- Offene Befunde und fachliche Abnahme.
