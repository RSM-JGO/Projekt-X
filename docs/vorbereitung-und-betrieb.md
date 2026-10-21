# Vorbereitung und Betrieb

Aktuelle Vorgabe: Betrieb auf virtuellem Windows-Server und Entwicklung unter Windows, siehe docs/decisions/002-windows-server.md. Die nachfolgenden Linux-/VPS-/Containerbausteine sind ältere Vorschläge und für die Umsetzung ersetzt. Native Windows-Dienste, PDF-Erzeugung und Deployment sind neu auszuarbeiten.

## Arbeitsstand

Die Produktgrundlage ist vorhanden. Ein lokales Vorbereitungsgerüst mit Claude-Arbeitsregeln und sechs Rollen liegt vor. Das private Repository https://github.com/jago1698/projektmanagement-software ist als origin eingetragen; erster Commit und Upload stehen aus. In Claude Code ist der lokale Projektordner ausgewählt und vom Benutzer freigegeben; das Lesen der Unterlagen und die Erkennung der Rollen müssen noch geprüft werden. Framework, Entwicklungswerkzeuge, Architektur und Server sind noch nicht abschließend festgelegt. Es gibt noch keine lauffähige Anwendung.

## Dev und Prod sowie Deployment-Pipeline

Der Benutzer möchte zwei Umgebungen und eine Deployment-Pipeline von Anfang an berücksichtigen. Die folgende Ausgestaltung ist ein Architekturentwurf, keine bereits eingerichtete Infrastruktur.

- Lokale Entwicklung auf dem Rechner ergänzt eine erreichbare Dev-Umgebung für Vorschau und Abnahme.
- Prod ist die produktive Teamumgebung.
- Dev und Prod besitzen getrennte Datenbanken, Dateiablagen, Konfigurationen und Zugangsdaten. Zwei Git-Branches allein schaffen diese Trennung nicht.
- Dev nutzt Beispieldaten und einen Mail-Testmodus, der keine Reminder an echte Teammitglieder versendet. Produktive Daten werden nicht automatisch nach Dev kopiert.
- Vorschlag für den Ablauf: Änderung und Pull Request, automatisierte Prüfungen und Build, Bereitstellung auf Dev, Prüfung, bewusste Freigabe derselben geprüften Anwendungsversion für Prod.
- Die konkrete Branch-Strategie, Pipeline-Technik und Freigabemöglichkeit sind noch festzulegen. GitHub Actions ist ein Kandidat; Verfügbarkeit von Funktionen im privaten Repository und Tarif vor Festlegung prüfen.
- Migrationen werden versioniert und je Umgebung kontrolliert ausgeführt. Rückkehr zur vorherigen Anwendungsversion und Wiederherstellung von Daten werden getrennt geplant; Datenbankmigrationen lassen sich nicht pauschal durch ein Code-Rollback zurücknehmen.
- Deployment-Zugangsdaten liegen außerhalb des Repository-Inhalts. Laufende Anwendungen, Backups und Zustände der Bereitstellungen sollen prüfbar sein.
- Ob Dev und Prod auf getrennten Servern oder zunächst isoliert auf einem Server laufen, bleibt eine Kosten- und Betriebsentscheidung. Gemeinsame Hardware erzeugt ein gemeinsames Ausfallrisiko.

Noch keine Server, kostenpflichtigen Dienste oder produktiven Deployments eingerichtet.

## Wo liegt was

| Ort | Zweck |
| --- | --- |
| Lokaler Projektordner | Dateien bearbeiten, Entwicklung und lokale Vorschau |
| Git | Änderungen und wiederherstellbare Versionsstände verwalten |
| Privates GitHub-Repository, vorgeschlagen | Quellcode und Dokumentation extern versionieren und Zusammenarbeit ermöglichen |
| Testumgebung, später | Änderungen mit Beispieldaten vor produktiver Nutzung prüfen |
| Produktiver Server, später | Anwendung, Hintergrundverarbeitung und gegebenenfalls Datenbank betreiben |
| Datenbank und Dateiablage | Geschäftsdaten, Uploads und erzeugte Dokumentstände speichern |
| Separate Sicherungsablage | Datenbank und Dateien wiederherstellbar sichern |
| E-Mail-Dienst | Reminder zustellen |
| Domain und HTTPS | Erreichbarkeit im Browser und verschlüsselte Verbindung |

GitHub veröffentlicht die Webanwendung nicht automatisch. GitHub Pages allein ersetzt kein Backend mit Datenbank und serverseitiger Rechteprüfung. Die genaue Hostinglösung ist noch offen. Der Server kann bereits bestehende externe Datenbank- oder Dateidienste nutzen; für den Start ist zusätzliche Verteilung nicht automatisch nötig.

SaaS beschreibt die Bereitstellung und Nutzung der Software als Dienst. Eine interne Team-Webanwendung benötigt nicht automatisch Kundenmandanten, Abonnements oder Zahlungsabwicklung. Diese Anforderungen sind bisher nicht beschlossen.

## Vorgeschlagene technische Grundrichtung

Eine gemeinsam entwickelte Anwendung mit klar getrennten fachlichen Modulen ist als Ausgangspunkt zu prüfen. Frontend und Backend können in einem Repository liegen; mehrere Projekte erfordern nicht mehrere Repositories. Microservices sind derzeit keine Anforderung.

Zu prüfen sind:

- Webframework und Programmiersprache mit guter Wartbarkeit und passender Claude-Unterstützung.
- Relationale Datenbank; PostgreSQL als Kandidat.
- Bewährte Anmeldung und Sitzungsverwaltung; keine selbst entworfene Kryptografie.
- Hintergrundverarbeitung für Reminder sowie gegebenenfalls PDF-Erzeugung.
- Dateispeicherung mit Zugriffsprüfung, Versionen und Sicherung.
- Bereitstellung auf Linux-VPS; Containerisierung als Kandidat für reproduzierbaren Betrieb.

Das sind Vorschläge, keine beschlossenen Technologieentscheidungen. Vor Festlegung aktuelle offizielle Dokumentation, Windows-Entwicklung, PDF-Funktionen, Betriebskosten und Wartungsaufwand prüfen.

## Entscheidungen vor Implementierungsbeginn

1. Claude-Code-Zugang und Zugriff auf diesen Projektordner verifizieren.
2. GitHub-Konto beziehungsweise Organisation und privates Repository festlegen. Interne Originalunterlagen verbleiben außerhalb des Repositories.
3. Konkreten Technologievorschlag mit begrenzten Alternativen erstellen und abstimmen.
4. Erstes Datenmodell und Rechteentwurf erstellen, einschließlich Planversionen, Mehrfachzuweisung und Dokumentständen.
5. Erste vollständige Funktion und ihre Abnahmekriterien auswählen.
6. Entwicklungs- und Testbefehle sowie geplante Ordnerstruktur dokumentieren.

## Entwicklungsreihenfolge als Vorschlag

1. Vorbereitung und technische Entscheidungen.
2. Lauffähige Grundanwendung mit Anmeldung, Datenbank und einfachen Projektberechtigungen.
3. Projektanlage und Aufgabenablauf über mehrere Projekte; zunächst kleiner Umfang mit echten Speicherungstests.
4. Oberfläche und Bedienung mit Beispieldaten prüfen und anpassen.
5. Planung, Planstände, Verschiebungen und Statusdarstellung ergänzen.
6. Monatlichen Statusbericht mit gespeichertem Stand und geprüftem PDF-Download umsetzen.
7. Reminder mit Zustellhistorie und Schutz gegen doppelte Benachrichtigungen ergänzen.
8. Managementansichten, weitere Dokumente und zusätzliche Funktionen ausbauen.

Ein früher Oberflächenprototyp kann zwischen Vorbereitung und Grundanwendung eingesetzt werden. Er darf nicht als fertig abgesicherte oder produktionsfähige Anwendung dargestellt werden.

## Vor Teamfreigabe

Testumgebung und Produktion unterscheiden, Rollenrechte und Dateizugriffe prüfen, HTTPS und Domain konfigurieren, sichere Zugangsdaten verwenden, Sicherungen und Wiederherstellung erproben, E-Mail-Zustellung prüfen sowie Aktualisierung und Rückkehr zur vorherigen Anwendungsversion dokumentieren. Ein Anbieter, kostenpflichtiger Vertrag oder Deployment wurde noch nicht beauftragt.
