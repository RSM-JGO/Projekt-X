# Zoomen in der mobilen Ansicht unterbinden

Datum: 21. Oktober 2026. Status: **beschlossen** durch den Benutzer („Ich möchte es unterbinden!“), nachdem der Projektleiter auf die Folgen für die Barrierefreiheit hingewiesen hatte.

## Entscheidung

Projekt X unterbindet das Zoomen in der mobilen Ansicht:
- Der Viewport ist auf `maximum-scale=1, user-scalable=no` gesetzt.
- Eingabefelder haben mindestens 16 px Schrift, damit iPhones beim Antippen nicht automatisch hineinzoomen.
- `touch-action: manipulation` verhindert den Doppeltipp-Zoom.

## Konsequenzen

- **Barrierefreiheit:** Die Entscheidung weicht von WCAG 1.4.4 ab („Text vergrößerbar“). Menschen mit Sehschwäche können nicht mehr per Geste vergrößern. Die Systemeinstellung für die Schriftgröße bzw. der Browser-Zoom bleiben je nach Gerät möglich.
- **iPhone/Safari** ignoriert `user-scalable=no` seit iOS 10 teilweise. Ein vollständiges Sperren ist dort technisch nicht garantiert; das automatische Zoomen beim Antippen von Feldern ist aber behoben.
- Wird Projekt X beim Arbeitgeber eingesetzt, kann dort eine Barrierefreiheitsvorgabe gelten. Die Entscheidung ist dann erneut zu prüfen.

Betroffen: Backlog F23; `src/templates/base.html`, `src/static/css/app.css`.
