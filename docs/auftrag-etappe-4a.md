# Auftrag: Etappe 4a – Projektnavigation, Meilensteine und Termine

Status: Vom Benutzer am 22.10.2026 beauftragt. **Umgesetzt, geprüft und vom Benutzer am 22.10.2026 abgenommen.** Grundlage:
- Entscheidung 006 mit Ergänzungen;
- `docs/entwurf-datenmodell-projektbereich.md` (bestätigt);
- Skizze F19 v3 in `design/` als Gestaltungsvorlage;
- Styleguide-Regeln in `docs/styleguide-briefing.md`.

## Umfang

1. **Datenmodell** laut Konzept: Standardkatalog, Meilenstein, Lieferobjekt, Freigabe, Planversion, Planeintrag, Terminänderung. Dazu die Datenmigration, die Katalog und M0–M5 für bestehende Projekte anlegt, und Planversion 1 als **Entwurf**.
2. **Projektnavigation:**
   - Die Unterpunkte des geöffneten Projekts stehen im Hauptmenü, mit Status und „M1: x offen“.
   - Am Handy gibt es ein Projektmenü.
   - Noch nicht gebaute Bereiche erscheinen als „folgt später“ und lassen sich nicht anklicken. Gebaute Bereiche in 4a: Übersicht, Termine & Zeitstrahl, Aufgaben (bisheriges Board, bis Etappe 5), Meilensteinseiten.
3. **Orientierungsleiste** M0–M5 mit Ampel; jeder Meilenstein ist anklickbar.
4. **Meilensteinseite:**
   - Ziel und Lieferobjekte mit Status und Pflicht-Kennzeichen; Projektleitung und Admin ändern alles, die verantwortliche Mitarbeiterin nur den Status ihrer eigenen Lieferobjekte.
   - Fortschritt und Vor/Zurück.
   - Freigabe erteilen mit Warnung und Bestätigung bei fehlenden Pflichtdokumenten; Freigaben sind unveränderlich, eine Korrektur ersetzt die alte Freigabe.
   - Meilenstein ergänzen und ausblenden.
5. **Termine & Zeitstrahl:**
   - Projektzeitraum und Meilensteintermine mit ursprünglichem Plan, genehmigtem Plan, Prognose und Ist.
   - Planentwurf bearbeiten und genehmigen.
   - Prognose und Ist mit Begründung ändern; Verlauf sichtbar.
   - Einfacher Zeitstrahl.
6. **Übersicht (Cockpit, einfache Fassung):**
   - aktueller Abschnitt mit Fortschritt;
   - nächste Schritte (offene Pflichtdokumente);
   - Kacheln für nächste Termine, offene Freigaben und Aufgaben;
   - Team bzw. Mitglieder erreichbar.
7. Bisherige Projektseite und Mitgliederverwaltung bleiben funktionsfähig und werden in die neue Navigation eingebunden.

## Abnahmekriterien

1. Jedes bestehende und jedes neue Projekt hat M0–M5 mit Standard-Lieferobjekten. Änderungen am Standardkatalog verändern bestehende Projekte nicht.
2. Ein Meilenstein lässt sich ergänzen und ausblenden, aber nicht löschen. Ausgeblendete erscheinen nicht in Leiste und Menü, ihre Freigaben bleiben erhalten.
3. Den Status eines Lieferobjekts ändern Projektleitung und Admin, außerdem die verantwortliche Mitarbeiterin bei ihrem eigenen. Alle anderen erhalten 403, Nichtmitglieder 403 bzw. 404 wie bisher.
4. Eine Freigabe bei fehlenden Pflichtdokumenten verlangt eine bestätigte Warnung. Die fehlenden Dokumente sind an der Freigabe eingefroren und bleiben sichtbar, auch wenn sie später nachgereicht werden. Orange verlangt Auflagen.
5. Freigaben lassen sich nicht ändern oder löschen, auch nicht per direkter Anfrage oder in der Datenbank. Eine Korrektur ist eine neue Freigabe mit Verweis auf die ersetzte.
6. Freigaben erteilen nur Projektleitung und Admin. Admin-Aktionen sind gekennzeichnet und protokolliert.
7. Der ursprüngliche Plan ist die erste genehmigte Version und ändert sich durch spätere Genehmigungen nicht. Der genehmigte Plan ist die neueste. Genehmigte Versionen sind unveränderlich.
8. Jede Änderung von Prognose oder Ist erzeugt einen Verlaufseintrag mit altem und neuem Wert, Person und Begründung.
9. Der aktuelle Meilenstein ist der erste sichtbare ohne gültige grüne oder orange Freigabe. Rot oder abgelaufen zählt als offen.
10. Ein Meilenstein ohne Lieferobjekte oder ohne Termin wird als „nicht bewertet“ angezeigt, nie als erledigt bzw. grün.
11. Projektzeitraum und genehmigter Plan laufen nicht auseinander; ein Test prüft das.
12. Die Gestaltungsregeln gelten. Hell und Dunkel funktionieren, 375 px ohne Überbreite. Alle bisherigen Tests bleiben grün.

## Nicht enthalten

- Steckbrief & Auftrag (4b), neues Board (5), Kommunikation, Risiken, Entscheidungslog und die übrigen Bereiche.
- Pflegeseite für den Standardkatalog.
- Vorgänge.
- Aufgabe ↔ Meilenstein.

## Prüfnachweis (22.10.2026)

- **Umsetzung** durch den Entwickler (neue App `milestones`, Migrationen 0001–0004).
- **Tests:** 872 grün, vom Projektleiter erneut ausgeführt; ruff, `check` und `makemigrations --check` sauber; `migrate` auf Dev ohne offene Schritte.
- **Browserprüfung durch den Projektleiter:**
  - Projektmenü mit Unterpunkten und „M2: x offen“.
  - Meilensteinleiste; M1-Seite mit Lieferobjekten, Pflicht-Kennzeichen und oranger Freigabe samt eingefrorener Fehlliste.
  - Termine mit ursprünglichem und genehmigtem Plan, Prognose und Zeitstrahl.
  - Darkmode; 375 px ohne Überbreite mit Projektmenü.
  - Projekte ohne Termine zeigen „nicht bewertet“, nie grün.
  - Keine Konsolenfehler.
- **Review:** keine Rechtelücke. Sieben Befunde behoben:
  - Warnbestätigung wird bei geänderter Fehlliste neu verlangt.
  - Kein ✓ ohne Termin.
  - Ausgeblendete Meilensteine stehen im Planentwurf.
  - DB-Trigger hält Projektzeitraum und genehmigten Plan synchron.
  - Ein bearbeiteter Entwurf wird nicht still überschrieben.
  - Migration ohne laufenden Code.
  - Bei gültiger Freigabe nur Korrektur mit Ersetzung.
- **Vom Projektleiter festgelegt:** Bei gültiger Freigabe ist nur eine Korrektur möglich. Eine Korrektur friert die Fehlliste zum Korrekturzeitpunkt ein.
- **Nicht geprüft:** echte parallele Genehmigungen; Rückwärtsmigration (0003 bewusst nicht umkehrbar); Screenreader.
