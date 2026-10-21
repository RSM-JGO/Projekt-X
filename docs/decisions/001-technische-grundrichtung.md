# Technische Grundrichtung

Datum: 21. Oktober 2026. Status: beschlossen; Linux-/Containeranteile durch Entscheidung 002 ersetzt.

## Entscheidung

Der Benutzer hat den vorgeschlagenen technischen Aufbau bestätigt und die weitere Vorbereitung bis zur praktischen Übergabe an Claude beauftragt.

- Django mit Python als Anwendungsframework und Backend.
- PostgreSQL als relationale Datenbank.
- HTML/CSS-Oberfläche mit gezielten interaktiven Komponenten.
- Ursprünglicher Vorschlag Linux-Container: durch die spätere ausdrückliche Windows-Server-Vorgabe ersetzt; siehe 002-windows-server.md.
- Getrennte Dev- und Prod-Umgebungen; geprüfte Anwendungsversionen und bewusste Prod-Freigabe.
- Bestehenden Windows-Projektordner und Claude Desktop möglichst beibehalten.

## Reihenfolge und Umfang

Die lokale Entwicklungsumgebung wird eingerichtet und geprüft. Gestaltungsproben und Vorbereitung des technischen Fundaments können parallel erfolgen. Anwendungsoberflächen werden erst nach Abstimmung des Styleguides umgesetzt. Ziel ist ein erster kleiner vollständiger Ablauf mit überprüfter Umsetzung durch Claude und anschließender selbstständiger Weiterarbeit im zentralen Claude-Projektleiterchat.

Die Bestätigung legt nicht automatisch Detailrechte, Phasenmodell, Paketversionen, Anbieter, kostenpflichtige Verträge oder die konkrete produktive Pipeline fest. Produktionsveröffentlichung und ein erforderlicher Rechnerneustart werden gesondert abgestimmt.

## Begründung

Ein gemeinsam entwickeltes System mit überschaubarer Modulstruktur, dauerhafter Datenhaltung und serverseitigen Berechtigungen passt zum zunächst persönlichen und späteren Teameinsatz. Die Oberfläche bleibt anhand konkreter Gestaltungsproben anpassbar. Container sollen Unterschiede zwischen Entwicklung und Betrieb begrenzen.

## Nächster Nachweis

Eine native Windows-Entwicklungsumgebung startet tatsächlich; Claude kann darin die Anwendung ausführen und geeignete Prüfungen durchführen. Die Installation allein ist kein Nachweis einer funktionierenden Entwicklungsumgebung. Zielbetrieb ist ein virtueller Windows-Server gemäß Entscheidung 002.
