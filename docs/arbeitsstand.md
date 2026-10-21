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

1. Benutzerentscheidung zu T1 (technische Grundrichtung) und R (Reihenfolge V06 parallel zu V07a, danach V07b) aus docs/entwurf-nacharbeit.md einholen und dann in docs/decisions/ festhalten.
2. Nach Auftrag: die lesenden Prüfschritte zur lokalen Containerumgebung (Abschnitt A) ausführen, danach T2 entscheiden. Keine Installation ohne gesonderte Freigabe.
3. Styleguide-Gestaltungsproben (V06) vorbereiten; Produktregeln (V05) einzeln klären. Oberfläche erst nach Gestaltungsklärung.

## Offen

Lesende Rechnerprüfung durch die Beratung bereits ausgeführt: siehe docs/pruefung-entwicklungsrechner.md. WSL ist nicht installiert; die tatsächliche Container-Eignung und ein lauffähiger Start sind noch nicht nachgewiesen. Diese Ergebnisse vor weiteren Prüfungen berücksichtigen.

Technikfreigabe (T1), lokale Containerumgebung (T2), detaillierte Rechte inklusive Administratorrechte in Projektinhalten, Teilen persönlicher Aufgaben, Vorgänge in der ersten Fassung, Phasenmodell, Styleguide, Serveranbieter, Prod-Variante P1 oder P2 und konkrete Pipeline. Noch keine Anwendung implementiert und keine Dev-/Prod-Server eingerichtet.

## Wiederaufnahme

In einem neuen Chat zuerst CLAUDE.md, README.md und diese Datei lesen, danach Backlog und relevante Entscheidungen. Ein Entwurf oder ein früherer Vorschlag ist keine Benutzerfreigabe. Den aktuellen Git-Zustand vor Änderungen prüfen. Änderungen an diesem Arbeitsstand mit konkreten Nachweisen ergänzen.
