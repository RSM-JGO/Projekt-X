# Weiterarbeit direkt in Claude

## Zentraler Ansprechpartner

Der Hauptdialog übernimmt die Projektleitung. Der Benutzer beschreibt hier Ziele, Probleme und Änderungswünsche in normaler Sprache. Die Projektleitung klärt Auswirkungen, pflegt den gemeinsamen Arbeitsstand und zieht passende Fachrollen hinzu. Der Benutzer muss nicht mehrere Rollen-Chats führen.

Sieben Rollen: project-lead, product-owner, enterprise-architect, architect, developer, tester, reviewer. Die delegierte Projektleiterrolle unterstützt die Planung; Agentenaufrufe koordiniert der Hauptdialog. Ein Rollenname alleine führt keine Prüfung aus. Ergebnisse müssen anhand der tatsächlichen Arbeit und Nachweise bewertet werden.

## Umgang mit Änderungswünschen

1. Wunsch aufnehmen und bestehende Anforderungen berücksichtigen.
2. Mit Product Owner Nutzen und Abnahmekriterien formulieren.
3. Bei relevanten Auswirkungen Architektur, Rechte, Daten und Betrieb prüfen lassen.
4. Änderung und Abhängigkeiten im gemeinsamen Backlog festhalten; größere Richtungsänderungen mit dem Benutzer abstimmen.
5. Nach Beauftragung umsetzen, testen und unabhängig prüfen lassen.
6. Ergebnis zeigen und Arbeitsstand dokumentieren. Fachliche Abnahme bleibt beim Benutzer.

## Wann die Übergabe vollständig ist

- Alle sieben Rollen sind erkannt; der Hauptdialog arbeitet als Projektleitung.
- Arbeitsstand, Backlog, Anforderungen und Entscheidungen sind auch ohne alte Chat-Historie nutzbar.
- Technische Grundrichtung und lokale Entwicklung sind abgestimmt und durch einen lauffähigen Start nachgewiesen.
- Styleguide und erster Entwicklungsabschnitt sind konkret genug zur Umsetzung.
- Der Benutzer kann eine Änderung anfragen und erhält nachvollziehbar Vorschlag, Umsetzung und Prüfergebnis.
- Git-Speicherung und Upload funktionieren; Betrieb und Pipeline sind als nächste Aufgaben klar beschrieben, soweit noch nicht eingerichtet.

Die Übergabe ist derzeit vorbereitet, noch nicht vollständig abgeschlossen. Codex muss nicht alle zukünftigen Produktfunktionen selbst begleiten. Freigaben und Zugänge bei externen Diensten verbleiben beim Benutzer.

## Startnachricht für einen neuen Claude-Chat

Übernimm die Projektleitung für meine IT-Projektmanagementplattform. Lies CLAUDE.md, README.md, docs/arbeitsstand.md, docs/backlog.md und docs/rollen-und-uebergaben.md. Du bist mein zentraler Ansprechpartner für Änderungswünsche und koordinierst die passenden Fachrollen intern. Prüfe, ob project-lead und die sechs weiteren Rollen geladen sind. Berücksichtige vor der nächsten Architekturentscheidung docs/pruefung-architekturentwuerfe.md. Setze beim dokumentierten nächsten Schritt fort; behandle Entwürfe nicht als Freigaben und frage bereits geklärte Anforderungen nicht erneut ab.
