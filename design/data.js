/*
 * Projekt X – Designvorschau
 * BEISPIELDATEN. Alle Personen, Projekte und Werte sind frei erfunden.
 * Keine produktiven Daten, keine echten Namen, keine echten Projekte.
 * Datumswerte im Format JJJJ-MM-TT. Stichtag der Vorschau: meta.today.
 */
window.PX_DATA = {
  meta: {
    today: "2026-10-21",
    currentUserId: "u-jan",
    staleAfterDays: 30
  },

  users: [
    { id: "u-jan",   name: "Jan (Beispiel)",          initials: "JA", role: "Projektleiter", tone: "brand" },
    { id: "u-mara",  name: "Mara Klein (Beispiel)",   initials: "MK", role: "Projektleiter", tone: "neutral" },
    { id: "u-tom",   name: "Tom Berger (Beispiel)",   initials: "TB", role: "Mitarbeiter",   tone: "neutral" },
    { id: "u-lea",   name: "Lea Schmidt (Beispiel)",  initials: "LS", role: "Projektleiter", tone: "neutral" },
    { id: "u-ole",   name: "Ole Hansen (Beispiel)",   initials: "OH", role: "Mitarbeiter",   tone: "neutral" },
    { id: "u-sina",  name: "Sina Wolf (Beispiel)",    initials: "SW", role: "Mitarbeiter",   tone: "neutral" },
    { id: "u-deniz", name: "Deniz Arslan (Beispiel)", initials: "DA", role: "Mitarbeiter",   tone: "neutral" }
  ],

  projects: [
    {
      id: "filialnetz",
      name: "Filialnetz Upgrade (Beispiel)",
      goal: "Netzwerktechnik in 120 Beispielfilialen in drei Wellen modernisieren.",
      sponsor: "IT-Infrastruktur (Beispiel)",
      leadId: "u-jan",
      start: "2026-03-02",
      end: "2027-02-26",
      reportedStatus: "beobachten",
      lastReport: "2026-10-14",
      decision: "Freigabe Rolloutwelle 3 trotz 12 Tagen Prognoseverzug – Entscheidung bis 30.10.2026 erbeten.",
      buckets: [
        { id: "planung", name: "Planung" },
        { id: "vorbereitung", name: "Vorbereitung" },
        { id: "rollout", name: "Rollout Welle 3" },
        { id: "nachbereitung", name: "Nachbereitung" }
      ],
      milestones: [
        { id: "fn-m1", name: "Pilotfilialen umgestellt",      baseline: "2026-06-30", approved: "2026-07-15", forecast: "2026-07-15", actual: "2026-07-14" },
        { id: "fn-m2", name: "Freigabe Welle 3",              baseline: "2026-10-30", approved: "2026-11-06", forecast: "2026-11-18", actual: null },
        { id: "fn-m3", name: "Welle 3 abgeschlossen",         baseline: "2026-12-18", approved: "2027-01-22", forecast: "2027-01-29", actual: null },
        { id: "fn-m4", name: "Projektabschluss",              baseline: "2027-02-26", approved: "2027-02-26", forecast: "2027-02-26", actual: null }
      ]
    },
    {
      id: "kasse",
      name: "Kassensystem Migration (Beispiel)",
      goal: "Kassenserver auf neue Plattform migrieren, Pilot in zwei Beispielfilialen.",
      sponsor: "Filial-IT (Beispiel)",
      leadId: "u-mara",
      start: "2026-07-01",
      end: "2027-01-29",
      reportedStatus: "im-plan",
      lastReport: "2026-10-16",
      decision: null,
      buckets: [
        { id: "analyse", name: "Analyse" },
        { id: "test", name: "Test" },
        { id: "umstellung", name: "Umstellung" }
      ],
      milestones: [
        { id: "ka-m1", name: "Testumgebung bereit", baseline: "2026-10-02", approved: "2026-10-02", forecast: "2026-10-02", actual: "2026-09-30" },
        { id: "ka-m2", name: "Abnahmetest",         baseline: "2026-11-13", approved: "2026-11-13", forecast: "2026-11-13", actual: null },
        { id: "ka-m3", name: "Go-live Pilot",       baseline: "2026-12-04", approved: "2026-12-04", forecast: "2026-12-04", actual: null }
      ]
    },
    {
      id: "wlan",
      name: "WLAN-Modernisierung Lager (Beispiel)",
      goal: "Flächendeckendes WLAN für Scanner in zwei Beispiel-Lagerhallen.",
      sponsor: "Logistik (Beispiel)",
      leadId: "u-jan",
      start: "2026-08-03",
      end: "2027-02-12",
      reportedStatus: "kritisch",
      lastReport: "2026-10-12",
      decision: "Alternativlieferant beauftragen? Mehrkosten ca. 4.000 € (Beispielwert), dafür etwa 4 Wochen früher.",
      buckets: [
        { id: "ausleuchtung", name: "Ausleuchtung" },
        { id: "beschaffung", name: "Beschaffung" },
        { id: "installation", name: "Installation" }
      ],
      milestones: [
        { id: "wl-m1", name: "Ausleuchtung abgeschlossen", baseline: "2026-09-15", approved: "2026-09-15", forecast: "2026-09-18", actual: "2026-09-18" },
        { id: "wl-m2", name: "Access Points geliefert",    baseline: "2026-10-15", approved: "2026-10-30", forecast: "2026-12-04", actual: null },
        { id: "wl-m3", name: "Inbetriebnahme Halle A",     baseline: "2026-11-20", approved: "2026-12-11", forecast: "2027-01-15", actual: null }
      ]
    },
    {
      id: "drucker",
      name: "Druckerflotte Erneuerung (Beispiel)",
      goal: "Altgeräte in Zentrale und Beispielfilialen durch verwaltete Drucker ersetzen.",
      sponsor: "Arbeitsplatz-IT (Beispiel)",
      leadId: "u-tom",
      start: "2026-05-04",
      end: "2026-12-18",
      reportedStatus: "im-plan",
      lastReport: "2026-08-28",
      decision: null,
      buckets: [
        { id: "bestand", name: "Bestandsaufnahme" },
        { id: "austausch", name: "Austausch" }
      ],
      milestones: [
        { id: "dr-m1", name: "Bestandsliste final", baseline: "2026-08-14", approved: "2026-08-14", forecast: "2026-08-20", actual: "2026-08-20" },
        { id: "dr-m2", name: "Austausch Zentrale",  baseline: "2026-10-30", approved: "2026-10-30", forecast: "2026-10-30", actual: null }
      ]
    },
    {
      id: "win11",
      name: "Client-Rollout Windows 11 (Beispiel)",
      goal: "Arbeitsplatzrechner der Beispielverwaltung auf Windows 11 umstellen.",
      sponsor: "Arbeitsplatz-IT (Beispiel)",
      leadId: "u-lea",
      start: "2026-09-01",
      end: "2027-03-31",
      reportedStatus: "im-plan",
      lastReport: "2026-10-20",
      decision: null,
      buckets: [
        { id: "paketierung", name: "Paketierung" },
        { id: "pilot", name: "Pilot" },
        { id: "rollout", name: "Rollout" }
      ],
      milestones: [
        { id: "w11-m1", name: "Pilotgruppe migriert",  baseline: "2026-11-06", approved: "2026-11-06", forecast: "2026-11-04", actual: null },
        { id: "w11-m2", name: "Rollout abgeschlossen", baseline: "2027-03-31", approved: "2027-03-31", forecast: "2027-03-31", actual: null }
      ]
    }
  ],

  tasks: [
    /* Filialnetz Upgrade */
    {
      id: "t-101", projectId: "filialnetz", bucketId: "planung", milestoneId: "fn-m2",
      title: "Hardwareliste Welle 3 abstimmen", due: "2026-10-16", status: "offen",
      assigneeIds: ["u-jan", "u-mara"],
      description: "Gerätetypen und Stückzahlen für die 40 Beispielfilialen der Welle 3 mit dem Einkauf abstimmen.",
      comments: [
        { by: "u-mara", at: "2026-10-20 09:12", text: "Sollen die Ersatzgeräte (5 %) direkt mitbestellt werden?" }
      ],
      history: [
        { type: "created", by: "u-jan", at: "2026-10-01 10:00" }
      ]
    },
    {
      id: "t-102", projectId: "filialnetz", bucketId: "vorbereitung", milestoneId: "fn-m2",
      title: "Filialtermine mit Regionalleitung bestätigen", due: "2026-10-21", status: "offen",
      assigneeIds: ["u-jan", "u-tom", "u-sina"],
      description: "Umstellungstermine je Filiale mit den Regionalleitungen (Beispiel) bestätigen und in der Terminliste festhalten.",
      comments: [
        { by: "u-tom", at: "2026-10-19 14:30", text: "Region Nord hat alle Termine bestätigt." },
        { by: "u-sina", at: "2026-10-20 08:45", text: "Region Süd fehlt noch, Rückmeldung heute erwartet." }
      ],
      history: [
        { type: "created", by: "u-jan", at: "2026-10-05 11:20" }
      ]
    },
    {
      id: "t-103", projectId: "filialnetz", bucketId: "vorbereitung", milestoneId: "fn-m2",
      title: "Rollback-Plan dokumentieren", due: "2026-10-23", status: "offen",
      assigneeIds: ["u-lea", "u-ole"],
      description: "Vorgehen beschreiben, falls eine Filialumstellung zurückgenommen werden muss.",
      comments: [
        { by: "u-lea", at: "2026-10-20 16:05", text: "Entwurf liegt vor, bitte um Freigabe." }
      ],
      history: [
        { type: "created", by: "u-jan", at: "2026-10-06 09:00" }
      ]
    },
    {
      id: "t-104", projectId: "filialnetz", bucketId: "planung", milestoneId: "fn-m2",
      title: "Netzwerkkomponenten bestellen", due: "2026-10-09", status: "erledigt",
      assigneeIds: ["u-mara"],
      description: "Bestellung der Switches und Router für Welle 3 auslösen.",
      comments: [],
      history: [
        { type: "created", by: "u-jan", at: "2026-09-21 10:00" },
        { type: "completed", by: "u-mara", at: "2026-10-08 15:42" }
      ]
    },
    {
      id: "t-105", projectId: "filialnetz", bucketId: "nachbereitung", milestoneId: "fn-m1",
      title: "Pilotfeedback auswerten", due: "2026-08-14", status: "erledigt",
      assigneeIds: ["u-jan", "u-ole"],
      description: "Rückmeldungen der Pilotfilialen sammeln und Maßnahmen ableiten.",
      comments: [
        { by: "u-ole", at: "2026-08-12 10:10", text: "Zwei Filialen fehlten noch, jetzt vollständig." }
      ],
      history: [
        { type: "created", by: "u-jan", at: "2026-07-20 09:00" },
        { type: "completed", by: "u-ole", at: "2026-08-10 17:00" },
        { type: "reopened", by: "u-jan", at: "2026-08-11 08:30" },
        { type: "completed", by: "u-ole", at: "2026-08-13 12:15" }
      ]
    },
    {
      id: "t-106", projectId: "filialnetz", bucketId: "rollout", milestoneId: "fn-m3",
      title: "Installationsanleitung Welle 3 aktualisieren", due: "2026-11-04", status: "offen",
      assigneeIds: ["u-tom", "u-sina", "u-jan"],
      description: "Anleitung für Vor-Ort-Techniker an neue Gerätetypen anpassen.",
      comments: [],
      history: [
        { type: "created", by: "u-jan", at: "2026-10-10 13:00" }
      ]
    },
    {
      id: "t-107", projectId: "filialnetz", bucketId: "rollout", milestoneId: null,
      title: "Vor-Ort-Techniker einplanen", due: "2026-11-12", status: "offen",
      assigneeIds: ["u-ole"],
      description: "Einsatzplanung der Techniker für die Umstellungstage.",
      comments: [],
      history: [
        { type: "created", by: "u-jan", at: "2026-10-10 13:05" }
      ]
    },

    /* WLAN-Modernisierung Lager */
    {
      id: "t-201", projectId: "wlan", bucketId: "beschaffung", milestoneId: "wl-m2",
      title: "Lieferverzug mit Händler klären", due: "2026-10-14", status: "offen",
      assigneeIds: ["u-jan", "u-deniz"],
      description: "Verbindlichen Liefertermin für die Access Points einholen.",
      comments: [
        { by: "u-deniz", at: "2026-10-19 11:00", text: "@Jan Händler nennt jetzt Anfang Dezember – sollen wir eskalieren?" }
      ],
      history: [
        { type: "created", by: "u-jan", at: "2026-10-02 09:30" }
      ]
    },
    {
      id: "t-202", projectId: "wlan", bucketId: "beschaffung", milestoneId: "wl-m2",
      title: "Alternativlieferant anfragen", due: "2026-10-22", status: "offen",
      assigneeIds: ["u-deniz"],
      description: "Angebot eines zweiten Lieferanten (Beispiel) mit Lieferzeit einholen.",
      comments: [],
      history: [
        { type: "created", by: "u-jan", at: "2026-10-15 10:00" }
      ]
    },
    {
      id: "t-203", projectId: "wlan", bucketId: "ausleuchtung", milestoneId: "wl-m1",
      title: "Ausleuchtungsbericht ablegen", due: "2026-09-18", status: "erledigt",
      assigneeIds: ["u-sina"],
      description: "Messbericht der Ausleuchtung im Projektordner ablegen.",
      comments: [],
      history: [
        { type: "created", by: "u-jan", at: "2026-09-01 09:00" },
        { type: "completed", by: "u-sina", at: "2026-09-18 16:20" }
      ]
    },
    {
      id: "t-204", projectId: "wlan", bucketId: "installation", milestoneId: "wl-m3",
      title: "Montageplan Halle A erstellen", due: "2026-11-10", status: "offen",
      assigneeIds: ["u-sina", "u-ole"],
      description: "Montagepunkte, Hubbühne und Zeitfenster für Halle A planen.",
      comments: [],
      history: [
        { type: "created", by: "u-jan", at: "2026-10-12 14:00" }
      ]
    },

    /* Kassensystem Migration */
    {
      id: "t-301", projectId: "kasse", bucketId: "test", milestoneId: "ka-m2",
      title: "Testfälle Kartenzahlung durchführen", due: "2026-10-23", status: "offen",
      assigneeIds: ["u-jan", "u-lea"],
      description: "Testfälle 1–24 (Kartenzahlung) in der Testumgebung durchführen und Ergebnisse dokumentieren.",
      comments: [],
      history: [
        { type: "created", by: "u-mara", at: "2026-10-05 08:00" }
      ]
    },
    {
      id: "t-302", projectId: "kasse", bucketId: "analyse", milestoneId: "ka-m1",
      title: "Schnittstellenbeschreibung prüfen", due: "2026-09-25", status: "erledigt",
      assigneeIds: ["u-mara", "u-deniz"],
      description: "Schnittstelle zur Warenwirtschaft (Beispiel) prüfen.",
      comments: [],
      history: [
        { type: "created", by: "u-mara", at: "2026-09-01 09:00" },
        { type: "completed", by: "u-deniz", at: "2026-09-24 11:45" }
      ]
    },
    {
      id: "t-303", projectId: "kasse", bucketId: "umstellung", milestoneId: "ka-m3",
      title: "Schulungsunterlagen Kasse vorbereiten", due: "2026-11-20", status: "offen",
      assigneeIds: ["u-mara"],
      description: "Kurzanleitung für Filialpersonal erstellen.",
      comments: [],
      history: [
        { type: "created", by: "u-mara", at: "2026-10-01 09:00" }
      ]
    },

    /* Druckerflotte Erneuerung */
    {
      id: "t-401", projectId: "drucker", bucketId: "bestand", milestoneId: "dr-m1",
      title: "Gerätebestand Filialen erfassen", due: "2026-08-14", status: "erledigt",
      assigneeIds: ["u-tom"],
      description: "Vorhandene Drucker je Standort erfassen.",
      comments: [],
      history: [
        { type: "created", by: "u-tom", at: "2026-07-01 09:00" },
        { type: "completed", by: "u-tom", at: "2026-08-20 10:00" }
      ]
    },
    {
      id: "t-402", projectId: "drucker", bucketId: "austausch", milestoneId: "dr-m2",
      title: "Austauschtermine Zentrale planen", due: "2026-10-19", status: "offen",
      assigneeIds: ["u-tom"],
      description: "Termine für den Geräteaustausch in der Zentrale abstimmen.",
      comments: [],
      history: [
        { type: "created", by: "u-tom", at: "2026-08-25 09:00" }
      ]
    },

    /* Client-Rollout Windows 11 – bewusst ohne erledigte Aufgaben (Leerzustand im Filter „Erledigt“) */
    {
      id: "t-501", projectId: "win11", bucketId: "paketierung", milestoneId: "w11-m1",
      title: "Softwarepakete testen", due: "2026-10-28", status: "offen",
      assigneeIds: ["u-lea", "u-sina", "u-jan"],
      description: "Standardpakete auf dem neuen Image testen.",
      comments: [],
      history: [
        { type: "created", by: "u-lea", at: "2026-10-01 10:00" }
      ]
    },
    {
      id: "t-502", projectId: "win11", bucketId: "pilot", milestoneId: "w11-m1",
      title: "Pilotnutzer informieren", due: "2026-11-02", status: "offen",
      assigneeIds: ["u-ole"],
      description: "Pilotgruppe per Infomail (Beispieltext) über Ablauf informieren.",
      comments: [],
      history: [
        { type: "created", by: "u-lea", at: "2026-10-08 10:00" }
      ]
    },

    /* Persönliche Aufgabe ohne Projekt */
    {
      id: "t-900", projectId: null, bucketId: null, milestoneId: null,
      title: "Urlaubsvertretung abstimmen", due: "2026-10-23", status: "offen",
      assigneeIds: ["u-jan"],
      description: "Persönliche Aufgabe ohne Projektbezug: Vertretung für die Woche ab 09.11. klären.",
      comments: [],
      history: [
        { type: "created", by: "u-jan", at: "2026-10-18 18:00" }
      ]
    }
  ],

  feedback: [
    { id: "f-1", kind: "kommentar", label: "Kommentar wartet auf Antwort", taskId: "t-101", fromId: "u-mara", at: "2026-10-20",
      text: "Sollen die Ersatzgeräte (5 %) direkt mitbestellt werden?" },
    { id: "f-2", kind: "freigabe", label: "Freigabe angefragt", taskId: "t-103", fromId: "u-lea", at: "2026-10-20",
      text: "Entwurf des Rollback-Plans liegt zur Freigabe vor." },
    { id: "f-3", kind: "erwaehnung", label: "Erwähnung", taskId: "t-201", fromId: "u-deniz", at: "2026-10-19",
      text: "Händler nennt jetzt Anfang Dezember – sollen wir eskalieren?" }
  ]
};
