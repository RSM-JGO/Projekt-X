# ENTWURF: Datenmodell Projektbereich (Etappe 4a)

Status: **Vom Benutzer am 22.10.2026 bestätigt**; die vier Punkte unten sind nach Empfehlung entschieden. Entwurf des Softwarearchitekten, vom Projektleiter zusammengefasst. Grundlage: Entscheidungen 003, 004 und 006, Entwurf F (Termine) und die fachliche Orientierung M0–M5.

## Bausteine

| Baustein | Inhalt | Wichtigste Regel |
| --- | --- | --- |
| **Standardkatalog** (Meilenstein- und Lieferobjekt-Vorlagen) | M0–M5 mit Abschnittsname, Titel, Ziel und Standard-Lieferobjekten (Titel, Pflicht, Bereich) | Wird beim Anlegen eines Projekts **kopiert**, nie live verknüpft. Spätere Änderungen am Standard verändern laufende Projekte nicht. In 4a per Migration befüllt, noch ohne eigene Pflegeseite. |
| **Meilenstein** je Projekt | Kürzel, Abschnittsname, Titel, Ziel, Reihenfolge, ausgeblendet, aktuelle Prognose, aktuelles Ist | Kürzel je Projekt eindeutig. Meilensteine werden **nur ausgeblendet, nie gelöscht**, weil Freigaben und Planstände darauf verweisen. Eigene Meilensteine lassen sich ergänzen. |
| **Lieferobjekt** | Titel, Pflicht, Status (fehlt, in Arbeit, vorhanden), Bereich, Verantwortlich, Notiz | Gehört sicher zum selben Projekt. Verantwortlich kann nur ein aktiver Projektleiter oder Mitarbeiter sein. Der Status wird in 4a **manuell** gepflegt; die Verknüpfung mit echten Dokumenten folgt mit den Bereichen. |
| **Freigabe** | Ampel (grün, orange, rot), Entscheidung, Datum, Beteiligte (Konten und Freitext für Externe), Grundlage, Auflagen, gültig bis, erteilt von, als Administrator | **Schnappschuss der fehlenden Pflichtdokumente**; wenn welche fehlen, muss die Warnung bestätigt werden. Orange braucht Auflagen. Freigaben sind **unveränderlich**; eine Korrektur ist eine neue Freigabe, die die alte ersetzt. |
| **Planversion** | laufende Nummer, Status (Entwurf, genehmigt, abgelöst), Anlass, genehmigt von/am | Je Projekt höchstens ein Entwurf. Genehmigte Versionen sind unveränderlich. |
| **Planeintrag** | entweder Projektzeitraum (Beginn/Ende) oder Meilenstein (ein Termin) | Je Version genau ein Projektzeitraum und höchstens ein Eintrag je Meilenstein. |
| **Terminänderung** | Ziel, Terminpunkt (Beginn, Ende, Termin), Art (Prognose oder Ist), alt, neu, Begründung, Person | Nur anfügbar. So bleibt jede Verschiebung sichtbar. |

**Die vier Terminbegriffe:**
- **Ursprünglicher Plan** = erste genehmigte Planversion, die das Objekt enthält.
- **Genehmigter Plan** = neueste genehmigte Version.
- **Prognose** und **Ist** sind aktuelle Werte mit vollständigem Verlauf.

**Planversion und Meilensteinfreigabe sind getrennt:** Eine Terminverschiebung braucht keine neue Meilensteinfreigabe, und eine Freigabe ändert keine Termine. Eine Freigabe kann aber auf eine im selben Schritt genehmigte Planversion verweisen, typisch bei M1.

## Rechte (Prüfung immer im Backend)

- **Lesen:** alle aktiven Mitglieder des Projekts, auch Management.
- **Schreiben:** an Meilensteinen, Lieferobjekten, Prognose und Ist, Planversionen sowie Freigaben erteilen: **Projektleiter und Administrator** (004). Administratoraktionen werden gekennzeichnet und protokolliert.

## Abgeleiteter Status (berechnet, nicht gespeichert)

- **Je Meilenstein:** Anzahl der Lieferobjekte, die noch nicht „vorhanden“ sind, getrennt nach Pflicht.
- **Je Menüpunkt:** offene Lieferobjekte dieses Bereichs im **aktuellen Meilenstein**, angezeigt z. B. als „M1: 2 offen“.
- **Symbole:** ✓ alles vorhanden, ● teilweise, ○ nichts begonnen.
- Ein Meilenstein ohne Lieferobjekte oder ohne Termin gilt als **„nicht bewertet“, nie als erledigt**.

## Migration bestehender Projekte

- Jedes Projekt bekommt M0–M5 mit Standard-Lieferobjekten im Status „fehlt“.
- Aus dem bisherigen Projektzeitraum entsteht Planversion 1.
- Der bisherige Projektzeitraum bleibt als Anzeige. Nach der ersten Genehmigung ändert er sich nur noch über Planversionen und wird dabei mitgeführt.

## Später, nicht in 4a

- Verknüpfung von Lieferobjekten mit echten Objekten, z. B. dem Projektauftrag ab 4b, mit automatischem Status.
- Pflegeseite für den Standardkatalog.
- Vorgänge.
- Aufgabe ↔ Meilenstein (Etappe 5).
- Phasenbezug (F12).

## Risiken

1. Bisheriger Projektzeitraum und genehmigter Plan dürfen nicht auseinanderlaufen; das braucht eine Synchronisationsregel mit Test.
2. Die Regel für den „aktuellen Meilenstein“ muss bei ausgeblendeten, roten oder abgelaufenen Freigaben eindeutig sein.
3. Ein späteres echtes Phasenmodell (F12) erfordert eine Migration.
4. Ersetzte Freigaben müssen in der Oberfläche verständlich dargestellt werden.

## Entscheidungen des Benutzers (22.10.2026: alle vier nach Empfehlung)

1. **Planversion 1 bestehender Projekte:** als Entwurf, den die Projektleitung genehmigt, oder automatisch als „genehmigt (übernommen)“? *Empfehlung: Entwurf, weil ehrlich – es gab noch keine echte Genehmigung.*
2. **„Aktueller Meilenstein“:** der erste sichtbare Meilenstein ohne gültige grüne oder orange Freigabe? *Empfehlung: ja. Rote oder abgelaufene Freigaben zählen als offen.*
3. **Lieferobjekt-Status durch Mitarbeiter:** Darf eine verantwortliche Mitarbeiterin den Status „ihres“ Lieferobjekts setzen? *Empfehlung: ja, nur den Status ihrer eigenen Lieferobjekte; alles andere bleibt bei Projektleitung und Administrator.*
4. **„Gültig bis“ einer Freigabe:** Datum oder Freitext? *Empfehlung: optionales Datum plus Auflagen als Text.*
