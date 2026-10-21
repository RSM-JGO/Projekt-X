# Beauftragter erster Designprototyp

Status: vom Benutzer beauftragte lokale Vorbereitung zur Gestaltung, Umsetzung noch nicht gestartet. Keine erneute Gesamtplanung oder zusätzliche Rollen erforderlich.

## Ziel

Projekt X jetzt sichtbar und klickbar machen, damit der Benutzer Gestaltung und Bedienung beurteilen kann. Der zentrale Claude-Hauptdialog ist Projektleiter und Single Point of Contact. Er delegiert die Umsetzung an developer und eine kurze Prüfung an reviewer oder tester, ohne weitere Rollen zu erfinden.

## Umfang

Lokale, eigenständig im Browser darstellbare Designvorschau unter design/. Dafür sind weder Server noch Django- oder Datenbankinstallation erforderlich. Keine Produktivdaten, nur klar gekennzeichnete Beispieldaten. Der Prototyp ist kein fertiges Backend und darf nicht so dargestellt werden.

- Produktname Projekt X.
- Moderne, ruhige Gestaltung mit Pastellakzenten und gut lesbaren Texten.
- Helle normale Ansicht und Darkmode; sichtbarer Umschalter, Auswahl lokal merken.
- Durchgehende Navigation: Mein Arbeitsplatz, Projekte, Management. Administration kann als noch nicht implementierter Menüeintrag erkennbar sein.
- Mein Arbeitsplatz: projektübergreifende Aufgaben, fällige und überfällige Aufgaben, Rückmeldungen.
- Projektübersicht: mehrere Beispielprojekte, Zeitraum, Verantwortlicher und verständlicher Status.
- Projekt-/Aufgabenansicht: Buckets, Mehrfachzuweisung, Meilensteinbezug, Kommentare als Beispielinhalt, Offen/Erledigt/Alle.
- Mindestens eine Aufgabe lässt sich im Prototyp abschließen und wiederöffnen; derselbe Beispielzustand erscheint im persönlichen Bereich und im Projekt.
- Management: kompakte Projektübersicht mit Meilensteinen, Plan/Prognose-Abweichung und Berichtsdatum. Keine bloße Aufgabenquote als Projektfortschritt.

## Nachweis und Abschluss

1. Dateien lokal erstellen und öffnen beziehungsweise einen lokalen Vorschauprozess bereitstellen.
2. Hell/Dunkel, Navigation, Aufgabenabschluss und Erledigtfilter tatsächlich prüfen. Bei kleinen Bildschirmbreiten darf nichts unbedienbar überlappen.
3. Dem Benutzer die funktionierende Vorschau zeigen, maximal drei konkrete Gestaltungsfragen stellen und Feedback abwarten.
4. Backlog und Arbeitsstand auf tatsächlichen Stand aktualisieren. Erst nach Benutzerfeedback Styleguide als bestätigt markieren.

Der virtuelle Windows-Server kommt erst beim späteren beruflichen Umzug. Es werden jetzt keine Dienste gebucht, keine Zugangsdaten erzeugt, keine Server freigegeben und keine WSL-/Linux-Installation vorgenommen. Die anschließende echte Anwendung bleibt Django/PostgreSQL nativ unter Windows. CI-Prüfungen können später vorbereitet werden; produktives Deployment kommt mit dem Server.
