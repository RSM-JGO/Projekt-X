# Fachliche Orientierung: Projektablauf aus Sicht der Projektleitung

Quelle: Text des Benutzers vom 22.10.2026 („So war mal ein Ursprungsgedanke“) und die Abschnitte zu Rollen und RACI aus seinem Rollout-Handbuch. Die Inhalte sind hier **sinngemäß und ohne firmenspezifische Bezeichnungen** zusammengefasst; das Originalhandbuch kommt nicht in Git (CLAUDE.md).

**Status: Orientierungshilfe, keine harte Anforderung** (Aussage des Benutzers). Es geht um das **Projektmanagement, nicht um das Rolloutmanagement**. Das allgemeine Phasenmodell (F12) bleibt offen; die Meilensteine dienen als Orientierung für die Journey in Projekt X.

## Ablauf mit Meilensteinen

| Abschnitt | Meilenstein | Typische Ergebnisse der Projektleitung |
| --- | --- | --- |
| 1. Auftragsklärung | M0 Start Projektauftrag | Projektsteckbrief (Grundinformationen, Zielbild, Umfang); Stakeholder identifizieren und analysieren; Stakeholdermatrix und Kommunikationsmatrix (Name, Abteilung, Aufgabe im Projekt, erforderliche Kommunikation); erste Einschätzung der Kritikalität |
| 2. Projektinitiierung | M1 Projektfreigabe | Projektauftrag (Ziele, Scope und Out-of-Scope, Business Case, Rollen, Toleranzen, Phasenplan); RACI-Matrix; Risikoliste mit Gefahren **und Chancen** (Ursache, Auswirkung, Maßnahme, Verantwortung; Bewertung nach Wahrscheinlichkeit, Auswirkung und zeitlicher Nähe); Kommunikationsmanagement (Zielgruppen, Formate, Häufigkeit, Kanäle, Verantwortliche); Entscheidung über die Projektfreigabe |
| 3. Produkt- und Pilotvorbereitung | M2 Pilotfreigabe | Produktbeschreibung bzw. Spezifikation, Abnahmekriterien, Pilotvorbereitung; Abstimmung der Voraussetzungen mit Fachbereichen, IT-Betrieb und weiteren Beteiligten; Fortschritt, Risiken, offene Punkte und Abhängigkeiten verfolgen |
| 4. Pilot und Nacharbeit | M3 Skalierungsfreigabe | Pilot planen und abnehmen; Pilotbericht; Defektliste mit Maßnahmen; Go-/No-Go-Entscheidung vorbereiten und dokumentieren |
| 5. Rollout | M4 Rolloutfreigabe | Übergreifende Projektsteuerung: Ziele, Fortschritt, Risiken, Kosten, Entscheidungen; Änderungen an Scope, Terminen, Kosten, Qualität oder Risiken im Change- und Entscheidungslog; Eskalation bei Abweichungen außerhalb der Toleranzen. Die operative Rollout- und Terminplanung liegt beim Rolloutmanagement und ist **nicht** Teil von Projekt X. |
| 6. Projektabschluss | M5 Abschlussfreigabe | Zielerreichung, tatsächlicher Scope, Business Case, Budget und Nutzen bewerten; offene Entscheidungen und Restpunkte dokumentieren; Lessons Learned und Rückführung in Standards und Vorlagen |

**Übergreifend:** Risiken, Issues, offene Punkte und Änderungen werden durchgehend nachgehalten. Entscheidungen und freigaberelevante Lieferobjekte werden nachvollziehbar dokumentiert.

## Freigaben mit Ampellogik

- **Grün:** Freigabe erteilt.
- **Gelb:** Freigabe unter Auflagen. In Projekt X wird Gelb wie „beobachten“ in **Orange** dargestellt (Farbregeln im Styleguide).
- **Rot:** Keine Freigabe ohne Ausnahmeentscheidung der definierten Entscheidungsebene.

Jede Freigabe wird mit Entscheidung, Datum, Beteiligten, Entscheidungsgrundlage, Auflagen und Gültigkeit dokumentiert.

## Rollen (verallgemeinert)

| Rolle | Kernverantwortung |
| --- | --- |
| Auftraggeber / Lenkungskreis | Geschäftliche Rechtfertigung, Priorität, Budgetrahmen, Entscheidungen außerhalb der Toleranzen |
| Nutzervertretung / Fachbereich | Nutzerbedarf, Akzeptanz, fachliche Abnahme |
| Lösungsverantwortung / IT-Betrieb | Machbarkeit, technische Qualität, Lieferfähigkeit, Betriebsfähigkeit |
| Projektleitung | Tagessteuerung des Projekts innerhalb der freigegebenen Toleranzen |
| Umsetzungsverantwortliche | Lieferung definierter Arbeitspakete, z. B. Rolloutmanagement oder Dienstleister |
| Qualitätssicherung / PMO | Unabhängige Prüfung |
| Projektunterstützung | Ablage, Protokolle, Entscheidungsliste, Reporting |
| Produktverantwortung (Product Owner) | Priorisiert Produktanforderungen und entscheidet fachlich im Produktkontext |

## RACI (Beispiel aus Sicht der Projektleitung, verallgemeinert)

R = führt aus, A = trägt die Gesamtverantwortung, C = wird konsultiert, I = wird informiert. Je Zeile genau ein A.

| Aktivität | Projektleitung | Auftraggeber | Fachbereich/PO | IT-Betrieb | Umsetzung (z. B. Rollout) |
| --- | --- | --- | --- | --- | --- |
| Projektauftrag erstellen | A/R | C | C | C | C |
| Projektfreigabe (M1) entscheiden | R | A | C | C | I |
| Spezifikation freigeben | A | I | R | C | C |
| Pilot planen und abnehmen | A/R | I | R | R | C |
| Go-/No-Go je Meilenstein | A/R | C | C | C | R |
| Änderung außerhalb der Toleranz entscheiden | R | A | C | C | I |
| Betriebsübergabe | A | I | C | R | R |
| Projektabschluss und Lessons Learned | A/R | C | C | C | C |

Die Rollen und Werte sind **Beispiele für die Skizze**. In Projekt X sollen Rollen und RACI je Projekt pflegbar sein.
