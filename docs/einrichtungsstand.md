# Einrichtungsstand

Stand: 21. Oktober 2026.

## Nachgewiesen

- GitHub-Konto jago1698 und privates Repository https://github.com/jago1698/projektmanagement-software vorhanden.
- Lokales Repository auf main; origin zeigt auf das private Repository.
- Lokale Commit-Identität mit GitHub-Namen und bestätigter noreply-Adresse eingerichtet.
- Erster Commit 46ba935 erstellt und erfolgreich nach origin/main hochgeladen; main verfolgt origin/main.
- Claude-Code-Sitzung „Projektordner Einrichtungsprüfung“ im Ordner C:\Users\jango\Documents\Projektmanagement-Software gestartet.
- Benutzer hat Workspace-Vertrauen selbst bestätigt.
- Claude hat die Projektunterlagen gelesen und alle sechs Unteragenten als tatsächlich aufrufbare Agententypen erkannt. Ein Probelauf der einzelnen Rollen ist noch nicht erfolgt.

## Lokale Werkzeuglücke

Claude meldet, dass der Kurzaufruf git in seiner PowerShell-Sitzung nicht gefunden wird. Git ist für die bisherige Vorbereitung unter folgendem vollständigen Pfad verfügbar und wurde darüber erfolgreich verwendet:

`C:\Users\jango\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe`

Dieser Pfad gehört zu einer verwalteten Codex-Laufzeit und kann sich bei Änderungen der Installation ändern. Er ist ein vorläufiger Weg, keine dauerhafte Projektabhängigkeit. Vor regulärer Entwicklung eine normale Git-for-Windows-Installation beziehungsweise einen stabilen Suchpfad prüfen und abstimmen. Keine Anwendung soll diesen Git-Pfad zur Laufzeit benötigen.

Claudes Einrichtungsbericht wurde teilweise vor dem ersten Commit erstellt. Seine Aussage „noch kein Commit“ ist inzwischen überholt. Das ist kein Fehler im Repository.

## Noch offen

- Dauerhaft nutzbare Git-Installation für Claude prüfen; Upload aus der aktuellen Vorbereitung funktioniert.
- Tech-Stack, Architektur und Datenmodell abstimmen.
- Styleguide gemeinsam festlegen.
- Dev-/Prod-Trennung und Deployment-Pipeline konkretisieren und später umsetzen.
- Anwendung und Betriebsumgebungen sind noch nicht implementiert.
