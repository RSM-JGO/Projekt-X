# Auftrag: Erster echter Ablauf (V07)

Status: Vom Benutzer am 21.10.2026 beauftragt. **V07a vom Benutzer am 21.10.2026 abgenommen** (inkl. Entscheidung 004). **V07b vom Benutzer am 21.10.2026 abgenommen** („Das passt … mach erstmal weiter“). Zusatzregel nach Empfehlung des Projektleiters: Zuständige ändern nur Projektleiter und Administrator.

**Grundlagen:**
- `docs/decisions/001` bis `003`;
- `docs/entwurf-nacharbeit.md` (Rollenmodell D, persönliche Aufgaben E);
- `docs/entwurf-erster-entwicklungsabschnitt.md` (ursprüngliche Kriterien);
- `docs/styleguide-briefing.md` (Gestaltungsregeln).

## Ziel

Ein kleiner, vollständiger Ablauf mit echter Datenbank, der die riskantesten Grundlagen nachweist: Anmeldung, Projektgrenzen, Rollenrechte, Mehrfachzuweisung sowie Abschließen und Wiederöffnen mit Verlauf. Er wird in zwei überprüfbaren Schritten umgesetzt, jeder mit eigenem Test, eigenem Review und eigener Abnahme durch den Benutzer.

## Schritt V07a: Anmeldung, Projekte, Mitgliedschaften

**Umfang:**
- An- und Abmelden mit Konten, die der Administrator anlegt. Es gibt keine Selbstregistrierung.
- Die E-Mail-Adresse ist eindeutig, ohne Rücksicht auf Groß-/Kleinschreibung.
- Benutzerbefugnisse `is_admin`, „Projekte anlegen“ und „Projekte löschen“ (nur Datenmodell; Löschen selbst folgt später).
- Projekte anlegen und bearbeiten: Name, Beschreibung, Zeitraum.
- Mitgliedschaften mit einer oder mehreren Projektrollen (Projektleiter, Mitarbeiter, Management). Je Projekt gibt es mindestens einen aktiven Projektleiter.
- Projektübersicht mit allen Projekten. Fremde Projekte erscheinen nur mit Eckdaten und lassen sich nicht öffnen (Entscheidung 004).
- Seiten im Stil der Designvorschau: Logo, Hell/Dunkel, Farbregeln.
- Neue Pakete, **gesonderte Freigabe nötig**: `argon2-cffi` für sicheres Passwort-Hashing und `django-axes` als Schutz gegen Passwortraten.

**Abnahmekriterien:**
1. Ohne Anmeldung liefert keine Seite Projektdaten; die Seite leitet zur Anmeldung weiter.
2. Ein falsches Passwort wird abgewiesen, ohne zu verraten, ob das Konto existiert. Nach mehreren Fehlversuchen wird gesperrt. Nach dem Abmelden ist die Sitzung ungültig.
3. Eine zweite Person mit derselben E-Mail-Adresse, auch in anderer Schreibweise, kann nicht angelegt werden.
4. *(geändert durch Entscheidung 004)* Alle angemeldeten Personen sehen alle Projekte in der Übersicht. Fremde Projekte zeigen nur Name, Zeitraum und Projektleitung, ohne Link, Beschreibung oder Mitglieder. Öffnen dürfen nur aktive Mitglieder und der Administrator. Ein direkter Aufruf eines fremden Projekts liefert 403 ohne Projektdaten; eine nicht existierende Adresse liefert 404.
5. Nur Personen mit der Befugnis „Projekte anlegen“ oder Administratoren legen Projekte an. Wer ein Projekt anlegt, wird automatisch dessen Projektleiter.
6. Das Entfernen des letzten aktiven Projektleiters wird abgelehnt.
7. Rollenänderungen und Mitgliedschaftsänderungen werden protokolliert: wer, wann, was.
8. Management und Mitarbeiter können Projekte nicht bearbeiten. Das Backend prüft das; eine direkte Anfrage wird mit 403 abgewiesen. *(Entscheidung 004)* Der Administrator darf alles; seine Aktionen werden als Administratoraktion protokolliert. Die Projektleiter-Regel gilt auch für ihn.

## Schritt V07b: Gemeinsame Aufgaben

**Umfang:**
- Buckets je Projekt.
- Aufgaben mit Titel, Bucket, Fälligkeit und einer oder mehreren zugewiesenen Personen.
- Filter Offen/Erledigt/Alle.
- Abschließen und Wiederöffnen mit Verlauf.
- „Meine Aufgaben“ über alle Projekte.
- Persönliche Aufgaben ohne Projekt.
- Der Administrator darf alles, auch bei persönlichen Aufgaben anderer; protokolliert (Entscheidung 004).

**Abnahmekriterien:**
1. Eine Aufgabe mit zwei zugewiesenen Personen ist **ein** Datensatz und erscheint im Projekt sowie in „Meine Aufgaben“ beider Personen.
2. Zuweisen lässt sich nur an aktive Projektleiter oder Mitarbeiter des Projekts; eine Management-Rolle allein reicht nicht.
3. Schließt eine zugewiesene Person ab, ist die Aufgabe für alle erledigt. Angezeigt wird, wer wann abgeschlossen hat.
4. Erledigte Aufgaben bleiben über die Filter Erledigt und Alle sichtbar.
5. Der Projektleiter öffnet wieder; der frühere Abschluss bleibt im Verlauf sichtbar. Ein Mitarbeiter kann nicht wiederöffnen (403).
6. Aufgaben aus Projekt A sind für Personen, die nur in Projekt B Mitglied sind, per direkter Anfrage weder lesbar noch änderbar (403 oder 404, ohne Daten).
7. *(geändert durch Entscheidung 004)* Eine persönliche Aufgabe sehen und bearbeiten nur ihr Eigentümer und der Administrator; alle anderen erhalten 404.
8. *(geändert durch Entscheidung 004)* Ändert der Administrator eine Projektaufgabe oder eine persönliche Aufgabe, steht die Änderung mit altem und neuem Wert und als Administratoraktion gekennzeichnet im Verlauf.
9. Zwei gleichzeitige Abschlüsse erzeugen genau ein Abschlussereignis.
10. Die Daten bleiben nach einem Neustart erhalten. Beispieldaten sind gekennzeichnet und lassen sich nur mit `DEBUG` laden.

## Prüfung je Schritt

- Automatisierte Tests, mindestens für alle Rechte- und Datenkriterien, mit einer Rechtematrix aus Rolle × Aktion × eigenes oder fremdes Projekt bzw. persönliche Aufgabe.
- Prüfungen: `ruff`, `check` und `makemigrations --check`.
- Kurzer Browsertest durch den Projektleiter, ein unabhängiges Review und anschließend die fachliche Abnahme durch den Benutzer.

## Nicht enthalten

Meilensteine und Planstände, Dashboard, Statusbericht und PDF, Dateien, Kommentare, Board- und Kalenderansicht, Reminder und E-Mail, Archivieren und Löschen, SSO, Passwort-Zurücksetzen per Mail, externe Demo, CI sowie die Überarbeitung des Arbeitsplatz-Aufbaus.
