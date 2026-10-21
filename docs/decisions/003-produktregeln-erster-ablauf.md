# Produktregeln für den ersten Ablauf

Datum: 21. Oktober 2026. Status: **beschlossen, teilweise ersetzt** durch `004-adminrechte-und-projektsichtbarkeit.md` (Punkte 1 und 2 für den Administrator, Projektsichtbarkeit). Der Benutzer hat zu allen vier Fragen die Empfehlung des Projektleiters übernommen („Gehe überall mit deiner Empfehlung mit“).

## Problem

Für den ersten echten Ablauf (Anmeldung, Projekte, gemeinsame Aufgaben) mussten vier offene Produktfragen aus `docs/entwurf-nacharbeit.md` (Abschnitte D bis F) und dem Django-Review entschieden werden.

## Entscheidungen

| Nr. | Frage | Entscheidung | Alternative (nicht gewählt) |
| --- | --- | --- | --- |
| 1 | Darf der Administrator Aufgaben in Projekten korrigieren? | **Ja, als protokollierte Ausnahme.** Jede Korrektur wird mit Person, Zeitpunkt und altem/neuem Wert festgehalten. **Freigaben erteilt der Administrator nie**; sie bleiben beim Projektleiter. Der Administrator liest alle Projekte und verwaltet Mitgliedschaften. | Nur Lesen, oder volle Projektleiterrechte |
| 2 | Dürfen persönliche Aufgaben geteilt werden? | **Vorerst nein.** Eine persönliche Aufgabe ohne Projekt sieht und bearbeitet nur ihr Eigentümer, auch kein Administrator. Zuweisung an andere ist nicht möglich. | Teilen mit ausgewählten Personen |
| 3 | Werden Zeiträume für Arbeitspakete („Vorgänge“) gebraucht? | **Erst später.** Der erste Ablauf kennt Projektzeitraum und Meilensteine; Vorgänge bleiben als Erweiterung vorgesehen. | Vorgänge sofort modellieren |
| 4 | Muss die E-Mail-Adresse eindeutig sein? | **Ja**, ohne Rücksicht auf Groß-/Kleinschreibung. Eine Person hat genau ein Konto; die täglichen Sammelmails hängen daran. | Mehrere Konten je Adresse |

## Konsequenzen

- Das Benutzermodell erhält eine eindeutige E-Mail-Adresse. Das ist jetzt noch einfach, weil keine Benutzerdaten existieren.
- Korrekturen durch den Administrator brauchen von Anfang an einen Protokolleintrag (Aufgabenverlauf bzw. Änderungsprotokoll).
- Rechteprüfung und Tests müssen den Ausschluss des Administrators von persönlichen Aufgaben und von Freigaben abdecken.
- Weiter offen sind die übrigen Detailrechte nach V05, das Phasenmodell und Vorgänge.

Betroffene Backlogeinträge: V05 (teilweise), V07.
