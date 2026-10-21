# Windows als Entwicklungs und Serverplattform

Datum: 21. Oktober 2026. Status: beschlossen, ausdrückliche Vorgabe des Benutzers.

## Entscheidung

Projekt X soll auf einem virtuellen Windows-Server betrieben werden. Der lokale Arbeitsplatz bleibt Windows mit Claude Desktop. Die Linux- und Containeranteile der Entscheidung 001 und der bisherigen Architekturentwürfe sind damit ersetzt. Django, PostgreSQL, die Weboberfläche, GitHub sowie getrennte Dev-/Prod-Umgebungen bleiben die technische Grundrichtung.

Zeitliche Präzisierung des Benutzers: Der Windows-Server kommt erst nach der privaten Entwicklung für den späteren Umzug in die berufliche Nutzung. Jetzt lokal entwickeln und testen. Serverzugang, Serverversion und produktive Pipeline sind keine Voraussetzung für den Start. Externe Zwischenstands-Demos sind eine mögliche spätere Ergänzung, noch kein beauftragtes Hosting.

WSL und Linux-Container sind keine geplanten Voraussetzungen mehr. WSL wurde nicht installiert; es sind keine entsprechenden Schritte zu wiederholen. Docker Desktop ist kein Ziel für den Windows-Server. Die genaue Windows-Server-Version ist noch unbekannt.

## Nacharbeit

Native Windows-Entwicklung und Windows-Betrieb ausarbeiten: geeigneter Produktions-Webserver, Dienstverwaltung, Hintergrundaufgaben, PDF-Erzeugung, Dateiablage, Sicherung und Pipeline. Betriebsmittel wie Bash-Skripte, Linux-Dienste, Linux-Pfade, Container-Digests und Linux-Compose-Stacks aus bisherigen Vorschlägen nicht als beschlossene Lösung übernehmen.

Dev und Prod behalten getrennte Datenbanken, Dateien, Konfigurationen und Identitäten. Eine Anwendungsversion muss vor Prod nachweislich auf Dev geprüft sein. Ob zwei Windows-Server oder getrennte Instanzen auf demselben Server verwendet werden, bleibt offen.

## Geprüfte Anknüpfungspunkte

- Waitress unterstützt Windows und kann als Produktions-WSGI-Server für eine Django-Anwendung geprüft werden: https://docs.pylonsproject.org/projects/waitress/en/stable/.
- PostgreSQL bietet Windows-Installer. Die konkrete Serverversion bestimmt die geeignete PostgreSQL-Hauptversion mit: https://www.postgresql.org/download/windows/.
- Docker Desktop wird laut Hersteller nicht auf Windows Server unterstützt: https://docs.docker.com/desktop/setup/install/windows-install/.

Die Quellen belegen mögliche Bausteine, noch keinen eingerichteten oder getesteten Betrieb. Ein virtueller Windows-Server ist mit einer Webanwendung vereinbar. SaaS-Nutzung erfordert kein bestimmtes Serverbetriebssystem.
