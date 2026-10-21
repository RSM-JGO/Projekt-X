# Releaseprozess

Status: Vorbereitungsentwurf. Die Rolle Releasemanager ist gewünscht; konkrete Pipeline und technische Freigabemechanismen sind noch nicht beschlossen oder implementiert.

## Zuständigkeiten

- Projektleiter: koordiniert Umfang und Reihenfolge, ist zentraler Ansprechpartner.
- Product Owner: konkretisiert den fachlichen Umfang und Abnahmekriterien.
- Entwickler: stellt die Änderung und technische Nachweise bereit.
- Tester und Reviewer: liefern unabhängige Prüfungen und Befunde.
- Releasemanager: bündelt Nachweise, plant die Bereitstellung und gibt eine begründete Release-Empfehlung.
- Benutzer: entscheidet über fachliche Abnahme und beauftragt produktive Veröffentlichung. Ein KI-Agent darf diese Entscheidung nicht selbst als erteilt dokumentieren.

## Vorgeschlagener Ablauf

1. Release-Umfang aus dem gemeinsamen Backlog zusammenstellen.
2. Anwendungsversion mit Commit und gegebenenfalls unveränderlicher Build-Kennung festhalten.
3. Automatische Prüfungen, Testergebnisse und Reviewer-Befunde prüfen.
4. Geprüfte Version auf Dev bereitstellen, Bedienung und relevante Abläufe nachprüfen.
5. Release Notes, verbleibende Einschränkungen, Migrationen und Rückfallmöglichkeit verständlich zusammenfassen.
6. Prod-Bereitstellung nach ausdrücklichem Auftrag mit genau der geprüften Anwendungsversion ausführen.
7. Nachprüfung auf Prod durchführen und Ergebnis festhalten.

Dev und Prod nutzen getrennte Daten, Dateien, Secrets und Mailkonfigurationen. Eine Code-Rückkehr ersetzt keine Datenwiederherstellung. Die konkrete Pipeline soll ohne regelmäßig manuell eingegebene Serverbefehle bedienbar sein, sofern die gewählte Architektur das zulässt. Manuelles Starten einer Pipeline und eine unabhängige technische Freigabesperre sind unterschiedliche Mechanismen.

## Vorlage für einen Release-Nachweis

- Version und zugehöriger Commit/Build.
- Enthaltene Backlogeinträge und verständliche Release Notes.
- Dev-Bereitstellung und Prüfung mit Zeitpunkt und Nachweisen.
- Bekannte Fehler und ihre Bewertung.
- Migrationen und relevante Konfigurationsänderungen.
- Rückfallplan und gegebenenfalls bestätigte Sicherung.
- Benutzerauftrag für Prod, sofern erteilt.
- Tatsächliche Prod-Bereitstellung und Nachprüfung, sobald erfolgt.

Noch kein produktiver Release oder Deployment beauftragt. Für kleine Änderungen den Nachweis angemessen kurz halten; das gemeinsame Backlog und den Arbeitsstand wiederverwenden.
