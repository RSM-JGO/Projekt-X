/*
 * Projekt X – Konzeptskizze F19 v2 (Projekt-Bereiche im Hauptmenü)
 * BEISPIELDATEN, frei erfunden. Gelten für alle Beispielprojekte der Vorschau.
 * Grundlage: docs/fachliche-orientierung-projektablauf.md (Orientierung, keine harte Anforderung;
 * Sicht der Projektleitung, nicht des Rolloutmanagements).
 */
window.PX_JOURNEY_DATA = {
  // Abschnitte mit Meilensteinen M0–M5. release: granted | conditional | denied | open
  // deliverables: Lieferobjekte (Orientierung, keine harte Vorgabe)
  //   status: have = vorhanden, wip = in Arbeit, missing = fehlt; required = für Freigabe benötigt
  phases: [
    { label: "Auftragsklärung", milestone: "M0", milestoneLabel: "Start Projektauftrag", release: "granted",
      goal: "Klären, was das Projekt erreichen soll, wen es betrifft und wie kritisch es ist.",
      deliverables: [
        { name: "Projektsteckbrief", section: "steckbrief", status: "have", required: true },
        { name: "Stakeholderliste", section: "kommunikation", status: "have", required: true },
        { name: "Erste Einschätzung der Kritikalität", section: "steckbrief", status: "have", required: false }
      ] },
    { label: "Initiierung", milestone: "M1", milestoneLabel: "Projektfreigabe", release: "conditional",
      goal: "Auftrag, Verantwortlichkeiten und Risiken so weit klären, dass über die Projektfreigabe entschieden werden kann.",
      deliverables: [
        { name: "Projektauftrag (Ziele, Scope, Business Case, Toleranzen, Phasenplan)", section: "steckbrief", status: "have", required: true },
        { name: "RACI-Matrix", section: "kommunikation", status: "wip", required: true },
        { name: "Risikoliste mit Gefahren und Chancen", section: "risiken", status: "have", required: true },
        { name: "Kommunikationsplan", section: "kommunikation", status: "wip", required: false }
      ] },
    { label: "Vorbereitung", milestone: "M2", milestoneLabel: "Pilotfreigabe", release: "open",
      goal: "Produkt beschreiben, Abnahmekriterien vereinbaren und den Pilot vorbereiten.",
      deliverables: [
        { name: "Spezifikation / Produktbeschreibung", section: "produkt", status: "wip", required: true },
        { name: "Abnahmekriterien", section: "produkt", status: "missing", required: true },
        { name: "Pilotplan", section: "termine", status: "have", required: true },
        { name: "Risikoliste aktualisiert", section: "risiken", status: "have", required: false },
        { name: "Offene Punkte geklärt", section: "aenderungen", status: "wip", required: false },
        { name: "Statusbericht", section: "berichte", status: "have", required: false }
      ] },
    { label: "Pilot", milestone: "M3", milestoneLabel: "Skalierungsfreigabe", release: "open",
      goal: "Pilot durchführen, Ergebnisse bewerten und die Go-/No-Go-Entscheidung vorbereiten.",
      deliverables: [
        { name: "Pilotbericht", section: "produkt", status: "missing", required: true },
        { name: "Defektliste mit Maßnahmen", section: "produkt", status: "missing", required: true },
        { name: "Go-/No-Go-Entscheidung", section: "aenderungen", status: "missing", required: true }
      ] },
    { label: "Rollout", milestone: "M4", milestoneLabel: "Rolloutfreigabe", release: "open",
      goal: "Rollout übergreifend steuern: Ziele, Fortschritt, Risiken, Kosten und Änderungen im Blick behalten. Die operative Rolloutplanung liegt beim Rolloutmanagement.",
      deliverables: [
        { name: "Change- und Entscheidungslog aktuell", section: "aenderungen", status: "missing", required: true },
        { name: "Statusbericht", section: "berichte", status: "missing", required: true }
      ] },
    { label: "Abschluss", milestone: "M5", milestoneLabel: "Abschlussfreigabe", release: "open",
      goal: "Zielerreichung bewerten, Restpunkte übergeben und Erfahrungen festhalten.",
      deliverables: [
        { name: "Abschlussbericht", section: "abschluss", status: "missing", required: true },
        { name: "Lessons Learned", section: "abschluss", status: "missing", required: true }
      ] }
  ],
  currentPhase: 2,

  // Vorschlag je aktuellem Abschnitt; offene Auflagen früherer Freigaben haben Vorrang
  phaseSteps: [
    { section: "steckbrief",    title: "Projektsteckbrief vervollständigen",    text: "Zielbild, Umfang und Kritikalität für M0 Start Projektauftrag festhalten." },
    { section: "steckbrief",    title: "Projektauftrag vorbereiten",            text: "Ziele, Scope, Business Case und Toleranzen für M1 Projektfreigabe klären." },
    { section: "produkt",       title: "Abnahmekriterien abstimmen",            text: "Spezifikation und Abnahmekriterien für M2 Pilotfreigabe mit dem Fachbereich abstimmen." },
    { section: "produkt",       title: "Pilotbericht erstellen",                text: "Ergebnisse und Defektliste für M3 Skalierungsfreigabe zusammenfassen." },
    { section: "aenderungen",   title: "Änderungen und Abweichungen steuern",   text: "Change- und Entscheidungslog für M4 Rolloutfreigabe aktuell halten." },
    { section: "abschluss",     title: "Lessons Learned sammeln",               text: "Zielerreichung bewerten und Erkenntnisse für M5 Abschlussfreigabe dokumentieren." }
  ],

  // Unterpunkte im Hauptmenü. available = in Projekt X schon umgesetzt, sonst "geplant".
  // journey = Stand im Beispielprojekt: done | open | todo (null = ohne Stand)
  sections: [
    { key: "uebersicht",    label: "Übersicht",                     available: true,  availableNote: "Eckdaten und Mitglieder", journey: null },
    { key: "steckbrief",    label: "Steckbrief & Auftrag",          available: false, availableNote: "Name, Beschreibung und Zeitraum gibt es schon", journey: "done" },
    { key: "kommunikation", label: "Kommunikation",                 available: false, journey: "open" },
    { key: "termine",       label: "Termine & Zeitstrahl",          available: false, journey: "done" },
    { key: "aufgaben",      label: "Aufgaben",                      available: true,  availableNote: "Buckets, Mehrfachzuweisung, Verlauf", journey: "open" },
    { key: "risiken",       label: "Risiken & Chancen",             available: false, journey: "open" },
    { key: "aenderungen",   label: "Änderungen & Entscheidungen",   available: false, journey: "open" },
    { key: "produkt",       label: "Produkt & Pilot",               available: false, journey: "todo" },
    { key: "berichte",      label: "Berichte",                      available: false, journey: "done" },
    { key: "dokumente",     label: "Dokumente",                     available: false, journey: "todo" },
    { key: "abschluss",     label: "Abschluss & Lessons Learned",   available: false, journey: "todo" }
  ],

  charter: {
    vision: "Stabile, zentral verwaltete Netzwerktechnik in allen Beispielfilialen.",
    scope: "120 Beispielfilialen, Switches und Access Points, drei Rolloutwellen",
    criticality: { level: "mittel", reason: "Filialbetrieb betroffen, aber Umbau außerhalb der Öffnungszeiten möglich" }
  },

  mandate: {
    goals: ["Alle 120 Beispielfilialen umgestellt bis Februar 2027", "Keine Störung über 30 Minuten während der Öffnungszeiten"],
    inScope: "Austausch und Konfiguration der Netzwerktechnik, Pilot, Betriebsübergabe",
    outOfScope: "Kassensysteme, Gebäudeverkabelung, operative Rollout-Terminplanung",
    businessCase: "Weniger Störungen und geringere Wartungskosten; Investition 480.000 € (Beispiel)",
    roles: "Auftraggeber, Lenkungskreis, Projektleitung, Fachbereich, IT-Betrieb, Umsetzung (Beispiel)",
    tolerances: "Termin ± 2 Wochen, Kosten ± 5 %; darüber entscheidet der Auftraggeber",
    phasePlan: "M0 bis M5 laut Orientierungsleiste"
  },

  stakeholders: [
    { name: "Auftraggeberin (Beispiel)",       department: "Geschäftsführung", task: "Entscheidet über Freigaben und Budget",        influence: "hoch",    interest: "hoch" },
    { name: "Filialleitungen (Beispiel)",      department: "Vertrieb",         task: "Stellen Zugang und Ansprechpartner vor Ort",   influence: "niedrig", interest: "hoch" },
    { name: "Mitbestimmungsgremium (Beispiel)", department: "Personalvertretung", task: "Prüft Auswirkungen auf Mitarbeitende",     influence: "hoch",    interest: "niedrig" },
    { name: "IT-Betrieb (Beispiel)",           department: "Zentrale IT",      task: "Übernimmt den Betrieb nach dem Rollout",        influence: "hoch",    interest: "hoch" },
    { name: "Informationssicherheit (Beispiel)", department: "Zentrale IT",    task: "Gibt Sicherheitskonzept frei",                 influence: "hoch",    interest: "niedrig" },
    { name: "Kundenservice (Beispiel)",        department: "Service",          task: "Wird über Umstellungstermine informiert",      influence: "niedrig", interest: "niedrig" }
  ],

  communication: [
    { audience: "Lenkungskreis",       format: "Statusbericht mit Ampel",  frequency: "monatlich",       channel: "Sitzung, PDF",      owner: "Projektleitung" },
    { audience: "Projektteam",         format: "Abstimmungsrunde",         frequency: "wöchentlich",     channel: "Videokonferenz",    owner: "Projektleitung" },
    { audience: "Fachbereich",         format: "Abnahmetermin, Protokoll", frequency: "je Meilenstein",  channel: "Besprechung",       owner: "Fachbereich / PO" },
    { audience: "Filialleitungen",     format: "Information zur Umstellung", frequency: "2 Wochen vorher", channel: "E-Mail, Intranet", owner: "Umsetzung" }
  ],

  // RACI rollenbasiert (verallgemeinerte Rollen); Zellen können "A/R" enthalten
  raci: {
    roles: [
      { key: "pl",  label: "Projektleitung" },
      { key: "ag",  label: "Auftraggeber" },
      { key: "fb",  label: "Fachbereich / PO" },
      { key: "it",  label: "IT-Betrieb" },
      { key: "um",  label: "Umsetzung" }
    ],
    rows: [
      { activity: "Projektauftrag erstellen",                   cells: { pl: "A/R", ag: "C", fb: "C", it: "C", um: "C" } },
      { activity: "Projektfreigabe (M1) entscheiden",           cells: { pl: "R", ag: "A", fb: "C", it: "C", um: "I" } },
      { activity: "Spezifikation freigeben",                    cells: { pl: "A", ag: "I", fb: "R", it: "C", um: "C" } },
      { activity: "Pilot planen und abnehmen",                  cells: { pl: "A/R", ag: "I", fb: "R", it: "R", um: "C" } },
      { activity: "Go-/No-Go je Meilenstein",                   cells: { pl: "A/R", ag: "C", fb: "C", it: "C", um: "R" } },
      { activity: "Änderung außerhalb der Toleranz entscheiden", cells: { pl: "R", ag: "A", fb: "C", it: "C", um: "I" } },
      { activity: "Kommunikationsplan abstimmen",               cells: { pl: "R", ag: "I", fb: "C", it: "C", um: "C" } },
      { activity: "Betriebsübergabe",                           cells: { pl: "A", ag: "I", fb: "C", it: "R", um: "R" } },
      { activity: "Projektabschluss und Lessons Learned",       cells: { pl: "A/R", ag: "C", fb: "C", it: "C", um: "C" } }
    ]
  },

  // Meilensteine (Plan/Prognose/Ist); Freigabe aus phases
  milestones: [
    { key: "M0", plan: "2026-03-02", forecast: "2026-03-02", actual: "2026-03-02" },
    { key: "M1", plan: "2026-04-15", forecast: "2026-04-22", actual: "2026-04-22" },
    { key: "M2", plan: "2026-10-30", forecast: "2026-11-13", actual: null },
    { key: "M3", plan: "2026-12-11", forecast: "2026-12-18", actual: null },
    { key: "M4", plan: "2027-01-15", forecast: "2027-01-22", actual: null },
    { key: "M5", plan: "2027-02-26", forecast: "2027-02-26", actual: null }
  ],

  // Risiken und Chancen; Wahrscheinlichkeit/Auswirkung 1 = gering, 2 = mittel, 3 = hoch
  risks: [
    { id: "R1", type: "Gefahr", title: "Lieferverzug Netzwerktechnik", cause: "Engpass beim Hersteller", effect: "Pilot verschiebt sich", measure: "Zweitlieferant anfragen", owner: "Projektleitung", proximity: "kurzfristig", probability: 3, impact: 3, status: "in Bearbeitung" },
    { id: "R2", type: "Gefahr", title: "Abnahmekriterien unklar", cause: "Fachbereich noch nicht eingebunden", effect: "Pilotfreigabe verzögert", measure: "Abstimmungstermin ansetzen", owner: "Fachbereich / PO", proximity: "kurzfristig", probability: 2, impact: 2, status: "offen" },
    { id: "R3", type: "Gefahr", title: "Konfigurationsfehler", cause: "Viele manuelle Schritte", effect: "Störung in Filialen", measure: "Vier-Augen-Prinzip, Vorlage", owner: "IT-Betrieb", proximity: "mittelfristig", probability: 1, impact: 3, status: "beobachten" },
    { id: "R4", type: "Gefahr", title: "Neue Sicherheitsvorgaben", cause: "Überarbeitung der Richtlinie", effect: "Nacharbeit an der Konfiguration", measure: "Früh mit Informationssicherheit abstimmen", owner: "Projektleitung", proximity: "mittelfristig", probability: 3, impact: 2, status: "offen" },
    { id: "C1", type: "Chance", title: "Mengenrabatt bei Sammelbestellung", cause: "Rahmenvertrag läuft aus", effect: "Kosten sinken", measure: "Bestellung bündeln", owner: "Projektleitung", proximity: "kurzfristig", probability: 2, impact: 2, status: "offen" },
    { id: "C2", type: "Chance", title: "Wiederverwendbare Vorlagen", cause: "Pilot erzeugt Standardkonfiguration", effect: "Schnellerer Rollout", measure: "Vorlagen dokumentieren", owner: "IT-Betrieb", proximity: "mittelfristig", probability: 3, impact: 1, status: "offen" },
    { id: "R5", type: "Gefahr", title: "Budgetkürzung im Folgejahr", cause: "Planungsrunde offen", effect: "noch nicht bewertet", measure: "noch nicht festgelegt", owner: "Auftraggeber", proximity: "langfristig", probability: null, impact: null, status: "offen" }
  ],

  releases: [
    { milestone: "M0", decision: "Freigabe erteilt", date: "2026-03-02", participants: "Auftraggeberin, Projektleitung (Beispiel)", basis: "Projektsteckbrief v1", conditions: "keine", validity: "bis M1" },
    { milestone: "M1", decision: "Freigabe unter Auflagen", date: "2026-04-22", participants: "Lenkungskreis (Beispiel)", basis: "Projektauftrag v1.2, Risikoliste", conditions: "RACI bis M2 vervollständigen", validity: "bis M2" }
  ],

  changes: [
    { id: "Ä1", date: "2026-06-10", kind: "Änderung", subject: "Welle 3 um zwei Filialen erweitert", impact: "Kosten +1 % (innerhalb Toleranz)", status: "genehmigt" },
    { id: "E1", date: "2026-07-14", kind: "Entscheidung", subject: "Pilotstandorte festgelegt", impact: "keine", status: "dokumentiert" },
    { id: "Ä2", date: "2026-10-08", kind: "Änderung", subject: "M2 um zwei Wochen verschoben", impact: "Termin außerhalb Toleranz", status: "zur Entscheidung" }
  ],

  issues: [
    { id: "OP1", title: "Ansprechpartner IT-Betrieb für Pilot fehlt", owner: "Projektleitung", due: "2026-10-28" },
    { id: "OP2", title: "Zugang zu zwei Pilotfilialen klären", owner: "Fachbereich / PO", due: "2026-11-04" }
  ],

  placeholders: {
    produkt: ["Spezifikation / Produktbeschreibung (Beispiel)", "Abnahmekriterien mit Fachbereich", "Pilotbericht", "Defektliste mit Maßnahmen"],
    berichte: ["Statusbericht Oktober – veröffentlicht 14.10.2026, PDF (Beispiel)", "Veröffentlichte Stände bleiben unverändert"],
    dokumente: ["Projektauftrag v1.2 (Beispiel)", "Abnahmeprotokoll Pilot, Entwurf (Beispiel)"],
    abschluss: ["Zielerreichung, Scope, Business Case und Budget bewerten", "Lessons Learned und Rückführung in Vorlagen"]
  }
};
