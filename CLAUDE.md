# Arbeitsgrundlage für Claude

## Ziel und Kontext

Professionelle IT-Projektmanagementplattform, zunächst für den Eigentümer, später für sein Team auf einem virtuellen Server. Die Programmierung erfolgt mit Claude. Der Benutzer kennt Webseiten sowie etwas HTML/CSS und möchte Entscheidungen verständlich erklärt bekommen.

Lies zuerst README.md, docs/produktgrundlage.md und docs/vorbereitung-und-betrieb.md. Bestätigte Anforderungen, Vorschläge und offene Entscheidungen sind getrennt zu behandeln. Das Phasenmodell ist ausdrücklich offen. Die bestehende operative Rolloutplattform wird nicht nachgebaut. Keine Implementierung allein aus unverbindlichen Vorschlägen ableiten.

## Arbeitsweise

- Kommuniziere auf Deutsch, mit verständlichen Begründungen und kleinen, überprüfbaren Arbeitsschritten.
- Nutze Product Owner zur Anforderungsklärung und Backlogpflege, Enterprise-Architekt für Systemgrenzen und Betrieb, Softwarearchitekt für Anwendungsaufbau und Datenmodell, Entwickler zur Umsetzung sowie Tester und Reviewer zur Prüfung. Siehe docs/rollen-und-uebergaben.md. Der Hauptdialog koordiniert; der Benutzer verantwortet Produktentscheidungen.
- Setze anfangs Rollen nacheinander ein. Vermeide gleichzeitig schreibende Agenten in denselben Dateien. Jede Übergabe benennt Ziel, relevante Dateien, Abnahmekriterien und offene Fragen.
- Nutze die Rollen bedarfsgerecht; nicht jede kleine Änderung benötigt alle Rollen.
- Aktuell gilt Vorbereitungsphase: keine Anwendung, Frameworkinstallation oder Infrastruktur erstellen, bis die technische Grundrichtung mit dem Benutzer abgestimmt und die Umsetzung beauftragt ist.
- Formuliere Architekturentscheidungen als Vorschläge mit Alternativen, Konsequenzen und offenen Punkten. Dokumentiere getroffene Entscheidungen in docs/decisions/.
- Nach Beginn der Umsetzung: kleine vollständige Funktionen entwickeln, passende Prüfungen ausführen und konkrete Ergebnisse zeigen. Nicht getestetes Verhalten ausdrücklich benennen.
- Halte Anforderungen und Arbeitsstand in Dateien aktuell. Stelle geklärte Fragen nicht erneut.
- Nutze docs/backlog.md als gemeinsames Backlog. Markiere eine Aufgabe nur anhand der Abnahmekriterien und tatsächlicher Prüfnachweise als erledigt. Kein Rollenagent besitzt ein konkurrierendes eigenes Backlog.
- Der Styleguide ist ausdrücklich offen und vor der Oberflächenimplementierung mit dem Benutzer abzustimmen. Siehe docs/styleguide-briefing.md. Erfinde kein bestätigtes Branding.

## Fachliche Leitplanken

- Vier Benutzerrollen: Administrator, Projektleiter, Mitarbeiter, Management. Detaillierte Rechte noch offen. Projektleiter erteilt Freigaben.
- Aufgaben können mehreren Personen zugewiesen werden; gemeinsame Aufgabe und gemeinsamer Status.
- Ein Bucket und optional ein Meilenstein je Aufgabe. Erledigte Aufgaben bleiben einsehbar.
- Ursprünglicher Plan, aktuell genehmigter Plan, Prognose und tatsächliche Termine bleiben unterscheidbar und historisiert.
- Fehlende oder veraltete Daten führen nicht automatisch zu grüner Bewertung.
- Erzeugte Dokumente müssen als PDF herunterladbar sein. Weitere Exportformate sind nicht beschlossen.
- Tägliche Sammelmails für überfällige Aufgaben; kein automatischer Berichtsversand ohne zusätzliche Entscheidung.

## Technische Leitplanken für die spätere Umsetzung

- Berechtigungen im Backend prüfen, einschließlich direkter Datei- und Objektzugriffe. UI-Ausblendung genügt nicht.
- Beispiele und Demonstrationsdaten klar von produktiven Daten trennen.
- Keine echten Zugangsdaten, Projektdaten, Uploads oder das interne Originalhandbuch in Git aufnehmen.
- Geheimnisse über lokale Umgebung beziehungsweise Serverkonfiguration verwalten. Nur Platzhalter in Beispieldateien.
- Datenbankänderungen versionieren. Wiederherstellung muss Datenbank, Dateien und erforderliche Konfiguration berücksichtigen.
- Ein Repository ersetzt keine Sicherung produktiver Daten.
- Plane getrennte Dev- und Prod-Umgebungen mit einer Deployment-Pipeline. Siehe docs/vorbereitung-und-betrieb.md. Trenne insbesondere Daten, Dateien, Secrets und E-Mail-Versand. Branches allein ersetzen keine Umgebungstrennung.
- Produktionsveröffentlichung, bezahlte Dienste und externe Uploads zuvor konkret mit dem Benutzer abstimmen. Der aktuelle Auftrag betrifft lokale Vorbereitung.

## Prüfung und Berichterstattung

Abnahmekriterien vor Umsetzung festhalten. Besonders prüfen: Projektgrenzen und Rollenrechte, Mehrfachzuweisung, Wiederöffnen, Terminverlauf, unveränderte Berichtsstände, PDF-Ausgabe und mehrfach ausgeführte Reminder-Jobs. Beschreibe Änderung, Prüfergebnis, Einschränkungen und nächsten Schritt.
