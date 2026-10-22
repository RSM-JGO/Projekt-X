# Struktur des Projektbereichs und Projekt-Journey

Datum: 22. Oktober 2026. Status: **beschlossen** durch den Benutzer („Version 3 passt“). Grundlage: klickbare Skizze F19 Version 3 in `design/`, `docs/auftrag-journey-konzept.md`, `docs/fachliche-orientierung-projektablauf.md`.

## Entscheidung

1. **Navigation:** Die Bereiche eines Projekts erscheinen als **Unterpunkte im Hauptmenü** unter dem geöffneten Projekt. Jeder Unterpunkt zeigt einen Status (✓ erledigt, ● offen, ○ nicht begonnen). Auf dem Handy sind sie über ein „Projektmenü“ erreichbar.
2. **Bereiche in dieser Reihenfolge:**
   1. Übersicht als Cockpit
   2. Steckbrief & Auftrag
   3. Kommunikation: Stakeholder, Kommunikationsmatrix, RACI
   4. Termine & Zeitstrahl
   5. Aufgaben
   6. Risiken & Chancen
   7. Änderungen & Entscheidungen
   8. Produkt & Pilot
   9. Berichte
   10. Dokumente
   11. Abschluss & Lessons Learned
3. **Orientierungsleiste** mit sechs Abschnitten und Meilensteinen: Auftragsklärung M0, Initiierung M1, Vorbereitung M2, Pilot M3, **Rollout** M4, Abschluss M5.
   - Jeder Meilenstein ist anklickbar und hat eine eigene Seite mit Ziel, **Lieferobjekten bzw. Pflichtdokumenten** samt Status und Link in den Bereich, Fortschritt und Freigabeblock.
   - Die Freigabe-Ampel ist **Orientierung, kein festes Phasenmodell** (F12 bleibt offen).
4. **Zusammenspiel:** Das Menü zeigt, welche Bereiche für den aktuellen Meilenstein noch offene Lieferobjekte haben. Bereichsseiten zeigen, für welchen Meilenstein sie benötigt werden.
5. **Freigabe-Ampel:** Grün = erteilt, Orange (statt Gelb) = unter Auflagen, Rot = keine Freigabe ohne Ausnahmeentscheidung. Jede Freigabe hat Entscheidung, Datum, Beteiligte, Grundlage, Auflagen und Gültigkeit.
6. **RACI** ist rollenbasiert (Rolle × Aktivität, genau ein A je Zeile). **Risiken und Chancen** stehen gemeinsam in einer Liste mit zeitlicher Nähe; die Matrix hat **3×3** Felder.
7. **Aufgabenboard** als eigener Bereich: Spalten nach Status (Offen, In Arbeit, Erledigt), Ziehen zum Verschieben, schnelles Anlegen, Detailbearbeitung, Priorität, Kommentare, Filter, Board/Liste.
8. **Sicht des Projektmanagements:** Die operative Rollout- und Terminplanung bleibt beim Rolloutmanagement und wird nicht nachgebaut.

## Konsequenzen

- Meilensteine und Lieferobjekte brauchen ein Datenmodell mit **Vorlage**: Standard-Meilensteine M0–M5 und Standard-Lieferobjekte, je Projekt anpassbar. Das ist vor der Umsetzung mit dem Softwarearchitekten zu klären.
- Termine bleiben historisiert: ursprünglicher Plan, genehmigter Plan, Prognose und Ist (CLAUDE.md).
- „Pflicht“ bei Lieferobjekten ist eine **Orientierung**. Ob eine Freigabe ohne alle Pflichtdokumente möglich ist, entscheidet die Projektleitung bzw. Freigabeinstanz; die Anwendung warnt, blockiert aber nicht. Das ist ein Vorschlag des Projektleiters und noch zu bestätigen.
- Die bestehende Projektdetailseite und das Bucket-Board aus V07b werden durch diese Struktur ersetzt bzw. umgebaut.

Betroffen: F19 (erledigt als Konzept), F11, F20, F21, Etappen 4 bis 8.

## Ergänzende Entscheidungen des Benutzers (22.10.2026)

Der Benutzer hat die Empfehlungen des Projektleiters übernommen:
1. Eine **Freigabe ohne alle Pflichtdokumente ist möglich**, zeigt aber eine **deutliche Warnung**; fehlende Pflichtdokumente werden an der Freigabe vermerkt. Es gibt keine Blockade.
2. **Meilensteine sind je Projekt anpassbar.** Standard ist M0–M5; Meilensteine lassen sich je Projekt ergänzen und ausblenden.
3. **Reihenfolge:** zuerst das Datenmodell-Konzept, dann Etappe 4a (Projektnavigation, Meilensteine, Termine).
