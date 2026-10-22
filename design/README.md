# Projekt X – klickbare Designvorschau

Zweck: Gestaltung und Bedienung von Projekt X sichtbar machen, damit Farben, Darkmode, Navigation, Informationsdichte und Aufgabenboard beurteilt werden können. Das ist ein **Gestaltungsvorschlag**, kein bestätigter Styleguide und keine echte Anwendung.

## Öffnen

- Direkt: `design/index.html` per Doppelklick im Browser öffnen (file://). Funktioniert offline, ohne Installation und ohne externe Schriften, Skripte oder CDNs.
- Alternativ über einen beliebigen einfachen statischen HTTP-Server mit dem Ordner `design/` als Wurzel.

Ansichten (Hash-Routing): `#/arbeitsplatz`, `#/projekte`, `#/projekt/<id>` (z. B. `#/projekt/filialnetz`), `#/management`.

## Dateien

- `index.html` – Grundgerüst: Vorschau-Band, Kopfzeile, Navigation, Dialog
- `styles.css` – Design-Tokens (Hell/Dunkel) und Komponenten
- `data.js` – ausschließlich erfundene Beispieldaten, Stichtag 21.10.2026
- `app.js` – Darstellung, Routing und simulierte Interaktionen
- `assets/logo-projekt-x.webp` – Logo von Projekt X (vom Benutzer bereitgestellt)

## Nur simuliert

- Es gibt kein Backend, keine Anmeldung, keine Rechteprüfung und keine Datenbank. Der Benutzer „Jan (Beispiel)“ ist fest eingestellt.
- Abschließen und Wiederöffnen ändern nur den Zustand im Browser. Wenn möglich wird er im localStorage gespeichert. „Beispieldaten zurücksetzen“ im Vorschau-Band stellt den Ausgangszustand wieder her.
- Kommentieren, Freigeben, Anlegen und Bearbeiten sind nicht umgesetzt. Ebenso fehlen E-Mail-Erinnerungen, Statusberichte und PDF-Ausgabe.
- „Daten veraltet“ wird aus dem Datum des letzten Statusberichts berechnet (älter als 30 Tage). Der Bezugstag ist der Stichtag der Beispieldaten, nicht das echte Tagesdatum.
- Administration ist nur als deaktivierter Menüeintrag sichtbar.

## Konzeptskizze F19 v3 (Projekt-Bereiche, Meilensteine, Aufgabenboard)

Konzept zum Beurteilen; die Entscheidung ist offen. Grundlage sind `docs/auftrag-journey-konzept.md` und `docs/fachliche-orientierung-projektablauf.md`. Sie dienen als Orientierung, nicht als harte Anforderung, und zeigen die Sicht der Projektleitung, nicht des Rolloutmanagements.

- **Projektkopf und Hinweis:** Der Projektkopf ist kompakt. Ganz oben steht klein der Hinweis „Konzeptskizze F19 v3 – Entscheidung offen“.
- **Orientierungsleiste, anklickbar:** Auftragsklärung · Initiierung · Vorbereitung · Pilot · Rollout · Abschluss mit M0–M5.
  - Jeder Schritt führt zur Meilenstein-Seite, z. B. `#/projekt/filialnetz/m/M1`.
  - Angezeigt werden Freigabe-Ampel (✓ erteilt, ! unter Auflagen, ✕ keine Freigabe, ○ offen) und erledigte Lieferobjekte (z. B. „4/6“).
  - Kein festes Phasenmodell; auf dem Handy kompakt mit Vor/Zurück.
- **Meilenstein-Seite:** Ziel des Abschnitts, Lieferobjekte-Checkliste und Fortschritt, Freigabeblock, Vor/Zurück zum Nachbar-Meilenstein.
  - Checkliste: Status ✓ vorhanden / ● in Arbeit / ○ fehlt, Link in den Bereich, Kennzeichen „Pflicht“ mit Dokument-Symbol.
  - Freigabeblock: Ampel, Entscheidung, Datum, Beteiligte, Grundlage, Auflagen, Gültigkeit.
- **Zusammenspiel:** Das Hauptmenü zeigt unter dem Projekt den Bezug zum gewählten Meilenstein (Standard: aktueller Abschnitt) und je Bereich offene Lieferobjekte, z. B. „M1: 2 offen“. Bereichsseiten zeigen oben „Benötigt für …“.
- **Übersicht (Cockpit):** Aktueller Abschnitt mit Fortschrittsbalken, bis zu drei nächste Schritte, gleich hohe Kennzahlenkarten (nächste Termine, Top-Risiken, offene Entscheidungen, Aufgaben).
- **Aufgaben:** Kanban nach Status Offen / In Arbeit / Erledigt.
  - Bedienung: Ziehen zwischen Spalten; Tastatur-Alternative über die Status-Auswahl auf der Karte. „Erledigt“ zeigt „Abgeschlossen von … am …“, Zurückziehen öffnet wieder (mit Verlaufseintrag).
  - Anlegen und Bearbeiten: „+ Aufgabe“ je Spalte; Karte anklicken öffnet das Detailpanel. Darin lassen sich Titel, Beschreibung, Fälligkeit, Priorität, Bucket, Meilenstein und mehrere Zuständige bearbeiten, Kommentare hinzufügen und der Verlauf einsehen. Speichern, Abbrechen und Löschen (mit Bestätigung).
  - Finden: Filter (Bucket, Person, Meilenstein, Priorität, „nur meine“), Suche, Zähler je Spalte, Umschalter Board/Liste; die Liste ist nach Fälligkeit sortierbar.
  - Speicherung: alles nur in diesem Browser (localStorage). „Beispieldaten zurücksetzen“ stellt den Ausgangszustand her.
- Weitere Bereiche wie in v2:
  - Steckbrief & Auftrag.
  - Kommunikation mit Stakeholder- und Kommunikationsmatrix und RACI nach Projektrollen.
  - Termine & Zeitstrahl.
  - Risiken & Chancen mit Matrix 3×3.
  - Änderungen & Entscheidungen.
  - Platzhalter: Produkt & Pilot, Berichte, Dokumente, Abschluss.
- Dateien: `journey-data.js` (Beispieldaten), `journey.js` (Projektbereiche und Meilensteine), `journey.css` (Stile). Board und Detailpanel liegen in `app.js`.

