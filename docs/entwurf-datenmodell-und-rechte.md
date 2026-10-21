# ENTWURF: Module, Datenmodell und Rollenrechte

Status: **Entwurf, nicht beschlossen**. Stand: 21. Oktober 2026. Übersicht und Entscheidungsvorlage: `docs/entwurf-vorbereitung.md`.
Annahmen aus der Entscheidungsvorlage (B1–B6) gelten, bis du entschieden hast.

## 1. Module der Anwendung

Eine Anwendung („modularer Monolith“): ein Programm, intern in klar getrennte Bereiche aufgeteilt. Keine Microservices.

| Modul | Verantwortung |
| --- | --- |
| `core` | gemeinsame Grundlagen: Änderungsfelder, logisches Löschen, Zeitzonen, Dateispeicher-Abstraktion, Umgebungsprüfung |
| `accounts` | Benutzer, globale Rolle, Anmeldung |
| `projects` | Projekt, Mitgliedschaft, Bucket, Zugriffsermittlung |
| `tasks` | Aufgabe, Zuweisung, Aufgabenverlauf, „Meine Aufgaben“ |
| `planning` | Meilenstein, Planversion, Prognose, Ist, Terminänderungen |
| `reporting` | Statusbericht und veröffentlichter, unveränderlicher Stand |
| `documents` | Vorlagen, Dokumentversionen, Dateien, PDF-Erzeugung |
| `notifications` | Reminder-Einstellungen, Zustellungen, Mail-Adapter |
| `scheduler` | regelmäßige Jobs mit Sperre; ruft nur Funktionen anderer Module auf |
| `audit` | nur anfügbares Änderungsprotokoll |
| `ops` | Gesundheitsendpunkt, Betriebs- und Beispieldatenbefehle |

**Abhängigkeitsrichtung:** `core` ← `accounts` ← `projects` ← `tasks`/`planning` ← `reporting`/`documents` ← `notifications` ← `scheduler`. `audit` hängt nur von `core` ab.

**Regeln:** Jedes Modul trennt Datenmodell, schreibende Funktionen (`services`), lesende, bereits gefilterte Abfragen (`selectors`), Rechteregeln (`policies`) und Seiten (`views`). Andere Module greifen nur über `services` und `selectors` zu. Zirkuläre Abhängigkeiten werden automatisiert verhindert.

## 2. Zentrale Datenobjekte

Allgemein: Zeitstempel in UTC; Änderungsfelder (`created_at/by`, `updated_at/by`); logisches Löschen über `deleted_at/by`; nach außen sichtbare Kennungen sind zufällige UUIDs, damit sie nicht erratbar sind.

### Benutzer, Projekte, Aufgaben

| Objekt | Wichtige Felder | Regeln |
| --- | --- | --- |
| **User** | E-Mail, Anzeigename, globale Rolle (ADMIN, PL, MA, MGMT), aktiv | E-Mail eindeutig ohne Rücksicht auf Groß-/Kleinschreibung. Interne, unveränderliche ID, damit später SSO möglich ist. |
| **Project** | fortlaufende Projektnummer, Name, Start, Ende, archiviert am, gelöscht am, Verweis auf Rolloutplattform (Kennung, URL) | Ende nicht vor Start. Rolloutplattform nur als Verweis, keine Datenübernahme. |
| **ProjectMembership** | Projekt, Benutzer, Projektrolle (PL, MA, MGMT), Beginn, Ende | Je Projekt und Benutzer höchstens eine aktive Mitgliedschaft. Mindestens ein Projektleiter je Projekt. |
| **Bucket** | Projekt, Name, Sortierung, archiviert am | Name je Projekt eindeutig (aktive Buckets). |
| **Task** | Projekt (leer = persönliche Aufgabe), Bucket, Meilenstein (optional), Titel, Beschreibung, Status (OFFEN, IN_ARBEIT, ERLEDIGT), Priorität, Fälligkeit, abgeschlossen am/von, Versionszähler | Projektaufgabe hat immer einen Bucket, persönliche Aufgabe nie. ERLEDIGT genau dann, wenn „abgeschlossen am“ gesetzt ist. Bucket und Meilenstein gehören zum selben Projekt. Versionszähler verhindert, dass zwei gleichzeitige Änderungen sich still überschreiben. |
| **TaskAssignment** | Aufgabe, Benutzer, zugewiesen von/am, entfernt am | Mehrfachzuweisung: viele Zeilen zu **einer** Aufgabe. Je Aufgabe und Person höchstens eine aktive Zuweisung. Nur Projektmitglieder zuweisbar. |
| **TaskEvent** | Aufgabe, Art (angelegt, Status geändert, abgeschlossen, wiedergeöffnet, zugewiesen, Zuweisung entfernt, Fälligkeit geändert …), handelnde Person, Zeitpunkt, alter/neuer Wert | Nur anfügen, nie ändern. Hier bleibt sichtbar, wer wann abgeschlossen und wiedergeöffnet hat. |

### Planung und Terminverlauf

Die vier geforderten Termin-Begriffe werden so getrennt:

| Begriff | Abbildung |
| --- | --- |
| Ursprünglicher Plan | erste **freigegebene** Planversion |
| Aktuell genehmigter Plan | neueste **freigegebene** Planversion |
| Prognose | aktueller Prognosetermin am Meilenstein, jede Änderung im Terminverlauf |
| Tatsächlicher Termin | Ist-Termin am Meilenstein, jede Änderung im Terminverlauf |

| Objekt | Wichtige Felder | Regeln |
| --- | --- | --- |
| **Milestone** | Projekt, Name, Prognose, Ist | Erledigte Aufgaben geben einen Meilenstein nicht automatisch frei. |
| **PlanVersion** | Projekt, laufende Nummer, Zustand (ENTWURF, FREIGEGEBEN, VERWORFEN), Ursache, erstellt von, freigegeben von/am, ersetzt Version | Nach Freigabe unveränderlich. Freigabe nur durch Projektleiter, nie durch ein Datum. |
| **PlanItem** | Planversion, Meilenstein, geplanter Start und geplantes Ende | Je Planversion und Meilenstein ein Eintrag. |
| **DateChange** | Objekt (Meilenstein oder Aufgabe), Art (Plan, Prognose, Ist, Fälligkeit), alt, neu, Zeitpunkt, Verursacher, Ursache, zugehörige Planversion | Nur anfügen. Verschiebungen können dadurch nie durch Überschreiben verschwinden. |

### Berichte, Dokumente, Dateien

| Objekt | Wichtige Felder | Regeln |
| --- | --- | --- |
| **StatusReport** | Projekt, Berichtsmonat, Revision, Zustand (ENTWURF, VERÖFFENTLICHT), Inhaltsfelder, veröffentlicht von/am | Je Projekt, Monat und Revision eindeutig. |
| **PublishedReportSnapshot** | Bericht, eingefrorene Inhalte inkl. Meilensteinwerte, Vorlagen-Version, PDF-Datei, Prüfsumme | Unveränderlich. Eine Korrektur ist eine neue Revision; der alte Stand bleibt abrufbar. |
| **DocumentTemplate** | Schlüssel, Version, Name, Feldbeschreibung | Vorlagen liegen versioniert im Repository. Welche Dokumente es gibt, ist noch offen. |
| **Document / DocumentVersion** | Projekt, Vorlage, laufende Nummer, eingefrorene Daten, Vorlagen-Version, Datei | Versionen unveränderlich. |
| **StoredFile** | UUID, zufälliger Speicherschlüssel, Originalname, Typ, Größe, Prüfsumme, Projekt (optional), hochgeladen von | Download ausschließlich über das Backend mit Rechteprüfung; keine direkt erreichbaren Dateipfade. |

### Reminder und Betrieb

| Objekt | Wichtige Felder | Regeln |
| --- | --- | --- |
| **ReminderSetting** | Benutzer, Sammelmail an/aus, Versandzeit, Zeitzone | Eine Einstellung je Benutzer. |
| **ReminderDelivery** | Benutzer, Art, lokales Datum, Zustand (BEANSPRUCHT, GESENDET, FEHLGESCHLAGEN, ÜBERSPRUNGEN), enthaltene Aufgaben, Versuche, Mail-Modus, gesendet am, Fehler | **Eindeutig je Benutzer, Art und Tag.** Ablauf: Zeile anlegen und speichern, dann senden, dann Zustand setzen. Ein zweiter Lauf am selben Tag scheitert an der Eindeutigkeit, also kein Doppelversand. Erledigte oder gelöschte Aufgaben werden nicht aufgenommen. |
| **JobLock** | Name, Inhaber, gesperrt bis | Verhindert, dass der Scheduler doppelt läuft. |
| **AuditLog** | handelnde Person, Aktion, Objekt, Projekt, Zeitpunkt, Änderungen | Nur anfügen. Optional darf die Anwendung diese Tabelle technisch weder ändern noch löschen. |

### Erweiterungspunkt Phasenmodell

Das Phasenmodell ist offen und wird **nicht** angelegt. Falls es später beschlossen wird, kommt eine Tabelle „Phase“ je Projekt hinzu, auf die Aufgaben und Meilensteine optional verweisen. Das bestehende Modell muss dafür nicht umgebaut werden.

## 3. Rollenrechte (Vorschlag)

G = gilt global, P = nur in Projekten, in denen die Person Mitglied mit dieser Projektrolle ist.

| Aktion | Administrator | Projektleiter | Mitarbeiter | Management |
| --- | --- | --- | --- | --- |
| Projekt anlegen | ja | ja (G), wird dabei Projektleiter | nein | nein |
| Projekt bearbeiten, Steckbrief | ja | ja (P) | nein | nein |
| Projekt archivieren | ja | ja (P) | nein | nein |
| Projekt löschen (logisch, mit Anzeige der betroffenen Inhalte) | ja | nein | nein | nein |
| Team verwalten | ja (protokolliert) | ja (P) | nein | nein |
| Aufgabe anlegen | ja | ja (P) | ja (P) | nein |
| Aufgabe bearbeiten | ja | alle (P) | zugewiesene (P) | nein |
| Aufgabe abschließen | ja | ja (P) | zugewiesene (P) | nein |
| Aufgabe wiederöffnen | ja | ja (P) | nein | nein |
| Prognose ändern | ja | ja (P) | für Zugewiesenes (P) | nein |
| Genehmigten Plan ändern, Freigabe erteilen | **nein** | ja (P) | nein | nein |
| Statusbericht entwerfen | nein | ja (P) | zuarbeiten (P) | nein |
| Statusbericht veröffentlichen | nein | ja (P) | nein | nein |
| Veröffentlichten Bericht lesen, PDF laden | ja | ja (P) | ja (P) | ja (P) |
| Datei hochladen | ja | ja (P) | ja (P) | nein |
| Datei herunterladen | ja | ja (P) | ja (P) | ja (P) |
| Dashboard | alle Projekte | eigene Projekte | eigene Projekte | zugeordnete Projekte, nur lesen |
| Benutzerverwaltung | ja | nein | nein | nein |
| Persönliche Aufgaben | nur eigene | nur eigene | nur eigene | nur eigene |

Erläuterungen:

- Freigaben erteilt laut Produktgrundlage nur der Projektleiter. Der Admin bekommt deshalb bewusst **kein** Freigaberecht.
- Persönliche Aufgaben ohne Projekt sieht nur die Person, die sie angelegt hat, auch der Admin nicht.
- Fachliche Stakeholder sind nicht automatisch Benutzer.
- Die globale Rolle „Projektleiter“ erlaubt das Anlegen von Projekten; was jemand in einem Projekt darf, bestimmt die Projektrolle der Mitgliedschaft.

## 4. Technische Rechteprüfung

1. **Gefilterte Abfragen:** Seiten laden Projekte, Aufgaben und Dateien nur über Abfragen, die bereits auf die erlaubten Projekte der Person eingeschränkt sind. Ein fremdes Objekt existiert für die Person dadurch nicht: Antwort **404**, ohne zu verraten, dass es das Objekt gibt.
2. **Zentrale Rechteregeln:** kleine, einzeln testbare Funktionen wie „darf diese Person diese Aufgabe wiederöffnen?“ in einer Rechtetabelle im Code. Ist ein Objekt sichtbar, die Aktion aber nicht erlaubt: **403**.
3. **Doppelte Prüfung:** Auch die schreibenden Funktionen prüfen die Regeln erneut, nicht nur die Seite. Statuswechsel sperren den Datensatz kurz, damit gleichzeitige Klicks nichts verdoppeln.
4. **Nicht angemeldet:** Weiterleitung zur Anmeldung. Datei-Downloads laufen ausschließlich über das Backend mit derselben Prüfung. Die Django-Verwaltungsoberfläche ist in Prod nur für den Betrieb gedacht oder abgeschaltet.
5. **Tests:** eine Matrix aus Rolle × Aktion × (eigenes Projekt, fremdes Projekt, persönliche Aufgabe) mit erwarteter Antwort; ein Test, der fehlschlägt, wenn eine neue Adresse keinen Eintrag in der Rechtematrix hat; Einzeltests je Rechteregel.
