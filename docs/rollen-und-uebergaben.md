# Claude Rollen und Übergaben

Die sieben Rollendateien liegen in .claude/agents/. Alle sieben wurden in der neuen Claude-Sitzung „Projektleitung und Rollenüberblick“ als tatsächlich geladene Unteragenten bestätigt. Drei beratende Rollen wurden bereits ausgeführt. Der Hauptdialog hat den Projektleitungsmodus übernommen. Es sind Entwicklungsrollen, keine Benutzerrollen der späteren Plattform. Es werden keine separaten Claude-Konten benötigt.

## Zuständigkeiten

| Rolle | Auftrag | Ergebnis |
| --- | --- | --- |
| Projektleiter | Zentraler Ansprechpartner im Hauptdialog; Änderungswünsche, Arbeitsstand und Fachrollen koordinieren | Verständlicher Arbeitsplan, Übergaben und aktueller Arbeitsstand; Unteragent project-lead unterstützt |
| Product Owner | Anforderungen konkretisieren und gemeinsames Backlog pflegen helfen | Arbeitsauftrag mit Nutzen, Umfang, Abnahmekriterien und offenen Fragen |
| Enterprise-Architekt | Systemlandschaft, Integrationen, Datenverantwortung und Betriebsrahmen prüfen | Systemgrenzen, Datenflüsse, Annahmen und Integrationsentscheidungen |
| Softwarearchitekt, Agent architect | Anwendungsstruktur, Datenmodell, Rechte und technische Umsetzung entwerfen | Architekturvorschlag und dokumentierte Entscheidungen |
| Entwickler | Einen beauftragten Backlogeintrag umsetzen | Kleine überprüfbare Änderung mit Prüfnachweisen |
| Tester | Verhalten gegen Abnahmekriterien prüfen | Testergebnisse und reproduzierbare Fehler |
| Reviewer | Änderungen unabhängig auf konkrete Fehler prüfen | Priorisierte Befunde mit Fundstellen und Auswirkungen |

Der Hauptdialog übernimmt die Projektleitung, delegiert und überträgt Ergebnisse der beratenden Rollen in Dateien. Product Owner, Architekten und Reviewer haben nur lesende Werkzeuge; sie bearbeiten das Backlog nicht selbst. project-lead kann Projektunterlagen pflegen, aber keine weiteren Agenten aufrufen. Der Entwickler kann nach Auftrag schreiben; der Tester kann Testbefehle ausführen. Werkzeugzugriff allein ist keine Erlaubnis für produktive Änderungen.

## Gemeinsames Backlog

docs/backlog.md enthält Priorität, Zustand und Abnahmekriterien. Rollen führen keine getrennten Aufgabenlisten. Der Benutzer entscheidet Prioritäten und fachliche Abnahme; Claude schlägt vor und dokumentiert.

## Übergabe pro Arbeitsauftrag

1. Backlog-ID, Ziel und ausdrücklich ausgeschlossener Umfang.
2. Relevante Anforderungen, Dateien und Architekturentscheidungen.
3. Abnahmekriterien und erwartete Prüfungen.
4. Änderungen beziehungsweise Vorschlag und ausgeführte Prüfschritte.
5. Offene Fragen, Befunde und nächster Bearbeiter.

Ein Arbeitsauftrag ist erst umgesetzt, wenn seine Kriterien erfüllt sind. Eine fachliche Abnahme durch den Benutzer darf nicht erfunden werden. Große technische Änderungen erhalten eine Architekturprüfung; kleine Änderungen brauchen nicht jedes Mal alle Rollen. Am Anfang erfolgen Übergaben nacheinander, damit sich schreibende Arbeiten nicht überschneiden.
