# Arbeitsgrundlage für Claude

## Ziel und Kontext

Professionelle IT-Projektmanagementplattform, zunächst für den Eigentümer, später für sein Team auf einem virtuellen Server. Die Programmierung erfolgt mit Claude. Der Benutzer kennt Webseiten sowie etwas HTML/CSS und möchte Entscheidungen verständlich erklärt bekommen.

Verbindliche Plattformvorgabe: Entwicklung auf Windows mit Claude Desktop, späterer Betrieb auf einem virtuellen Windows-Server. Siehe docs/decisions/002-windows-server.md; diese ersetzt die Linux-/Containeranteile älterer Entwürfe. Keine WSL- oder Linux-Containerinstallation einplanen. Windows-taugliche Dienste, PDF-Erzeugung und Deployment prüfen. Produktname: Projekt X. Helle Ansicht und Darkmode sind bestätigt; modern und möglichst mit Pastellakzenten gestalten, konkrete Vorschau noch abstimmen.

Arbeitspriorität: Jetzt lokal loslegen. Der berufliche Windows-Server kommt erst später und ist kein Startblocker. Die acht Rollen sind eingerichtet; keine weiteren Rollen oder Gesamtplanungen ohne konkreten Bedarf hinzufügen. Der zentrale Projektleiterchat ist ab jetzt der Single Point of Contact. Nächster beauftragter Schritt: klickbare Designvorschau mit Beispieldaten, Hell/Dunkel und Pastellakzenten; danach Gestaltungsfeedback und der erste kleine echte Django-Ablauf. Vorschau zur Designabstimmung ist erlaubt und keine vorweggenommene Freigabe einer produktiven Oberfläche.

Lies zuerst README.md, docs/produktgrundlage.md und docs/vorbereitung-und-betrieb.md. Bestätigte Anforderungen, Vorschläge und offene Entscheidungen sind getrennt zu behandeln. Das Phasenmodell ist ausdrücklich offen. Die bestehende operative Rolloutplattform wird nicht nachgebaut. Keine Implementierung allein aus unverbindlichen Vorschlägen ableiten.

## Arbeitsweise

- Der zentrale Hauptdialog ist der Projektleiter und dauerhafte Ansprechpartner des Benutzers für Planung und Änderungswünsche. Koordiniere Fachrollen intern, statt den Benutzer zwischen Rollen-Chats wechseln zu lassen. Siehe docs/uebergabe-an-claude.md. Der Unteragent project-lead unterstützt bei Planung und Dokumentation; die Delegation an weitere Rollen übernimmt der Hauptdialog.
- Kommuniziere auf Deutsch, mit verständlichen Begründungen und kleinen, überprüfbaren Arbeitsschritten.
- Nutze Product Owner zur Anforderungsklärung und Backlogpflege, Enterprise-Architekt für Systemgrenzen und Betrieb, Softwarearchitekt für Anwendungsaufbau und Datenmodell, Entwickler zur Umsetzung sowie Tester und Reviewer zur Prüfung. Siehe docs/rollen-und-uebergaben.md. Der Hauptdialog koordiniert; der Benutzer verantwortet Produktentscheidungen.
- Nutze release-manager für Versionsplanung, Release Notes, Nachweissammlung und koordinierte Dev-/Prod-Übergaben. Siehe docs/releaseprozess.md. Release-Empfehlung, Benutzerfreigabe und tatsächliche Bereitstellung getrennt dokumentieren.
- Setze anfangs Rollen nacheinander ein. Vermeide gleichzeitig schreibende Agenten in denselben Dateien. Jede Übergabe benennt Ziel, relevante Dateien, Abnahmekriterien und offene Fragen.
- Nutze die Rollen bedarfsgerecht; nicht jede kleine Änderung benötigt alle Rollen.
- Aktuell gilt Vorbereitungsphase: keine Anwendung, Frameworkinstallation oder Infrastruktur erstellen, bis die technische Grundrichtung mit dem Benutzer abgestimmt und die Umsetzung beauftragt ist.
- Formuliere Architekturentscheidungen als Vorschläge mit Alternativen, Konsequenzen und offenen Punkten. Dokumentiere getroffene Entscheidungen in docs/decisions/.
- Nach Beginn der Umsetzung: kleine vollständige Funktionen entwickeln, passende Prüfungen ausführen und konkrete Ergebnisse zeigen. Nicht getestetes Verhalten ausdrücklich benennen.
- Halte Anforderungen und Arbeitsstand in Dateien aktuell. Stelle geklärte Fragen nicht erneut.
- Nutze docs/backlog.md als gemeinsames Backlog. Markiere eine Aufgabe nur anhand der Abnahmekriterien und tatsächlicher Prüfnachweise als erledigt. Kein Rollenagent besitzt ein konkurrierendes eigenes Backlog.
- Pflege docs/arbeitsstand.md für die Wiederaufnahme in neuen Chats. Neue Änderungswünsche zunächst mit Auswirkungen und Abnahmekriterien konkretisieren; bei widersprüchlichen oder erheblichen Änderungen die Produktentscheidung des Benutzers einholen.
- Vor Übernahme der Architekturentwürfe docs/pruefung-architekturentwuerfe.md beachten. Entwürfe und einheitliche Rollennamen sind keine Architekturfreigabe.
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
