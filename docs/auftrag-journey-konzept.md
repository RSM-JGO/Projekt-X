# Auftrag: Konzept Projekt-Journey und Menüstruktur (F19)

Status: In Arbeit seit 21.10.2026, auf Wunsch des Benutzers („Lass uns weiter machen“). **Konzept, kein Produktivcode.**

## Ziel

Der Benutzer soll beurteilen können, wie Projekt X durch ein Projekt führt, vom Start bis zum Abschluss, und wie der Projektbereich aufgebaut ist. Dazu gibt es eine klickbare Skizze mit zwei Varianten. Der Benutzer wählt danach eine Variante, kombiniert beide oder verwirft sie.

## Arbeitsannahmen für die Skizze

Sie gelten bis zur Entscheidung des Benutzers und sind **keine** Festlegung:

1. Die Journey gibt **Orientierung** und schlägt den nächsten Schritt vor. Sie erzwingt keine Schritte und **beschließt kein Phasenmodell** (F12 bleibt offen).
2. Die **RACI-Matrix** wird beispielhaft für Aufgaben, Meilensteine und Entscheidungen gezeigt, damit der Bezug beurteilt werden kann.
3. Die **Risiko-Matrix** wird als 3×3 gezeigt; 5×5 ist als Umschalter in der Skizze sichtbar.
4. Die **Stakeholder** werden als Register und als Einfluss-Interesse-Matrix (2×2) gezeigt. Stakeholder sind keine Benutzerkonten.

## Bausteine

Steckbrief, Stakeholder, RACI, Meilensteine und Termine, Aufgaben, Risiken, Entscheidungen und Freigaben, Statusberichte, Dokumente, Abschluss und Lessons Learned.

In der Skizze ist für jeden Baustein erkennbar, ob er **in Projekt X schon vorhanden ist** (Aufgaben, Mitglieder) oder **noch fehlt**.

## Varianten

| | Variante A „Projekt-Cockpit mit Reitern“ | Variante B „Geführte Journey-Leiste“ |
| --- | --- | --- |
| Aufbau | Projektseite mit Reitern für jeden Baustein; oben eine schmale Fortschrittsleiste Start → Planung → Umsetzung → Abschluss | Seitenleiste im Projekt, nach Journey-Abschnitten gruppiert; je Baustein ein Stand (erledigt, offen, nicht begonnen) und ein Hinweis „Nächster empfohlener Schritt“ |
| Stärke | Schneller Direktzugriff, gewohnte Bedienung | Führt durch das Projekt, Lücken fallen auf |
| Schwäche | Weniger Führung; viele Reiter | Mehr Platzbedarf; auf dem Handy ein ausklappbares Menü |

## Abnahmekriterien für das Konzept

1. Beide Varianten sind in `design/` klickbar, mit gekennzeichneten Beispieldaten, in Hell und Dunkel und auf dem Handy bedienbar.
2. Alle Bausteine sind zugeordnet; vorhanden und fehlend ist unterscheidbar.
3. Beispielinhalte gibt es für Stakeholdermatrix, RACI-Matrix und Risiko-Matrix.
4. Die Gestaltungsregeln aus `docs/styleguide-briefing.md` gelten: Logo, Schrift dunkelgrau, Statusfarben Grün/Orange/Rot/Grau, gleich hohe Karten.
5. Es gibt eine Entscheidungsvorlage mit Vor- und Nachteilen und den offenen Fragen. Die Entscheidung trifft der Benutzer.

## Stand und Entscheidungsvorlage (21.10.2026)

**Skizze umgesetzt** in `design/` (`journey.js`, `journey-data.js`, `journey.css`) durch den Entwickler.

**Vom Projektleiter im Browser geprüft:**
- Umschalter A/B mit gespeicherter Auswahl.
- Variante A: Orientierungsleiste, Reiter, Risiko-Matrix 3×3 mit Statusfarben.
- Variante B: gruppierte Leiste mit ✓/●/○ und Text, Karte „Nächster empfohlener Schritt“.
- Darkmode; 375 px ohne Überbreite, in B mit aufklappbarer Bausteinauswahl; keine Konsolenfehler.

**Nicht geprüft:** Screenreader, vollständige Tastaturbedienung.

**Entscheidungen des Benutzers** (Empfehlung des Projektleiters in Klammern):
1. **Variante:** A, B oder eine Mischung? *(Empfehlung: B als Grundstruktur für Führung durchs Projekt, mit der kompakten Orientierungsleiste aus A oben.)*
2. **Journey:** nur Orientierung oder Schritte vorgeben? *(Empfehlung: Orientierung mit empfohlenem nächstem Schritt, keine Pflichtschritte, solange das Phasenmodell offen ist.)*
3. **RACI-Bezug:** Aufgaben, Meilensteine, Entscheidungen? *(Empfehlung: Meilensteine und Entscheidungen; für einzelne Aufgaben reicht die Zuständigkeit.)*
4. **Risiko-Matrix:** 3×3 oder 5×5? *(Empfehlung: 3×3 für den Start, weil es einfacher zu pflegen ist; 5×5 lässt sich später erweitern.)*

## Feedback des Benutzers zu Version 1 (21.10.2026) → Version 2 in Arbeit

- **Navigation:** Beide Varianten sind noch nicht ideal. Die Projektbereiche sollen **Unterpunkte im Menü** sein. Variante B geht mehr in die gewünschte Richtung.
- **Neue Gruppierung:**
  - Stakeholder und RACI gehören in den Bereich **Kommunikation**.
  - **Projektsteckbrief und Projektauftrag** gehören zusammen.
  - **Termine und Zeitstrahl** gehören zusammen.
  - **Risikoliste und Risiko-Matrix** gehören zusammen.
  - Das **Aufgabenboard** wird ein eigener Bereich.
- **RACI:** rollenbasiert, also welche **Rolle** welche Verantwortung hat. Die Rollen sollen aus dem Word-Dokument des Benutzers kommen; das Lesen des Rollout-Handbuchs wurde von der Werkzeugfreigabe blockiert, deshalb vorerst Beispielrollen.
- **Risiko-Matrix:** 3×3 (vom Benutzer entschieden).
- Version 2 der Skizze setzt das um. Offen bleiben die Rollen aus dem Handbuch und die Frage, ob nur Orientierung oder Pflichtschritte gewünscht sind.
- **Ergänzung 22.10.2026:** Der Benutzer hat seinen ursprünglichen Projektablauf (M0–M5) und das Handbuch bereitgestellt; Zusammenfassung in `docs/fachliche-orientierung-projektablauf.md`.
  - Das ist eine **Orientierungshilfe, keine harte Anforderung**, aus Sicht des **Projektmanagements, nicht des Rolloutmanagements**.
  - Version 2 nutzt den Ablauf für die Orientierungsleiste und für den „nächsten empfohlenen Schritt“.
  - Die Bereiche lauten jetzt:
    - Steckbrief & Auftrag
    - Kommunikation (Stakeholder, Kommunikationsmatrix, RACI)
    - Termine & Zeitstrahl
    - Aufgaben
    - Risiken & Chancen
    - Änderungen & Entscheidungen (Freigaben mit Ampel)
    - Produkt & Pilot
    - Berichte, Dokumente
    - Abschluss & Lessons Learned
- Erledigte offene Fragen:
  - **RACI-Bezug:** rollenbasiert je Aktivität.
  - **Chancen:** werden mit den Risiken erfasst.
  - **Risiko-Matrix:** 3×3.
- **Version 2 umgesetzt** (22.10.2026, Entwickler) und vom Projektleiter im Browser geprüft:
  - 11 Projektbereiche als Unterpunkte im Hauptmenü mit Statusmarkern.
  - Orientierungsleiste M0–M5 mit Freigabe-Ampel.
  - RACI nach Rollen mit Prüfregel.
  - Risiken & Chancen mit 3×3-Matrix; Chancen nicht rot, unbewertete grau.
  - Darkmode.
  - Handy: 375 px ohne Überbreite, mit „Projektmenü“ und kompakter Leiste „Abschnitt 3 von 6“.
  - Keine Konsolenfehler.
  - **Nicht geprüft:** Screenreader, vollständige Tastaturbedienung.

## Feedback des Benutzers zu Version 2 (22.10.2026) → Version 3

- Die Richtung stimmt.
- **Meilensteine M0 bis M5 sind nicht anklickbar.** Man soll sich durch die Abschnitte klicken können.
- **Pflichtdokumente bzw. Lieferobjekte** je Meilenstein sind nicht erkennbar.
- Das **Zusammenspiel** zwischen Menü (Bereiche) und Meilensteinleiste fehlt.
- Die **Übersicht** gefällt noch nicht.
- Das **Aufgabenboard** muss überarbeitet werden.

**Ansatz für Version 3 (Vorschlag des Projektleiters):**
- **Meilenstein-Seiten:** Jeder Meilenstein ist anklickbar. Die Seite zeigt das Ziel des Abschnitts, die **Lieferobjekte mit Status** (vorhanden, in Arbeit, fehlt) und Links in den jeweiligen Bereich sowie den Freigabeblock mit Ampel.
- **Zusammenspiel:** Das Menü zeigt beim gewählten Meilenstein, welche Bereiche dafür noch offene Lieferobjekte haben. Jede Bereichsseite zeigt „Benötigt für M1 …“.
- **Übersicht neu:** ein Cockpit mit aktuellem Abschnitt und Fortschritt der Lieferobjekte, den nächsten drei Schritten und kompakten Kennzahlen (nächste Termine, Top-Risiken, offene Entscheidungen, Aufgaben).
- **Aufgabenboard neu:** Kanban nach Status (Offen, In Arbeit, Erledigt) mit Filtern nach Bucket, Person und Meilenstein; der Meilensteinbezug ist auf der Karte sichtbar. Offene Frage an den Benutzer: Was stört am Board konkret?
- Benutzer 22.10.2026: Abschnitt M4 heißt **„Rollout“**, nicht „Einführung“.
- **Version 3 umgesetzt** (22.10.2026) und vom Projektleiter im Browser geprüft:
  - Meilensteine M0–M5 anklickbar, mit eigener Seite: Lieferobjekte mit Pflicht-Kennzeichen und Fortschritt (z. B. „2 von 4“), Freigabeblock, Vor/Zurück.
  - Menü zeigt „M1: 2 offen“; M4 heißt „Rollout“.
  - Board nach Status:
    - Verschieben über die Drop-Logik geprüft, mit simulierten Zieh-Ereignissen.
    - „+ Aufgabe“ legt an; das Detailpanel hat alle Felder.
    - Handy: Spalten untereinander, Status per Auswahlfeld, keine Überbreite.
  - Keine Konsolenfehler.
  - **Nicht geprüft:** echtes Ziehen mit der Maus, weil das Automatisierungswerkzeug kein natives Ziehen auslöst; Screenreader.
  - **Hinweis:** Auf Touch-Geräten funktioniert Ziehen mit HTML5-Drag&Drop nicht. Dort wird der Status per Auswahlfeld geändert; für die echte Anwendung ist Touch-Ziehen gesondert zu prüfen.
