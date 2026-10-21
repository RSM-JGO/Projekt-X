# Administratorrechte und Projektsichtbarkeit

Datum: 21. Oktober 2026. Status: **beschlossen** durch den Benutzer nach dem Ausprobieren von V07a. **Ersetzt** in `003-produktregeln-erster-ablauf.md` die Punkte 1 und 2 für den Administrator sowie die Sichtbarkeitsregel „Projektzugriff nur über Mitgliedschaft“.

## Entscheidungen

| Nr. | Thema | Entscheidung |
| --- | --- | --- |
| 1 | Administrator | Der Administrator darf **uneingeschränkt alles**: Projekte anlegen und bearbeiten, Mitglieder und Rollen verwalten, Aufgaben ändern und **auch Freigaben erteilen**. |
| 2 | Persönliche Aufgaben | Der Administrator darf **auch persönliche Aufgaben anderer Personen** sehen und ändern. Für alle anderen bleiben persönliche Aufgaben privat; Teilen ist weiterhin nicht vorgesehen. |
| 3 | Projektliste | **Alle angemeldeten Personen sehen alle Projekte** in der Übersicht. Fremde Projekte erscheinen nur mit **Name, Zeitraum und Projektleitung** und sind als „kein Zugriff“ erkennbar. |
| 4 | Projekt öffnen | **Öffnen dürfen nur aktive Mitglieder** des jeweiligen Projekts, mit jeder Rolle, und der Administrator. Nicht-Mitglieder erhalten „Kein Zugriff“ (HTTP 403). |

Unverändert gilt:
- Innerhalb eines Projekts ändern nur Projektleiter und der Administrator.
- Jedes Projekt braucht mindestens einen aktiven Projektleiter.
- Jede Änderung wird protokolliert; Aktionen des Administrators werden als solche gekennzeichnet.

## Konsequenzen

- Die fachliche Leitplanke in CLAUDE.md „Projektleiter erteilt Freigaben“ wird ergänzt: Freigaben erteilen Projektleiter und Administrator.
- Freigaben und Korrekturen durch den Administrator müssen im Verlauf eindeutig als Administratoraktion erkennbar sein, damit nachvollziehbar bleibt, wer freigegeben hat.
- Persönliche Aufgaben sind für den Administrator einsehbar. Das ist bei späterer Teamnutzung transparent zu machen, zum Beispiel durch einen Hinweis in der Oberfläche.
- Projektnamen, Zeiträume und Projektleitungen sind für alle Konten sichtbar. Vertrauliche Projektnamen müssten später gesondert gelöst werden.
- Abnahmekriterien V07a 4 und 8 sowie V07b 7 und 8 in `docs/auftrag-erster-ablauf.md` sind entsprechend angepasst.

Betroffene Backlogeinträge: V05, V07.
