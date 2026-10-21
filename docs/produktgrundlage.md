# Produktgrundlage der IT-Projektmanagementplattform

Stand: 21. Oktober 2026

Dieses Dokument hält die bisher abgestimmten Anforderungen fest. Vorschläge und offene Entscheidungen sind ausdrücklich getrennt aufgeführt. Die Umsetzung soll durch Claude erfolgen. Die Benutzeroberfläche und Abläufe sollen zunächst anhand eines Prototyps überprüft werden.

## Ziel und Einsatz

- Zentrale Plattform für die operative Arbeit von IT-Projektmanagern sowie Planung und Managementreporting über mehrere Projekte.
- Zunächst persönliche Nutzung, perspektivisch Teamnutzung auf einem virtuellen Server.
- Professionelle Webanwendung mit Frontend, Backend, Datenbank, Dateiablage und Berechtigungsmodell.
- Dev- und Prod-Umgebungen sowie eine Deployment-Pipeline sollen von Anfang an eingeplant werden; konkrete Ausgestaltung und Infrastruktur noch offen.
- Projekte enthalten regelmäßig einen Rollout. Teilweise wird das gesamte Projektmanagement übernommen.
- Die operative Rolloutsteuerung erfolgt in einer bestehenden Rolloutplattform. Ihre Detailfunktionen sollen nicht nachgebaut werden.
- Das bereitgestellte Rollouthandbuch ist eine fachliche Quelle, keine uneingeschränkte Softwarevorgabe. Das allgemeine Phasenmodell ist noch offen; bisherige Phasenvorschläge sind nicht beschlossen.
- Projektwissen, Aufgaben und Dokumentation sollen zentral gepflegt und bei Bedarf heruntergeladen werden können.

## Arbeitsbereiche

### Persönlicher Arbeitsplatz

- Projektübergreifende Übersicht eigener Aufgaben.
- Tagesplanung, überfällige und kommende Aufgaben, eigene Freigaben, offene Rückmeldungen und eigene Projekte.
- Persönliche Aufgaben ohne Projektzuordnung.
- Vollständige Aufgabenansicht mit Filtern nach Projekt, Termin, Priorität und Status; Listen-, Board- und Kalenderansicht.
- Dieselbe Aufgabe erscheint im Projekt und im persönlichen Arbeitsplatz, ohne dupliziert zu werden.
- Aufgaben in verantworteten Projekten sind von persönlich zugewiesenen Aufgaben unterscheidbar.

### Projektbereich und Projektübersicht

- Mehrere Projekte anlegen, anzeigen, bearbeiten und löschen.
- Projektteam zuordnen; Aufgaben, Planung, Dokumentation, Dateien, Risiken und Entscheidungen gemeinsam bearbeiten.
- Projekte archivieren können, damit abgeschlossene Vorhaben zugänglich bleiben und aus aktiven Übersichten verschwinden können.
- Löschen mit gesonderter Berechtigung und Bestätigung der betroffenen Inhalte.
- Projektübergreifendes Dashboard mit Status, Meilensteinen, Abweichungen und Entscheidungsbedarf gemäß Zugriffsrechten.

## Aufgabenmanagement

- Aufgaben anlegen, bearbeiten, löschen, kommentieren und abschließen.
- Eine oder mehrere Personen zuweisen. Bei mehreren Personen bleibt es eine gemeinsame Aufgabe mit gemeinsamem Status.
- Ein Bucket und optional ein Meilenstein je Aufgabe.
- Buckets je Projekt anlegen, umbenennen und sortieren; sie gruppieren thematisch und sind unabhängig vom Aufgabenstatus.
- Erledigte Aufgaben mit Filtern Offen, Erledigt und Alle weiterhin anzeigen; im Board aufklappbar.
- Kommentare, Anhänge, Zuordnungen und Abschlussinformationen bleiben erhalten.
- Anzeigen, wer eine Aufgabe wann abgeschlossen hat; Wiederöffnen mit entsprechender Berechtigung.
- Erledigte Aufgaben geben einen zugeordneten Meilenstein nicht automatisch frei.

### Reminder

- Optionale Erinnerung vor Fälligkeit und individuelle Wiedervorlagen.
- Überfällige Aufgaben im persönlichen Arbeitsplatz anzeigen.
- Tägliche Sammelmail je Person mit ihren überfälligen Aufgaben, Projektbezug, Fälligkeit und direktem Link.
- Bei Mehrfachzuweisung alle zugewiesenen Personen berücksichtigen.
- Versandzeitpunkt und aktivierte E-Mail-Erinnerungen persönlich einstellbar.
- Erledigte oder gelöschte Aufgaben lösen keine weiteren Erinnerungen aus.
- Auf dem Server auch bei geschlossenem Browser ausführen.
- Automatische Eskalation an die Projektleitung ist noch nicht festgelegt.

## Projektbeschreibung und Dokumentation

Vom Benutzer ausdrücklich benannte Inhalte des Projektsteckbriefs:

- Projekt und Projektzeitraum.
- Scope und grober Arbeitsumfang.
- Ziele und Nichtziele.
- Relevante Stakeholder.

Zur weiteren Abstimmung vorgeschlagene Ergänzungen:

- Automatische Projektnummer, Kurzbeschreibung, Ausgangslage und Nutzen.
- Erfolgskriterien, Projektleitung, Auftraggeber, Projektteam und fachliche Rollen.
- Zentrale Meilensteine, Abhängigkeiten, Annahmen, Rahmenbedingungen und erste Risiken.
- Verknüpfungen zu Dateien, Dokumenten und externen Systemen.
- Entwurfsanlage mit wenigen Pflichtfeldern; genauer Pflichtfeldumfang offen.

## Projektstatus und Terminverschiebungen

- Ursprünglichen freigegebenen Plan, aktuell genehmigten Plan, aktuelle Prognose und tatsächliche Termine getrennt führen.
- Planstände und frühere Statusberichte erhalten; Verschiebungen dürfen durch Überschreiben nicht unsichtbar werden.
- Terminänderungen mit altem und neuem Termin, Zeitpunkt, Verursacher, Ursache und gegebenenfalls Freigabe nachvollziehen.
- Bearbeitungszustand, Projektgesundheit und Fortschritt getrennt darstellen.
- Keine pauschale Gleichsetzung von Anteil erledigter Aufgaben und Projektfortschritt.
- Automatische Hinweise auf überfällige Meilensteine, Prognoseabweichungen, fehlende Voraussetzungen und veraltete Statusdaten.
- Fachliche Bewertung durch Projektleitung mit Begründung, Auswirkungen, Gegenmaßnahmen und Entscheidungsbedarf.
- Toleranzen für Bewertungen definierbar; fehlende oder veraltete Daten nicht automatisch grün darstellen.
- Plan und Prognose im Zeitplan vergleichen; Meilensteinübersicht und Vergleich zu früheren Statusberichten.
- Meilensteintrendanalyse als spätere Ausbaustufe vorgeschlagen.
- Budget und Kostenverfolgung sind spätere Erweiterungen.

## Benutzerrollen

Bestätigte Rollen:

- Administrator.
- Projektleiter.
- Mitarbeiter.
- Management mit Dashboard und Reporting für die jeweils zugeordneten Projekte.

Freigaben erteilt der Projektleiter nach den entsprechenden Terminen. Ein Datum löst keine automatische Freigabe aus. Eine separate Freigaberolle und eine zusätzliche Rolle für Leseberechtigte sind nicht vorgesehen.

Die konkrete Berechtigungsmatrix bleibt auszuarbeiten, insbesondere für Projektanlage, Löschen, Teamverwaltung, Aufgabenänderungen, Vorlagen und Downloads. Vorgeschlagen sind globale Administration und projektbezogene Rollen. Fachliche Stakeholder sind nicht automatisch zugriffsberechtigte Benutzer.

## Dateien und Dokumentenerzeugung

- Dateien hoch- und herunterladen.
- Inhalte über Erfassungsmasken im Tool pflegen.
- Dokumente anhand einheitlicher Vorlagen erzeugen; vorhandene Projektinformationen wiederverwenden.
- Alle erzeugten Dokumente als eigenständige PDF-Dateien herunterladen und per E-Mail-Anhang weitergeben können, ohne Plattformzugang beim Empfänger.
- PDF-Ausgabe mit einheitlichem Layout, lesbaren Tabellen, sauberen Seitenumbrüchen und Seitenzahlen.
- Word-Export und zusätzliche Listenformate sind Vorschläge und noch nicht bestätigt.
- Automatischer E-Mail-Versand von Berichten ist noch nicht beschlossen und von den bestätigten Aufgaben-Remindern zu unterscheiden.

### Monatlicher Statusbericht

Bestätigt ist der PDF-Download, insbesondere für einen monatlichen Statusbericht. Als Inhalt und Ablauf vorgeschlagen:

- Projekt, Projektleitung, Berichtsmonat, Erstellungsdatum und Version.
- Gesamtstatus mit Begründung und Veränderung zum Vormonat.
- Ergebnisse und nächste Schritte.
- Meilensteine mit Plan, Prognose und Abweichungen.
- Risiken, Probleme, Maßnahmen und Entscheidungsbedarf.
- Prüfung und Veröffentlichung durch Projektleiter; veröffentlichter Stand bleibt unverändert abrufbar.

### Weitere Dokumentkandidaten

Projektsteckbrief, Projektauftrag, Besprechungsprotokoll, Entscheidungs- und Freigabeprotokoll, Phasenabschluss, Projektabschlussbericht und Lessons Learned. Die genaue Auswahl, Felder und Vorlagen sind noch abzustimmen. Projektauftrag und Timeline wurden vom Benutzer als Beispiele genannt.

## Nächster sinnvoller Schritt

Ein klickbarer Prototyp mit eindeutig gekennzeichneten Beispieldaten soll die persönliche Startseite, Projektübersicht, Projektdetail, Aufgabenverwaltung, Managementdashboard und den Ablauf zum Statusbericht veranschaulichen. Er dient der Prüfung von Bedienung und Informationsstruktur. Produktive Datenhaltung, Berechtigungsprüfung, Reminder-Versand und PDF-Erzeugung müssen später gesondert umgesetzt und geprüft werden.

## Offene Entscheidungen

- Allgemeines Phasenmodell und phasenspezifische Abschlussdokumente.
- Exakte Berechtigungen und Sichtbarkeit persönlicher Aufgaben.
- Pflichtfelder, Aufgabenstatus, Hauptverantwortung bei Mehrfachzuweisung.
- Freigaben, Planänderungen, Toleranzen und Berechnung von Statuskennzahlen.
- Dokumentvorlagen, Branding, Versionierung und Veröffentlichungsablauf.
- Import aus bisherigen Werkzeugen und Anbindung der Rolloutplattform.
- Technischer Aufbau, Betrieb, Backup, Anmeldung und E-Mail-Dienst.
- Verwendeter Claude-Tarif und Verfügbarkeit von Claude Code.

## Vorgehen mit Claude

Der Benutzer entscheidet über Produktziele und Abnahme. KI-Rollen für Product Owner, Architektur, Entwicklung und Test erhalten klar abgegrenzte Aufträge und gemeinsame Projektunterlagen. Die genaue Claude-Konfiguration und Rollenbeschreibungen werden nach Klärung der verfügbaren Arbeitsumgebung erstellt.
