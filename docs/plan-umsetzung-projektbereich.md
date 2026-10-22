# Plan: Umsetzung des Projektbereichs in der echten Anwendung

Status: **Vorschlag des Projektleiters**, Stand 22.10.2026. Grundlage: Entscheidung 006 und die Skizze F19 v3. Die Reihenfolge entscheidet der Benutzer. Jede Etappe folgt dem bewährten Ablauf: Abnahmekriterien → Umsetzung (Entwickler) → Tests, Browserprüfung und Review → Benutzerabnahme → Commit.

## Vorab: Datenmodell klären (Softwarearchitekt, nur Konzept)

Kurzer Architekturauftrag mit Entscheidungsvorlage zu:
- **Meilenstein-Vorlage:** Standard M0–M5 mit Standard-Lieferobjekten; je Projekt anpassbar (Meilensteine ergänzen oder ausblenden, Lieferobjekte ergänzen)?
- **Lieferobjekt:** Verweis auf ein Objekt in einem Bereich (z. B. Projektauftrag, RACI) mit abgeleitetem Status, oder manuell gepflegter Status?
- **Freigaben:** eigenes Objekt mit Ampel, Entscheidung, Beteiligten, Auflagen, Gültigkeit; Verhältnis zu Planversionen (genehmigter Plan).
- **Termine:** ursprünglicher Plan, genehmigter Plan, Prognose und Ist, historisiert (Entwurf F in `docs/entwurf-nacharbeit.md`).
- **Rollenkatalog** für RACI: global vorgegeben und je Projekt erweiterbar.

## Etappen

| Nr. | Etappe | Inhalt | Abhängigkeit |
| --- | --- | --- | --- |
| 4a | **Projektnavigation, Meilensteine und Termine** | Unterpunkte im Menü; Orientierungsleiste M0–M5; Meilensteinseiten mit Lieferobjekten (zunächst Katalog und manueller Status); Termine & Zeitstrahl mit Plan, genehmigtem Plan, Prognose und Ist, historisiert; Freigaben mit Ampel; einfache Übersicht als Cockpit | Datenmodell |
| 4b | **Steckbrief & Auftrag** | strukturierte Felder (Zielbild, Umfang, Kritikalität; Ziele, Scope/Out-of-Scope, Business Case, Rollen, Toleranzen, Phasenplan); Änderungen nachvollziehbar; als Lieferobjekt für M0/M1 erkennbar | 4a |
| 5 | **Aufgabenboard neu** | Status-Kanban (Offen, In Arbeit, Erledigt) mit Ziehen, auch per Finger zu prüfen; schnelles Anlegen; Detailbearbeitung; Priorität; Kommentare; Filter, Suche, Board/Liste; Meilensteinbezug; F23 bleibt erhalten | V07b |
| 6 | **Kommunikation** | Stakeholderregister und Einfluss-Interesse-Matrix (F20); Kommunikationsmatrix; RACI rollenbasiert mit Prüfregel (F21) | 4a |
| 7 | **Risiken & Chancen** | Liste mit Typ, Ursache, Auswirkung, Maßnahme, Verantwortlich und zeitlicher Nähe; 3×3-Matrix; unbewertet grau (F11) | 4a |
| 8 | **Änderungen & Entscheidungen** | Change- und Entscheidungslog, offene Punkte/Issues, Verknüpfung mit Freigaben | 4a |
| 9 | Produkt & Pilot, Berichte und PDF, Dokumente und Dateien, Abschluss & Lessons Learned | inkl. PDF-Prototyp W-C und Dateiablage F10 | 4a–8 |
| 10 | Management-Übersicht, Erinnerungsmails, Monitoring F17, Logo-Animation F18 | wie bisher geplant | |

Etappe 2 (Arbeitsplatz) geht im Umbau von Übersicht und Board teilweise auf. Die verbleibenden Punkte werden nach Feedback des Benutzers ergänzt.

## Empfehlung

Mit dem **Datenmodell-Konzept** beginnen und danach **Etappe 4a** umsetzen, weil Meilensteine, Lieferobjekte und Termine das Gerüst für alle anderen Bereiche sind. **Etappe 5 (Board)** kann danach oder parallel folgen, weil sie unabhängig vom neuen Datenmodell ist und dem Benutzer im Alltag am meisten hilft.

## Offene Fragen an den Benutzer

1. Soll eine Freigabe ohne alle Pflichtdokumente **möglich sein, aber eine Warnung zeigen** (Empfehlung) oder blockiert werden?
2. Sollen Meilensteine **je Projekt anpassbar** sein (Empfehlung), oder gelten immer genau M0–M5?
3. Welche Etappe zuerst: **4a Meilensteine und Termine** (Empfehlung) oder **5 Aufgabenboard**?
