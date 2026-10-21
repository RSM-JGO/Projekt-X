# Aktueller Arbeitsstand

Stand 21. Oktober 2026. Diese Datei dient als Einstieg in neue Claude-Chats.

## Ziel

Der Benutzer soll die Entwicklung nach abgeschlossener Einrichtung direkt in Claude Desktop steuern können. Der zentrale Claude-Chat übernimmt die Projektleitung und koordiniert die Fachrollen. Codex hat die Vorbereitung und Beratung übernommen; es ist keine dauerhafte externe Koordination erforderlich.

## Vorhanden und geprüft

- Privates GitHub-Repository: https://github.com/jago1698/projektmanagement-software.
- Lokaler Ordner: C:\Users\jango\Documents\Projektmanagement-Software.
- Git for Windows regulär installiert; Pfad und Aufruf ohne vollständige Pfadangabe in neu gestarteter Claude-Sitzung bestätigt.
- Projektgrundlage, gemeinsames Backlog und Arbeitsregeln vorhanden.
- Product Owner, Enterprise-Architekt, Softwarearchitekt, Entwickler, Tester und Reviewer von Claude als geladen erkannt. Die drei beratenden Rollen haben Architekturentwürfe geliefert.
- Projektleiter ergänzt: .claude/agents/project-lead.md. In der neuen Sitzung „Projektleitung und Rollenüberblick“ hat Claude alle sieben Rollen als geladen bestätigt und die Projektleitung im Hauptdialog übernommen.
- Vier Architekturentwürfe vorhanden, aber nicht freigegeben. Die Beraterprüfung in docs/pruefung-architekturentwuerfe.md ist bei der Nacharbeit zu berücksichtigen.

## Nächster Auftrag

1. Projektleitungsmodus im Hauptdialog fortführen; Rollen-Erkennung ist nachgewiesen und muss ohne Anlass nicht erneut geprüft werden.
2. Architekturentwürfe anhand der Prüfung nacharbeiten, ohne Anwendung oder Infrastruktur zu implementieren.
3. Eine kurze, verständliche technische Empfehlung zur gemeinsamen Entscheidung vorlegen.
4. Anschließend lokale Entwicklungsumgebung und Styleguide konkretisieren; Oberfläche erst nach Gestaltungsklärung umsetzen.

## Offen

Technikfreigabe, lokale Containerumgebung, detaillierte Rechte, Phasenmodell, Styleguide, Serveranbieter und konkrete Pipeline. Noch keine Anwendung implementiert und keine Dev-/Prod-Server eingerichtet.

## Wiederaufnahme

In einem neuen Chat zuerst CLAUDE.md, README.md und diese Datei lesen, danach Backlog und relevante Entscheidungen. Ein Entwurf oder ein früherer Vorschlag ist keine Benutzerfreigabe. Den aktuellen Git-Zustand vor Änderungen prüfen. Änderungen an diesem Arbeitsstand mit konkreten Nachweisen ergänzen.
