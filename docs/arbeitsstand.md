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
- Als achte Rolle release-manager ergänzt, mit docs/releaseprozess.md für Versionen, Release Notes und Dev-/Prod-Übergaben. Nachweis 21.10.2026: release-manager erscheint in der Projektleitungssitzung als geladener Unteragent und hat einen Prüfauftrag zu Abschnitt C der Nacharbeit ausgeführt. Damit sind alle acht Rollen erkannt.
- Vier Architekturentwürfe vorhanden, aber nicht freigegeben. Nacharbeit zu allen zehn Prüfpunkten liegt in docs/entwurf-nacharbeit.md (Revision 2, Entwurf). Die vier Originale tragen nur einen Hinweis darauf. Eng begrenzte Prüfungen: architect zu Rollen, Dateien und Terminen (sechs Befunde), release-manager zum Prod-Prozess (fünf Befunde). Alle Befunde sind eingearbeitet.

## Nächster Auftrag

1. Grundrichtung bestätigt, anschließend explizit auf Windows-Server präzisiert: docs/decisions/001-technische-grundrichtung.md und 002-windows-server.md. Die Linux-/Containeranteile der älteren Entscheidung sind ersetzt. Diese Vorgabe nicht erneut abfragen.
2. Native Windows-Entwicklung und Betrieb auf virtuellem Windows-Server konkretisieren und praktisch prüfen. Keine WSL- oder Linux-Containerinstallation. PDF-Erzeugung, Dienste, Hintergrundjobs und Pipeline Windows-tauglich ausarbeiten. Installationsfreigaben über die vorhandenen Systemwerkzeuge beachten; keinen Rechnerneustart eigenständig auslösen.
3. Styleguide-Gestaltungsproben (V06) vorbereiten; Produktregeln (V05) konkretisieren. Oberfläche erst nach Gestaltungsklärung.
4. Ersten kleinen Ablauf durch Claude implementieren und unabhängig prüfen lassen; danach Übergabekriterien aus docs/uebergabe-an-claude.md nachweisen.

## Offen

Die beantragte Installation von Microsoft.WSL über winget wurde vom Benutzer nicht freigegeben und nicht ausgeführt. Der vorherige direkte WSL-Installationsaufruf schlug ohne Installation fehl. WSL ist nach der Windows-Server-Entscheidung nicht mehr Teil der geplanten Einrichtung.

Bestätigte Gestaltungsvorgabe: Name Projekt X, moderne Gestaltung, gerne Pastellfarben, helle normale Ansicht und Darkmode. Die konkrete Gestaltung wird zunächst als Vorschau abgestimmt.

Lesende Rechnerprüfung durch die Beratung bereits ausgeführt: siehe docs/pruefung-entwicklungsrechner.md. Windows-Arbeitsplatz und Git funktionieren. Die native Python-/Datenbankumgebung ist noch einzurichten und nachzuweisen.

Native Windows-Entwicklungsumgebung, genaue Windows-Server-Version, Windows-Betriebsaufbau, detaillierte Rechte inklusive Administratorrechte in Projektinhalten, Teilen persönlicher Aufgaben, Vorgänge in der ersten Fassung, Phasenmodell, Styleguide und konkrete Pipeline. Technische Grundrichtung ist bestätigt. Noch keine Anwendung implementiert und keine Dev-/Prod-Instanzen eingerichtet.

## Wiederaufnahme

In einem neuen Chat zuerst CLAUDE.md, README.md und diese Datei lesen, danach Backlog und relevante Entscheidungen. Ein Entwurf oder ein früherer Vorschlag ist keine Benutzerfreigabe. Den aktuellen Git-Zustand vor Änderungen prüfen. Änderungen an diesem Arbeitsstand mit konkreten Nachweisen ergänzen.
