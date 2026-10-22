# Hinweise für KI-Assistenten (GitHub Copilot, Claude u. a.)

Die verbindlichen Arbeitsregeln dieses Projekts stehen in **`CLAUDE.md`**. Lies sie zuerst und befolge sie, unabhängig davon, welches Werkzeug du bist.

Danach in dieser Reihenfolge lesen:
1. `README.md` (Befehle für Entwicklung, Tests, Demo)
2. `docs/arbeitsstand.md` (aktueller Stand und nächster Schritt)
3. `docs/backlog.md` (Reihenfolge und Wünsche)
4. `docs/decisions/` (getroffene Entscheidungen, z. B. 004 Rechte, 006 Projektstruktur)

Die Rollenbeschreibungen (Projektleitung, Product Owner, Architekt, Entwickler, Tester, Reviewer, Releasemanager) liegen in `.claude/agents/`. Werkzeuge ohne Unteragenten nutzen sie als Leitfaden für die jeweilige Arbeitsweise.

Wichtig:
- Kommunikation auf Deutsch, verständlich für den Benutzer.
- Keine Geheimnisse (`.env`, `.env.demo`) lesen, ausgeben oder in Git aufnehmen.
- Berechtigungen immer im Backend prüfen.
- Vor Änderungen Abnahmekriterien festhalten.
- Ergebnisse mit Tests (`uv run pytest`) nachweisen.
