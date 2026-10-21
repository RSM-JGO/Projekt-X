# Styleguide Vorbereitung

Der Benutzer möchte die optische Gestaltung ausdrücklich gemeinsam festlegen. Noch keine konkrete Gestaltung ist freigegeben. Die Oberfläche soll professionell, übersichtlich und für tägliche Projektarbeit geeignet sein. Die erste Umsetzung muss später betrachtet und angepasst werden können.

## Bestätigte Anforderung zu Ansichten

Produktname: Projekt X. Gewünscht ist eine moderne Gestaltung, gerne mit Pastellfarben. Es gibt noch keine festgelegte Farbpalette oder freigegebene Gestaltungsprobe.

Präzisierung beim Logoentwurf: Lavendel gefällt dem Benutzer nicht. Bevorzugte Farben sind Grün, Blau und Rot. Diese Präferenz bei weiteren Marken- und Gestaltungsentwürfen berücksichtigen; die konkrete Palette bleibt abzustimmen. Logoentwurf assets/branding/projekt-x-logo-v2.png verwendet diese Farben und hat einen transparenten Hintergrund.

Die Anwendung erhält sowohl eine normale helle Ansicht als auch einen Darkmode. Die konkrete Farbpalette und Gestaltung sind noch abzustimmen. Bedienung (vom Benutzer am 21.10.2026 entschieden): ein einfacher Umschalter zwischen Hell und Dunkel, ohne Option „System“, mit gespeicherter persönlicher Auswahl; beim ersten Öffnen gilt die Windows-Einstellung. Vorgeschlagen: konsistente Darstellung in Tabellen, Formularen, Boards und Dialogen. PDF-Ausgaben bleiben unabhängig vom Bildschirmmodus für Versand und Druck geeignet. Die Auswahl beider Modi ist bestätigt. Die Gestaltung der Designvorschau (Pastellfarben, Stil) hat der Benutzer grundsätzlich akzeptiert; der Seitenaufbau, besonders des Arbeitsplatzes, wird später überarbeitet.

Vor der Oberflächenimplementierung abstimmen:

- Produktname, Logo und vorhandene Gestaltungsrichtlinien. Rossmann-Branding aus dem Handbuch ist nicht automatisch für diese Anwendung freigegeben.
- Navigation zwischen persönlichem Arbeitsplatz, Projekten, Managementübersicht und Administration.
- Farbpalette, Schrift, Abstände, Informationsdichte und gegebenenfalls Hell-/Dunkelmodus.
- Tabellen, Aufgabenboards, Formulare, Detailansichten und Dialoge.
- Erkennbare Auswahl-, Fokus-, Lade-, Leer- und Fehlerzustände.
- Statusdarstellung mit Text und Symbolen zusätzlich zu Farbe.
- Bildschirmgrößen und Priorität für Desktop, Tablet und Smartphone.
- PDF-Dokumentgestaltung, die den Exportanforderungen entspricht und nicht bloß Bildschirmansichten druckt.

Empfohlene Abnahme anhand von persönlicher Startseite, Projektübersicht, Aufgabenboard und Statusberichtsvorschau mit klar gekennzeichneten Beispieldaten. Erst danach Komponenten und Gestaltungsregeln festschreiben.

## Vom Benutzer festgelegte Gestaltungsregeln (21.10.2026)

- **Schrift ist immer dunkelgrau oder schwarz**, im Darkmode hellgrau. Das gilt auch für Links, Statuschips, Navigation und Buttons. Farbige Schrift, etwa Lila, wird nicht verwendet. Pastellfarben dienen nur als Flächen-, Linien- und Symbolfarben. Links sind am Unterstrich erkennbar.
- **Gleichartige Kästen nebeneinander sind gleich hoch** und haben die gleiche Oberkante. Ihr Kopfbereich ist einheitlich aufgebaut.
- **Darstellung:** ein einfacher Umschalter Hell/Dunkel ohne Option „System“.
- **Logo (vom Benutzer bereitgestellt, 21.10.2026):** Bildmarke „X“ in Rot, Grün und Blau plus Schriftzug „Projekt X“ in Blau, mit transparentem Hintergrund. Datei `design/assets/logo-projekt-x.webp` (2000 × 667 px). Im Kopf der Anwendung 38 px hoch, auf dem Handy 30 px.
- **Einheitliche Farbbedeutung, abgeleitet aus dem Logo:**
  - **Grün** = gut / im Plan / erledigt.
  - **Orange** = beobachten / heute fällig / leichte Verzögerung.
  - **Rot** = kritisch / überfällig / größere Verzögerung.
  - **Grau** = unbekannt / Daten veraltet.
  - **Logoblau** und ein helles Türkis nur für Nicht-Status-Elemente: Navigation, Markierungen, Buttons, Hinweise.
  - Status-Farben werden nicht für Dekoration verwendet, etwa für Personen-Avatare. Diese sind neutral grau, der angemeldete Benutzer ist blau.
