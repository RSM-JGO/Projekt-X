# Lesende Prüfung des Entwicklungsrechners

Stand 21. Oktober 2026. Keine Installation, Aktivierung von Windows-Komponenten oder Änderung von Systemkonfiguration im Rahmen dieser Prüfung.

## Beobachtete Ergebnisse

- Betriebssystem: Microsoft Windows 11 Home, Version 10.0.26200, Build 26200.
- Gemeldeter Arbeitsspeicher: rund 31,1 GiB.
- Windows meldet einen vorhandenen Hypervisor und aktivierte Firmware-Virtualisierung.
- Das CPU-Feld SecondLevelAddressTranslationExtensions lieferte false. Bei vorhandenem Hypervisor ist dieser einzelne Befund keine hinreichende Grundlage, um die Eignung für WSL2 oder Docker zu bestätigen oder auszuschließen. Vor Installation gegebenenfalls gezielt weiter prüfen.
- Das vorhandene wsl.exe meldet für Versions- und Statusabfrage, dass das Windows-Subsystem für Linux nicht installiert ist.
- Git for Windows ist regulär installiert und nach vollständigem Neustart in Claude geprüft; siehe docs/einrichtungsstand.md.

## Konsequenz

Ein Docker-/WSL-Start ist noch nicht nachgewiesen. Nach Entscheidung zur technischen Grundrichtung die Voraussetzungen gezielt prüfen und eine konkrete Einrichtung vorschlagen. Eine erforderliche Windows-Komponentenaktivierung, Installation oder ein Neustart ist separat mit dem Benutzer zu koordinieren. Den bestehenden Projektordner und den funktionierenden Claude-Desktop-Zugang möglichst erhalten.
