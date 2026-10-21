# Erster Auftrag an Claude Code

Wir bereiten eine professionelle IT-Projektmanagementplattform vor. Beginne mit Vorbereitung und Planung; programmiere noch keine Anwendung und installiere noch keine Frameworks.

Lies CLAUDE.md, README.md, docs/arbeitsstand.md, docs/produktgrundlage.md, docs/vorbereitung-und-betrieb.md, docs/backlog.md, docs/rollen-und-uebergaben.md und docs/styleguide-briefing.md. Prüfe, ob alle acht Rollen in .claude/agents/ erkannt werden: project-lead, product-owner, enterprise-architect, architect, developer, tester, reviewer und release-manager. Übernimm die Projektleitung im Hauptdialog. Nutze Product Owner, Enterprise-Architekt und Softwarearchitekt bedarfsgerecht nacheinander sowie Releasemanager für Pipeline- und Releasefragen. Falls Unteragenten nicht verfügbar sind, benenne das und bearbeite die Rollen nachvollziehbar nacheinander im Hauptdialog. Bestehende Architekturentwürfe anhand docs/pruefung-architekturentwuerfe.md nacharbeiten, statt die gesamte Vorbereitung zu wiederholen.

Erstelle anschließend:

1. Eine kurze Bestandsaufnahme der Projektdateien und der verfügbaren lokalen Entwicklungswerkzeuge, ohne Installationen oder Zugangsdaten auszulesen.
2. Eine Übersicht bestätigter Anforderungen und der wenigen Entscheidungen, die den technischen Aufbau tatsächlich blockieren. Nicht alle offenen Produktdetails müssen vorab geklärt sein.
3. Einen begründeten Vorschlag für Webframework, Backend, relationale Datenbank, Anmeldung, PDF-Erzeugung, Hintergrundjobs und späteren Linux-VPS-Betrieb. Verifiziere versionsabhängige Aussagen anhand offizieller Dokumentation und zeige laufenden Betriebsaufwand auf.
4. Einen Entwurf für Module und zentrale Datenobjekte, insbesondere Projekt, Mitgliedschaft, Aufgabe, Mehrfachzuweisung, Bucket, Meilenstein, Planstand, Statusbericht, Dokumentversion und Reminder.
5. Einen konkreten ersten Entwicklungsabschnitt mit Abnahmekriterien, geeigneten Tests und geplanter Ordnerstruktur.

Speichere Ergebnisse als klar gekennzeichnete Entwürfe in docs/. Erkläre sie auf Deutsch verständlich. Veröffentliche nichts auf GitHub und buche keine Dienste. GitHub-Repository und technische Grundrichtung werden zunächst mit mir festgelegt. Bewahre das Phasenmodell als offene Produktentscheidung.
