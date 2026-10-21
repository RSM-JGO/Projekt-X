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
- Windows-Nacharbeit, Auftrag des Benutzers vom 21.10.2026: docs/entwurf-windows-betrieb.md (Revision 3, Entwurf). Er ersetzt die Abschnitte A und C von docs/entwurf-nacharbeit.md und deckt lokale Windows-Entwicklung, PDF-Optionen, Windows-Serverbetrieb, Hintergrundjobs, Pipeline mit Release-Paket und Prüfsumme sowie die externe Demo-Ansicht ab. Geprüft durch architect (sechs Befunde) und release-manager (fünf Befunde); alle Befunde sind eingearbeitet.
- Präzisiertes Zielbild des Benutzers: Das MVP hat eine lokale Umgebung **und** eine Möglichkeit, dass andere es von außen ansehen; später folgt der Umzug auf eine Umgebung des Arbeitgebers.
- Installationsliste zur Freigabe: docs/installationsliste-windows.md (uv, von uv verwaltetes Python 3.13, PostgreSQL 18). Noch **nicht freigegeben, nichts installiert**.

- **Lokale Umgebung eingerichtet (21.10.2026):** uv 0.13.4, Python 3.13.16 und PostgreSQL 18.6 mit Rolle `projektx` und Datenbank `projektx_dev`, nur über `localhost` erreichbar. Nachweise in docs/einrichtungsstand.md. Ein Django-Start ist noch nicht nachgewiesen.
- **Designvorschau (V06, Auftrag docs/auftrag-erster-prototyp.md) erstellt:** design/ (index.html, styles.css, app.js, data.js, README.md). Gebaut vom developer, Kurzreview durch reviewer; dessen vier Befunde sind behoben. Lokal zu öffnen per Doppelklick auf design/index.html oder über die Vorschau-Konfiguration `designvorschau` in .claude/launch.json (http://127.0.0.1:8123, nur lokal).
  - **Im Browser durch den Hauptdialog geprüft:** Navigation; Hell, Dunkel und Speicherung nach Neuladen; Abschließen und Wiederöffnen von „Filialtermine mit Regionalleitung bestätigen“ mit gleichem Zustand in Projekt und Arbeitsplatz; Filter Offen/Erledigt/Alle; Verlaufseinträge; Management mit Plan/Prognose-Abweichung; veraltete Berichte werden neutral statt grün dargestellt; unbekannte Projekt-Adressen zeigen einen Leerzustand; bei 375 px Breite keine horizontale Überbreite, untere Navigation und Detailpanel bedienbar; keine Konsolenfehler.
  - **Nicht geprüft:** gemessene Kontrastwerte, Screenreader, vollständige Tastaturbedienung, Darstellung auf Tablet-Breite und in anderen Browsern.
  - **Benutzerfeedback vom 21.10.2026:**
    - Die Gestaltung (Farben, Stil) ist „schon in Ordnung“.
    - Der Aufbau gefällt noch nicht ganz; besonders der Arbeitsplatz ist unübersichtlich. Die Überarbeitung kommt später.
    - Die Darkmode-Einstellung war zu präsent. Umgesetzt ist jetzt ein einzelner Hell/Dunkel-Umschalter (☾/☀) ohne Option „System“. Beim ersten Öffnen gilt die Windows-Einstellung, danach die gespeicherte Wahl. Im Browser geprüft: Umschalten, Speicherung nach Neuladen, Handybreite, keine Konsolenfehler.
    - Drittes Feedback: Das Logo des Benutzers ist im Kopf eingebaut (design/assets/logo-projekt-x.webp). Die Farben sind ans Logo angeglichen: Grün = gut, Orange = beobachten, Rot = kritisch, Grau = veraltet, Blau nur ohne Statusbedeutung; Avatare sind neutral. Geprüft hell, dunkel und bei 375 px; keine Konsolenfehler.
    - Zweites Feedback: Die Management-Kästen waren unterschiedlich hoch, und die lila Schrift gefiel nicht. Umgesetzt: Schrift überall dunkelgrau bzw. im Darkmode hellgrau, farbig sind nur noch Symbole und Linien; die Management-Karten sind gleich hoch mit gleicher Oberkante und einheitlichem Kopf. Im Browser per Farbabfrage auf allen vier Ansichten geprüft: keine farbige Schrift außer Statussymbolen. Regeln stehen in docs/styleguide-briefing.md.
  - Styleguide damit noch **nicht** vollständig bestätigt. Offen ist der Aufbau des Arbeitsplatzes und der Seiten.

## Nächster Auftrag

1. Der zentrale Claude-Chat „Projektleitung und Rollenüberblick“ übernimmt ab jetzt den Single Point of Contact. Die acht Rollen sind eingerichtet und nachgewiesen.
2. Jetzt den beauftragten Auftrag docs/auftrag-erster-prototyp.md ausführen: klickbare Designvorschau (V06) lokal erstellen, Projekt X mit Pastellakzenten, Hell/Dunkel und Beispieldaten. Kein weiterer Server- oder Gesamtplanungsblock davor. Umsetzung noch nicht gestartet; die Vorbereitung allein ist kein funktionierender Prototyp.
3. Nach Feedback Gestaltung festhalten; native Windows-Python-/PostgreSQL-Umgebung einrichten und ersten kleinen echten Ablauf mit Django umsetzen und prüfen. Keine erneute Gesamtplanung.
4. Der virtuelle Windows-Server kommt erst beim späteren Umzug von privater Entwicklung in berufliche Nutzung. Serverversion, Hosting und konkrete produktive Pipeline blockieren die lokale Entwicklung nicht. Keine WSL-/Linux-Installation.

## Offen

Die beantragte Installation von Microsoft.WSL über winget wurde vom Benutzer nicht freigegeben und nicht ausgeführt. Der vorherige direkte WSL-Installationsaufruf schlug ohne Installation fehl. WSL ist nach der Windows-Server-Entscheidung nicht mehr Teil der geplanten Einrichtung.

Bestätigte Gestaltungsvorgabe: Name Projekt X, moderne Gestaltung, gerne Pastellfarben, helle normale Ansicht und Darkmode. Die konkrete Gestaltung wird zunächst als Vorschau abgestimmt.

Lesende Rechnerprüfung durch die Beratung bereits ausgeführt: siehe docs/pruefung-entwicklungsrechner.md. Windows-Arbeitsplatz und Git funktionieren. Die native Python-/Datenbankumgebung ist noch einzurichten und nachzuweisen.

Freigabe der Installationsliste, Django-Version (W-B), PDF-Verfahren (W-C), Variante der externen Demo-Ansicht (W-D), genaue Windows-Server-Version, Webserver und Dienste beim Arbeitgeber (W-E), detaillierte Rechte inklusive Administratorrechte in Projektinhalten, Teilen persönlicher Aufgaben, Vorgänge in der ersten Fassung, Phasenmodell, Styleguide und konkrete Pipeline. Technische Grundrichtung ist bestätigt. Noch keine Anwendung implementiert und keine Dev-/Prod-Instanzen eingerichtet.

## Wiederaufnahme

In einem neuen Chat zuerst CLAUDE.md, README.md und diese Datei lesen, danach Backlog und relevante Entscheidungen. Ein Entwurf oder ein früherer Vorschlag ist keine Benutzerfreigabe. Den aktuellen Git-Zustand vor Änderungen prüfen. Änderungen an diesem Arbeitsstand mit konkreten Nachweisen ergänzen.
