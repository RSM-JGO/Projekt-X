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
