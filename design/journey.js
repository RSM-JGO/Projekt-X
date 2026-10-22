/*
 * Projekt X – Konzeptskizze F19 v2: Projekt-Bereiche als Unterpunkte im Hauptmenü
 * KONZEPT, keine Festlegung. Orientierung an docs/fachliche-orientierung-projektablauf.md;
 * kein festes Phasenmodell (F12 offen). Bereiche außer Übersicht und Aufgaben sind "geplant".
 * Wird von app.js initialisiert: window.PX_JOURNEY(api).
 */
(function () {
  "use strict";

  var J = window.PX_JOURNEY_DATA;
  var DAY_MS = 86400000;

  window.PX_JOURNEY = function (api) {
    var esc = api.esc;
    var sectionsByKey = Object.create(null);
    J.sections.forEach(function (s) { sectionsByKey[s.key] = s; });
    var phaseByMs = Object.create(null);
    J.phases.forEach(function (ph, i) { ph.index = i; phaseByMs[ph.milestone] = ph; });
    // selectedMs: gewählter Meilenstein (Meilenstein-Seite), sonst der aktuelle Abschnitt
    var state = { subnavOpen: true, mobileOpen: false, selectedMs: J.phases[J.currentPhase].milestone };

    /* ---------------- Hilfen ---------------- */

    function toUtc(iso) {
      var p = String(iso).split("-");
      return Date.UTC(+p[0], +p[1] - 1, +p[2]);
    }

    function sectionUrl(p, key) {
      return "#/projekt/" + encodeURIComponent(p.id) + (key === "uebersicht" ? "" : "/" + key);
    }

    function availability(s) {
      if (s.available) {
        return '<span class="chip tone-sky" title="' + esc(s.availableNote || "") + '">vorhanden in Projekt X</span>';
      }
      return '<span class="chip chip--planned">geplant</span>';
    }

    var JOURNEY_STATUS = {
      done: { icon: "✓", label: "erledigt", tone: "mint" },
      open: { icon: "●", label: "offen", tone: "peach" },
      todo: { icon: "○", label: "nicht begonnen", tone: "neutral" }
    };

    // Freigabe-Ampel; Gelb aus der Vorlage wird als Orange dargestellt
    var RELEASE = {
      granted: { icon: "✓", label: "erteilt", tone: "mint" },
      conditional: { icon: "!", label: "unter Auflagen", tone: "peach" },
      denied: { icon: "✕", label: "keine Freigabe", tone: "rose" },
      open: { icon: "○", label: "offen", tone: "neutral" }
    };

    function marker(def, showText) {
      return '<span class="jstate"><span class="jstate__icon tone-' + def.tone + '" aria-hidden="true">' + def.icon + "</span>" +
        '<span class="' + (showText ? "jstate__text" : "sr-only") + '">' + esc(def.label) + "</span></span>";
    }

    function list(lines) {
      return '<ul class="j-lines">' + lines.map(function (l) { return "<li>" + esc(l) + "</li>"; }).join("") + "</ul>";
    }

    function table(caption, headers, rows, cards) {
      return '<div class="table-wrap j-tablewrap' + (cards ? " table-wrap--cards" : "") + '"><table class="table' + (cards ? " table--cards" : "") + '">' +
        '<caption class="sr-only">' + esc(caption) + "</caption><thead><tr>" +
        headers.map(function (h) { return '<th scope="col">' + esc(h) + "</th>"; }).join("") + "</tr></thead><tbody>" +
        rows.map(function (r) {
          return "<tr>" + r.map(function (c, i) {
            return '<td data-label="' + esc(headers[i]) + '"' + (i === 0 ? ' class="table__title"' : "") + ">" + c + "</td>";
          }).join("") + "</tr>";
        }).join("") + "</tbody></table></div>";
    }

    /* ---------------- Meilensteine und Lieferobjekte ---------------- */

    // Stand eines Lieferobjekts: Text und Symbol, Farbe nur am Symbol
    var DELIVERABLE = {
      have: { icon: "✓", label: "vorhanden", tone: "mint" },
      wip: { icon: "●", label: "in Arbeit", tone: "peach" },
      missing: { icon: "○", label: "fehlt", tone: "neutral" }
    };

    var DOC_ICON = '<svg class="doc-icon" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M4 1.5h5.5L13 5v9.5H4z M9.5 1.5V5H13" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>';

    function msUrl(p, ms) {
      return "#/projekt/" + encodeURIComponent(p.id) + "/m/" + ms;
    }

    function msTitle(ph) {
      return ph.milestone + " " + ph.milestoneLabel;
    }

    function milestoneDates(ms) {
      return J.milestones.filter(function (m) { return m.key === ms; })[0];
    }

    function releaseOf(ms) {
      return J.releases.filter(function (r) { return r.milestone === ms; })[0] || null;
    }

    function progress(ph) {
      var have = ph.deliverables.filter(function (d) { return d.status === "have"; }).length;
      return { have: have, total: ph.deliverables.length };
    }

    function openDeliverables(ph, sectionKey) {
      return ph.deliverables.filter(function (d) {
        return d.status !== "have" && (!sectionKey || d.section === sectionKey);
      });
    }

    function progressBar(ph) {
      var pr = progress(ph);
      var pct = pr.total ? Math.round((pr.have / pr.total) * 100) : 0;
      return '<div class="j-progress" role="img" aria-label="' + pr.have + " von " + pr.total + ' Lieferobjekten vorhanden">' +
        '<span class="j-progress__bar"><span class="j-progress__fill" style="width:' + pct + '%"></span></span>' +
        '<span class="j-progress__text">' + pr.have + " von " + pr.total + " Lieferobjekten</span></div>";
    }

    function requiredChip(d) {
      return d.required
        ? '<span class="chip tone-brand chip--doc">' + DOC_ICON + "Pflicht<span class=\"sr-only\">: für Freigabe benötigt</span></span>"
        : '<span class="chip chip--optional">optional</span>';
    }

    function nextSteps(p) {
      // Offene Auflagen früherer Freigaben zuerst, dann offene Pflicht-Lieferobjekte des aktuellen Abschnitts
      var steps = [];
      for (var i = 0; i < J.currentPhase; i++) {
        var ph = J.phases[i];
        if (ph.release === "conditional") {
          var rel = releaseOf(ph.milestone);
          steps.push({ title: "Auflage aus " + msTitle(ph) + " erfüllen", text: rel ? rel.conditions : "", href: msUrl(p, ph.milestone) });
        }
      }
      var cur = J.phases[J.currentPhase];
      var open = openDeliverables(cur).sort(function (a, b) { return (b.required ? 1 : 0) - (a.required ? 1 : 0); });
      open.forEach(function (d) {
        steps.push({ title: d.name + " (" + DELIVERABLE[d.status].label + ")", text: "für " + msTitle(cur), href: sectionUrl(p, d.section) });
      });
      J.changes.filter(function (c) { return c.status === "zur Entscheidung"; }).forEach(function (c) {
        steps.push({ title: "Entscheidung: " + c.subject, text: c.impact, href: sectionUrl(p, "aenderungen") });
      });
      return steps.slice(0, 3);
    }

    /* ---------------- Orientierungsleiste M0–M5 (anklickbar) ---------------- */

    function orientation(p, onMsPage) {
      var steps = J.phases.map(function (ph, i) {
        var cls = i < J.currentPhase ? " is-past" : (i === J.currentPhase ? " is-current" : "");
        if (ph.milestone === state.selectedMs) { cls += " is-selected"; }
        var rel = i < J.currentPhase ? RELEASE[ph.release] : RELEASE.open;
        var pr = progress(ph);
        var current = onMsPage && ph.milestone === state.selectedMs;
        return '<li><a class="j-orient__step' + cls + '" href="' + msUrl(p, ph.milestone) + '"' +
          (current ? ' aria-current="page"' : "") +
          ' title="' + esc(msTitle(ph) + ": Freigabe " + rel.label + ", " + pr.have + " von " + pr.total + " Lieferobjekten") + '">' +
          '<span class="j-orient__name">' + esc(ph.label) + (i === J.currentPhase ? '<span class="sr-only"> (aktueller Abschnitt)</span>' : "") + "</span>" +
          '<span class="j-orient__ms">' + marker(rel, false) + " " + esc(ph.milestone) +
          '<span class="j-orient__count">' + pr.have + "/" + pr.total + "</span></span></a></li>";
      }).join("");
      var sel = phaseByMs[state.selectedMs];
      return '<nav class="j-orient" aria-label="Abschnitte und Meilensteine">' +
        '<ol class="j-orient__list">' + steps + "</ol>" +
        '<p class="j-orient__compact"><a href="' + msUrl(p, sel.milestone) + '">Abschnitt ' + (sel.index + 1) + " von " + J.phases.length + ": <strong>" +
          esc(sel.label) + "</strong> · " + esc(msTitle(sel)) + "</a>" +
          (sel.index > 0 ? ' <a class="j-orient__nav" href="' + msUrl(p, J.phases[sel.index - 1].milestone) + '" aria-label="Voriger Meilenstein">‹</a>' : "") +
          (sel.index < J.phases.length - 1 ? ' <a class="j-orient__nav" href="' + msUrl(p, J.phases[sel.index + 1].milestone) + '" aria-label="Nächster Meilenstein">›</a>' : "") + "</p>" +
        '<p class="j-orient__hint">Orientierung – kein festes Phasenmodell. Freigabe-Ampel: ' +
          marker(RELEASE.granted, true) + " " + marker(RELEASE.conditional, true) + " " + marker(RELEASE.denied, true) + " " + marker(RELEASE.open, true) + "</p>" +
        "</nav>";
    }

    /* Hinweis oben auf Bereichsseiten: welche Lieferobjekte dieses Bereichs der gewählte Meilenstein braucht */
    function needsHint(p, key) {
      var ph = phaseByMs[state.selectedMs];
      var items = ph.deliverables.filter(function (d) { return d.section === key; });
      if (!items.length) { return ""; }
      return '<p class="j-needs"><span class="j-needs__label">Benötigt für <a href="' + msUrl(p, ph.milestone) + '">' + esc(msTitle(ph)) + "</a>:</span> " +
        items.map(function (d) { return esc(d.name) + " (" + DELIVERABLE[d.status].label + ")"; }).join(", ") + "</p>";
    }

    /* ---------------- Unterpunkte (Hauptmenü und mobiles Projektmenü) ---------------- */

    function sectionItems(p, current, idPrefix) {
      var ph = phaseByMs[state.selectedMs];
      return J.sections.map(function (s) {
        var st = JOURNEY_STATUS[s.journey];
        var active = s.key === current;
        var open = openDeliverables(ph, s.key).length;
        return '<li><a class="subnav__item' + (active ? " is-active" : "") + '" href="' + sectionUrl(p, s.key) + '"' +
          (active ? ' aria-current="page"' : "") + ' id="' + idPrefix + s.key + '">' +
          (st ? marker(st, false) : '<span class="jstate"><span class="jstate__icon jstate__icon--blank" aria-hidden="true"></span></span>') +
          '<span class="subnav__label">' + esc(s.label) +
          '<span class="subnav__meta">' + (st ? esc(st.label) + " · " : "") + (s.available ? "vorhanden" : "geplant") + "</span>" +
          (open ? '<span class="subnav__ms">' + esc(ph.milestone) + ": " + open + " offen</span>" : "") +
          "</span></a></li>";
      }).join("");
    }

    function renderSubnav(p, current) {
      if (!p) { return ""; }
      return '<div class="subnav">' +
        '<button type="button" class="subnav__project" data-action="journey-subnav" aria-expanded="' + state.subnavOpen + '" aria-controls="subnav-list">' +
          '<span class="subnav__project-name">' + esc(p.name) + '</span><span aria-hidden="true">' + (state.subnavOpen ? "▾" : "▸") + "</span></button>" +
        '<p class="subnav__context">Bezug: <a href="' + msUrl(p, state.selectedMs) + '">' + esc(msTitle(phaseByMs[state.selectedMs])) + "</a></p>" +
        '<ul class="subnav__list" id="subnav-list"' + (state.subnavOpen ? "" : " hidden") + ">" + sectionItems(p, current, "nav-") + "</ul></div>";
    }

    function mobileMenu(p, current) {
      var label = current === "meilenstein" ? msTitle(phaseByMs[state.selectedMs]) : sectionsByKey[current].label;
      return '<div class="j-mobilemenu">' +
        '<button type="button" class="btn j-mobilemenu__toggle" data-action="journey-mobilemenu" aria-expanded="' + state.mobileOpen + '" aria-controls="j-mobile-list">' +
          "Projektmenü: " + esc(label) + ' <span aria-hidden="true">' + (state.mobileOpen ? "▲" : "▼") + "</span></button>" +
        '<ul class="subnav__list j-mobilemenu__list" id="j-mobile-list"' + (state.mobileOpen ? "" : " hidden") + ">" + sectionItems(p, current, "mob-") + "</ul></div>";
    }

    /* ---------------- Meilenstein-Seite ---------------- */

    function renderMilestone(p) {
      var ph = phaseByMs[state.selectedMs];
      var dates = milestoneDates(ph.milestone);
      var rel = releaseOf(ph.milestone);
      var relDef = ph.index < J.currentPhase ? RELEASE[ph.release] : RELEASE.open;
      var rows = ph.deliverables.map(function (d) {
        return "<li class=\"deliv\">" + marker(DELIVERABLE[d.status], true) +
          '<span class="deliv__name">' + esc(d.name) + "</span>" + requiredChip(d) +
          '<a class="deliv__link" href="' + sectionUrl(p, d.section) + '">' + esc(sectionsByKey[d.section].label) + "</a></li>";
      }).join("");
      function field(label, value) {
        return "<div><dt>" + esc(label) + "</dt><dd>" + (value ? esc(value) : '<span class="muted">noch nicht entschieden</span>') + "</dd></div>";
      }
      var prev = ph.index > 0 ? J.phases[ph.index - 1] : null;
      var next = ph.index < J.phases.length - 1 ? J.phases[ph.index + 1] : null;
      return '<p class="j-goal">' + esc(ph.goal) + "</p>" +
        '<div class="j-grid j-grid--ms">' +
          '<section class="card" aria-labelledby="dl-title"><div class="card__head"><h3 id="dl-title">Lieferobjekte</h3>' + progressBar(ph) + "</div>" +
            '<ul class="deliv-list">' + rows + "</ul>" +
            '<p class="card__hint j-hint">Orientierung, keine harte Vorgabe. „Pflicht“ kennzeichnet, was für die Freigabe benötigt wird.</p></section>' +
          '<section class="card" aria-labelledby="fg-title"><div class="card__head"><h3 id="fg-title">Freigabe</h3>' + marker(relDef, true) + "</div>" +
            '<dl class="facts j-facts j-facts--wide">' +
              field("Entscheidung", rel && rel.decision) + field("Datum", rel && api.fmtDate(rel.date)) +
              field("Beteiligte", rel && rel.participants) + field("Grundlage", rel && rel.basis) +
              field("Auflagen", rel && rel.conditions) + field("Gültigkeit", rel && rel.validity) +
            "</dl></section>" +
        "</div>" +
        '<p class="j-msdates muted">Termin: Plan ' + esc(api.fmtDate(dates.plan)) +
          (dates.actual ? " · Ist " + esc(api.fmtDate(dates.actual)) : " · Prognose " + esc(api.fmtDate(dates.forecast))) + "</p>" +
        '<nav class="j-pager" aria-label="Meilensteine blättern">' +
          (prev ? '<a class="btn" href="' + msUrl(p, prev.milestone) + '">‹ ' + esc(msTitle(prev)) + "</a>" : "<span></span>") +
          (next ? '<a class="btn" href="' + msUrl(p, next.milestone) + '">' + esc(msTitle(next)) + " ›</a>" : "<span></span>") +
        "</nav>";
    }

    /* ---------------- Bereiche ---------------- */

    function renderOverview(p) {
      var cur = J.phases[J.currentPhase];
      var dates = milestoneDates(cur.milestone);
      var steps = nextSteps(p);
      var today = toUtc(api.today());

      var upcoming = J.milestones.filter(function (m) { return !m.actual && toUtc(m.forecast) >= today; }).slice(0, 2);
      var risks = J.risks.filter(function (r) { return r.type === "Gefahr" && r.probability !== null && r.impact !== null; })
        .sort(function (a, b) { return b.probability * b.impact - a.probability * a.impact; }).slice(0, 3);
      var decisions = J.changes.filter(function (c) { return c.status === "zur Entscheidung"; });
      var tasks = api.taskStats(p);

      function kpi(title, body, href, linkText) {
        return '<section class="card j-kpi"><h3>' + esc(title) + "</h3>" + body +
          '<a class="j-kpi__link" href="' + href + '">' + esc(linkText) + "</a></section>";
      }

      var kpis =
        kpi("Nächste Termine", '<ul class="j-kpi__list">' + upcoming.map(function (m) {
          return "<li><strong>" + esc(m.key) + "</strong> " + esc(phaseByMs[m.key].milestoneLabel) + '<span class="muted"> · ' + esc(api.fmtDate(m.forecast)) + "</span></li>";
        }).join("") + "</ul>", sectionUrl(p, "termine"), "Termine & Zeitstrahl") +
        kpi("Top-Risiken", '<ul class="j-kpi__list">' + risks.map(function (r) {
          return "<li>" + marker({ icon: "●", label: LEVEL[r.probability] + "/" + LEVEL[r.impact], tone: riskTone(r.probability, r.impact) }, false) + " " + esc(r.title) + "</li>";
        }).join("") + "</ul>", sectionUrl(p, "risiken"), "Risiken & Chancen") +
        kpi("Offene Entscheidungen", '<p class="j-kpi__value">' + decisions.length + "</p>" +
          '<ul class="j-kpi__list">' + decisions.map(function (c) { return "<li>" + esc(c.subject) + "</li>"; }).join("") + "</ul>",
          sectionUrl(p, "aenderungen"), "Änderungen & Entscheidungen") +
        kpi("Aufgaben", '<p class="j-kpi__value">' + tasks.open + '<span class="j-kpi__unit"> offen</span></p>' +
          '<p class="j-kpi__sub">' + tasks.inProgress + " in Arbeit · " +
          (tasks.overdue ? marker({ icon: "!", label: tasks.overdue + " überfällig", tone: "rose" }, true) : "keine überfällig") + "</p>",
          sectionUrl(p, "aufgaben"), "Zum Board");

      return '<div class="j-grid j-grid--2 j-grid--top">' +
          '<section class="card j-phase" aria-labelledby="ph-title"><p class="j-next__label">Aktueller Abschnitt</p>' +
            '<h3 id="ph-title">' + esc((cur.index + 1) + ". " + cur.label) + "</h3>" +
            '<p class="muted">Nächster Meilenstein <strong>' + esc(msTitle(cur)) + "</strong> · Prognose " + esc(api.fmtDate(dates.forecast)) + "</p>" +
            progressBar(cur) +
            '<a class="btn btn--small" href="' + msUrl(p, cur.milestone) + '">Lieferobjekte für ' + esc(cur.milestone) + "</a></section>" +
          '<section class="card j-next" aria-labelledby="ns-title"><p class="j-next__label">Vorschlag, keine Pflicht</p><h3 id="ns-title">Nächste Schritte</h3>' +
            '<ol class="j-steps">' + steps.map(function (s) {
              return '<li><a href="' + s.href + '">' + esc(s.title) + "</a>" + (s.text ? '<span class="muted"> – ' + esc(s.text) + "</span>" : "") + "</li>";
            }).join("") + "</ol></section>" +
        "</div>" +
        '<div class="j-grid j-grid--4">' + kpis + "</div>";
    }

    function renderCharter(p) {
      var c = J.charter;
      var m = J.mandate;
      return '<div class="j-grid j-grid--2">' +
        '<section class="card" aria-labelledby="sb-title"><h3 id="sb-title" class="j-sub">Projektsteckbrief</h3><dl class="facts j-facts">' +
          "<div><dt>Zielbild</dt><dd>" + esc(c.vision) + "</dd></div>" +
          "<div><dt>Umfang</dt><dd>" + esc(c.scope) + "</dd></div>" +
          "<div><dt>Zeitraum</dt><dd>" + esc(api.fmtDate(p.start)) + " – " + esc(api.fmtDate(p.end)) + "</dd></div>" +
          "<div><dt>Kritikalität</dt><dd>" + esc(c.criticality.level) + '<span class="table__sub">' + esc(c.criticality.reason) + "</span></dd></div>" +
        '</dl><p class="card__hint j-hint">In Projekt X gibt es heute Name, Beschreibung und Zeitraum.</p></section>' +
        '<section class="card" aria-labelledby="pa-title"><h3 id="pa-title" class="j-sub">Projektauftrag</h3><dl class="facts j-facts j-facts--wide">' +
          "<div><dt>Ziele</dt><dd>" + list(m.goals) + "</dd></div>" +
          "<div><dt>Scope</dt><dd>" + esc(m.inScope) + "</dd></div>" +
          "<div><dt>Out of Scope</dt><dd>" + esc(m.outOfScope) + "</dd></div>" +
          "<div><dt>Business Case</dt><dd>" + esc(m.businessCase) + "</dd></div>" +
          "<div><dt>Rollen</dt><dd>" + esc(m.roles) + "</dd></div>" +
          "<div><dt>Toleranzen</dt><dd>" + esc(m.tolerances) + "</dd></div>" +
          "<div><dt>Phasenplan</dt><dd>" + esc(m.phasePlan) + "</dd></div>" +
        "</dl></section></div>";
    }

    var QUADRANTS = [
      { influence: "hoch", interest: "niedrig", label: "Zufriedenstellen" },
      { influence: "hoch", interest: "hoch", label: "Eng einbinden" },
      { influence: "niedrig", interest: "niedrig", label: "Beobachten" },
      { influence: "niedrig", interest: "hoch", label: "Informieren" }
    ];

    function countA(row) {
      var n = 0;
      for (var k in row.cells) { if (String(row.cells[k]).indexOf("A") !== -1) { n++; } }
      return n;
    }

    function raciTable() {
      var roles = J.raci.roles;
      var head = '<tr><th scope="col">Aktivität</th>' + roles.map(function (r) { return '<th scope="col">' + esc(r.label) + "</th>"; }).join("") +
        '<th scope="col">Prüfung</th></tr>';
      var body = J.raci.rows.map(function (row) {
        var a = countA(row);
        var check = a === 1 ? marker({ icon: "✓", label: "genau ein A", tone: "mint" }, true)
          : marker({ icon: "!", label: a === 0 ? "kein A" : a + "× A", tone: "peach" }, true);
        return '<tr><th scope="row">' + esc(row.activity) + "</th>" + roles.map(function (r) {
          var v = row.cells[r.key] || "";
          var parts = v ? v.split("/") : [];
          return '<td class="raci-cell">' + (parts.length
            ? parts.map(function (x) { return '<span class="raci raci--' + x + '" title="' + raciLabel(x) + '">' + x + "</span>"; }).join("")
            : '<span class="muted">–</span>') + "</td>";
        }).join("") + "<td>" + check + "</td></tr>";
      }).join("");
      return '<div class="table-wrap j-tablewrap"><table class="table raci-table"><caption class="sr-only">RACI-Matrix nach Projektrollen (Beispiel)</caption>' +
        "<thead>" + head + "</thead><tbody>" + body + "</tbody></table></div>" +
        '<p class="raci-legend"><span class="raci raci--R">R</span> führt aus <span class="raci raci--A">A</span> trägt die Gesamtverantwortung ' +
        '<span class="raci raci--C">C</span> wird konsultiert <span class="raci raci--I">I</span> wird informiert</p>';
    }

    function raciLabel(v) {
      return { R: "führt aus", A: "trägt die Gesamtverantwortung", C: "wird konsultiert", I: "wird informiert" }[v] || v;
    }

    function renderCommunication() {
      var cells = QUADRANTS.map(function (q) {
        var names = J.stakeholders.filter(function (s) { return s.influence === q.influence && s.interest === q.interest; });
        return '<div class="sh-cell"><p class="sh-cell__title">' + esc(q.label) + "</p>" +
          '<p class="sh-cell__axis muted">Einfluss ' + q.influence + " · Interesse " + q.interest + "</p>" +
          "<ul>" + names.map(function (s) { return "<li>" + esc(s.name) + "</li>"; }).join("") + "</ul></div>";
      }).join("");
      var shRows = J.stakeholders.map(function (s) {
        return [esc(s.name), esc(s.department), esc(s.task), esc(s.influence), esc(s.interest)];
      });
      var commRows = J.communication.map(function (c) {
        return [esc(c.audience), esc(c.format), esc(c.frequency), esc(c.channel), esc(c.owner)];
      });
      return '<p class="note">Stakeholder sind <strong>keine Benutzerkonten</strong> und erhalten keinen Zugriff. Alle Werte sind Beispielwerte und je Projekt pflegbar.</p>' +
        '<div class="j-grid j-grid--2">' +
          '<section class="card" aria-labelledby="shm-title"><h3 id="shm-title" class="j-sub">Stakeholdermatrix</h3>' +
            '<div class="sh-matrix" role="group" aria-label="Einfluss-Interesse-Matrix">' +
              '<span class="sh-matrix__y" aria-hidden="true">Einfluss ↑</span>' + cells +
              '<span class="sh-matrix__x" aria-hidden="true">Interesse →</span></div></section>' +
          '<section class="card" aria-labelledby="shl-title"><h3 id="shl-title" class="j-sub">Stakeholderliste</h3>' +
            table("Stakeholderliste (Beispiel)", ["Name", "Abteilung", "Aufgabe im Projekt", "Einfluss", "Interesse"], shRows, true) + "</section>" +
        "</div>" +
        '<section class="card j-block" aria-labelledby="km-title"><h3 id="km-title" class="j-sub">Kommunikationsmatrix</h3>' +
          table("Kommunikationsmatrix (Beispiel)", ["Zielgruppe", "Format", "Häufigkeit", "Kanal", "Verantwortlich"], commRows, true) + "</section>" +
        '<section class="card j-block" aria-labelledby="raci-title"><div class="card__head"><h3 id="raci-title">RACI nach Projektrollen</h3>' +
          '<span class="card__hint">Prüfregel: genau ein A je Zeile</span></div>' +
          '<p class="note">Beispielrollen und -werte, je Projekt pflegbar. Sie werden durch die Rollen aus dem Handbuch des Benutzers ersetzt.</p>' +
          raciTable() + "</section>";
    }

    function renderSchedule() {
      var phasesByMs = Object.create(null);
      J.phases.forEach(function (ph) { phasesByMs[ph.milestone] = ph; });
      var rows = J.milestones.map(function (m) {
        var ph = phasesByMs[m.key];
        var dev = Math.round((toUtc(m.actual || m.forecast) - toUtc(m.plan)) / DAY_MS);
        return [esc(m.key + " " + ph.milestoneLabel), esc(api.fmtDate(m.plan)),
          m.actual ? '<span class="muted">–</span>' : esc(api.fmtDate(m.forecast)),
          m.actual ? esc(api.fmtDate(m.actual)) : '<span class="muted">offen</span>',
          dev === 0 ? "±0 Tage" : (dev > 0 ? "+" : "") + dev + " Tage",
          marker(RELEASE[ph.release], true)];
      });
      var first = toUtc(J.milestones[0].plan);
      var last = toUtc(J.milestones[J.milestones.length - 1].plan);
      var span = last - first || 1;
      function pos(iso) { return Math.max(0, Math.min(100, ((toUtc(iso) - first) / span) * 100)).toFixed(1); }
      var points = J.milestones.map(function (m) {
        var ph = phasesByMs[m.key];
        var rel = RELEASE[ph.release];
        return '<li class="tl__point tone-' + rel.tone + '" style="left:' + pos(m.actual || m.forecast) + '%" title="' +
          esc(m.key + " " + ph.milestoneLabel + ": " + api.fmtDate(m.actual || m.forecast) + (m.actual ? " (Ist)" : " (Prognose)")) + '">' +
          '<span class="tl__label">' + esc(m.key) + "</span></li>";
      }).join("");
      var today = api.today();
      return '<section class="card" aria-labelledby="tl-title"><h3 id="tl-title" class="j-sub">Zeitstrahl</h3>' +
          '<div class="tl" role="img" aria-label="Zeitstrahl der Meilensteine M0 bis M5 mit Markierung für heute">' +
            '<div class="tl__bar"></div><ol class="tl__points">' + points + "</ol>" +
            '<span class="tl__today" style="left:' + pos(today) + '%"><span>heute</span></span>' +
          "</div>" +
          '<p class="tl__range muted"><span>' + esc(api.fmtDate(J.milestones[0].plan)) + "</span><span>" +
            esc(api.fmtDate(J.milestones[J.milestones.length - 1].plan)) + "</span></p></section>" +
        '<section class="card j-block" aria-labelledby="ms-title2"><h3 id="ms-title2" class="j-sub">Meilensteine</h3>' +
          table("Meilensteine mit Plan, Prognose, Ist und Freigabe (Beispiel)", ["Meilenstein", "Plan", "Prognose", "Ist", "Abweichung", "Freigabe"], rows, true) +
          '<p class="card__hint j-hint">Ursprünglicher und genehmigter Plan bleiben in Projekt X historisiert (hier vereinfacht).</p></section>';
    }

    var LEVEL = ["", "gering", "mittel", "hoch"];

    function riskTone(p, i) {
      var score = p * i;
      return score <= 2 ? "mint" : (score <= 4 ? "peach" : "rose");
    }

    function renderRisks() {
      var rated = J.risks.filter(function (r) { return r.probability !== null && r.impact !== null; });
      var unrated = J.risks.filter(function (r) { return r.probability === null || r.impact === null; });
      var rows = J.risks.map(function (r) {
        var bewertet = r.probability !== null && r.impact !== null;
        var typ = r.type === "Chance"
          ? '<span class="risk-kind risk-kind--chance"><span aria-hidden="true">◆</span> Chance</span>'
          : '<span class="risk-kind"><span aria-hidden="true">▲</span> Gefahr</span>';
        var level = !bewertet
          ? marker({ icon: "?", label: "nicht bewertet", tone: "neutral" }, true)
          : (r.type === "Chance" ? esc(LEVEL[r.probability] + " / " + LEVEL[r.impact])
            : marker({ icon: "●", label: LEVEL[r.probability] + " / " + LEVEL[r.impact], tone: riskTone(r.probability, r.impact) }, true));
        return [esc(r.id + " · " + r.title), typ, esc(r.cause), esc(r.effect), level, esc(r.proximity), esc(r.measure), esc(r.owner), esc(r.status)];
      });
      var grid = "";
      for (var p = 3; p >= 1; p--) {
        grid += '<span class="rm-axis rm-axis--y">' + LEVEL[p] + "</span>";
        for (var i = 1; i <= 3; i++) {
          var inCell = rated.filter(function (r) { return r.probability === p && r.impact === i; });
          var tone = riskTone(p, i);
          var items = inCell.map(function (r) {
            return r.type === "Chance"
              ? '<span class="rm-item rm-item--chance" title="Chance ' + esc(r.id + ": " + r.title) + '"><span aria-hidden="true">◆</span>' + esc(r.id) + "</span>"
              : '<span class="rm-item" title="Gefahr ' + esc(r.id + ": " + r.title) + '"><span aria-hidden="true">▲</span>' + esc(r.id) + "</span>";
          }).join("");
          grid += '<div class="rm-cell tone-' + tone + '">' + items +
            '<span class="sr-only">Wahrscheinlichkeit ' + LEVEL[p] + ", Auswirkung " + LEVEL[i] + ": " +
            (inCell.length ? inCell.map(function (r) { return r.type + " " + r.id; }).join(", ") : "keine Einträge") + "</span></div>";
        }
      }
      grid += '<span class="rm-corner" aria-hidden="true"></span>';
      for (var x = 1; x <= 3; x++) { grid += '<span class="rm-axis rm-axis--x">' + LEVEL[x] + "</span>"; }
      return '<div class="j-grid j-grid--matrix">' +
        '<section class="card" aria-labelledby="rm-title"><h3 id="rm-title" class="j-sub">Matrix 3×3</h3>' +
          '<div class="rm rm--3" role="group" aria-label="Risiko-Matrix: Zeilen Wahrscheinlichkeit, Spalten Auswirkung">' + grid + "</div>" +
          '<p class="card__hint">Zeilen: Wahrscheinlichkeit, Spalten: Auswirkung. Feldfarbe gilt für Gefahren: Grün gering, Orange mittel, Rot hoch. ' +
          "Chancen ◆ werden nicht rot bewertet.</p>" +
          '<div class="rm-unrated"><p>' + marker({ icon: "?", label: "Nicht bewertet (" + unrated.length + ")", tone: "neutral" }, true) +
          " – fehlende Bewertung ist nie grün:</p><ul>" +
          unrated.map(function (r) { return "<li>" + esc(r.id + " · " + r.title) + "</li>"; }).join("") + "</ul></div></section>" +
        '<section class="card" aria-labelledby="rl-title"><h3 id="rl-title" class="j-sub">Liste</h3>' +
          table("Risiken und Chancen (Beispiel)", ["Eintrag", "Typ", "Ursache", "Auswirkung", "Bewertung (W/A)", "Zeitliche Nähe", "Maßnahme", "Verantwortlich", "Status"], rows, true) +
        "</section></div>";
    }

    function renderChanges() {
      var releases = J.phases.map(function (ph) {
        var r = J.releases.filter(function (x) { return x.milestone === ph.milestone; })[0];
        return [esc(ph.milestone + " " + ph.milestoneLabel), marker(RELEASE[ph.release], true),
          r ? esc(r.decision) : '<span class="muted">–</span>', r ? esc(api.fmtDate(r.date)) : "–",
          r ? esc(r.participants) : "–", r ? esc(r.basis) : "–", r ? esc(r.conditions) : "–", r ? esc(r.validity) : "–"];
      });
      var changes = J.changes.map(function (c) {
        return [esc(c.id + " · " + c.subject), esc(c.kind), esc(api.fmtDate(c.date)), esc(c.impact), esc(c.status)];
      });
      var issues = J.issues.map(function (i) { return [esc(i.id + " · " + i.title), esc(i.owner), esc(api.fmtDate(i.due))]; });
      return '<section class="card" aria-labelledby="rel-title"><h3 id="rel-title" class="j-sub">Freigaben je Meilenstein</h3>' +
          table("Freigaben mit Ampel (Beispiel)", ["Meilenstein", "Ampel", "Entscheidung", "Datum", "Beteiligte", "Grundlage", "Auflagen", "Gültigkeit"], releases, true) +
        "</section>" +
        '<div class="j-grid j-grid--2 j-block">' +
          '<section class="card" aria-labelledby="chg-title"><h3 id="chg-title" class="j-sub">Change- und Entscheidungslog</h3>' +
            table("Änderungen und Entscheidungen (Beispiel)", ["Eintrag", "Art", "Datum", "Auswirkung", "Status"], changes, true) + "</section>" +
          '<section class="card" aria-labelledby="iss-title"><h3 id="iss-title" class="j-sub">Offene Punkte</h3>' +
            table("Offene Punkte (Beispiel)", ["Punkt", "Verantwortlich", "Fällig"], issues, true) + "</section>" +
        "</div>";
    }

    function placeholder(key) {
      return '<div class="card j-placeholder"><p class="card__hint">Platzhalter – Inhalt folgt mit dem Bereich:</p>' + list(J.placeholders[key]) + "</div>";
    }

    function content(key, p) {
      if (key === "uebersicht") { return renderOverview(p); }
      if (key === "steckbrief") { return renderCharter(p); }
      if (key === "kommunikation") { return renderCommunication(); }
      if (key === "termine") { return renderSchedule(); }
      if (key === "aufgaben") { return api.taskBoard(p); }
      if (key === "risiken") { return renderRisks(); }
      if (key === "aenderungen") { return renderChanges(); }
      return placeholder(key);
    }

    /* ---------------- Öffentliche Funktionen ---------------- */

    function normalize(section) {
      return section === "meilenstein" || sectionsByKey[section] ? section : "uebersicht";
    }

    function normalizeMs(ms) {
      return phaseByMs[ms] ? ms : null;
    }

    function band() {
      return '<p class="j-band" role="note">Konzeptskizze F19 v3 – Entscheidung offen</p>';
    }

    function render(p, section, ms) {
      var key = normalize(section);
      if (key === "meilenstein" && normalizeMs(ms)) { state.selectedMs = ms; }
      if (key === "meilenstein") {
        var ph = phaseByMs[state.selectedMs];
        return orientation(p, true) + mobileMenu(p, key) +
          '<section class="j-panel" aria-labelledby="j-title">' +
            '<div class="card__head j-head"><h2 id="j-title" tabindex="-1">' + esc(msTitle(ph)) + "</h2>" +
            '<span class="j-head__meta"><span class="muted">Abschnitt ' + (ph.index + 1) + " · " + esc(ph.label) + "</span></span></div>" +
            renderMilestone(p) +
          "</section>";
      }
      var s = sectionsByKey[key];
      var st = JOURNEY_STATUS[s.journey];
      return orientation(p, false) + mobileMenu(p, key) +
        '<section class="j-panel" aria-labelledby="j-title">' +
          '<div class="card__head j-head"><h2 id="j-title" tabindex="-1">' + esc(s.label) + "</h2>" +
          '<span class="j-head__meta">' + availability(s) + (st ? " " + marker(st, true) : "") + "</span></div>" +
          needsHint(p, key) +
          content(key, p) +
        "</section>";
    }

    function sectionLabel(section, ms) {
      var key = normalize(section);
      if (key === "meilenstein") { return msTitle(phaseByMs[normalizeMs(ms) || state.selectedMs]); }
      return sectionsByKey[key].label;
    }

    function handleAction(action) {
      if (action === "journey-subnav") {
        state.subnavOpen = !state.subnavOpen;
        return '[data-action="journey-subnav"]';
      }
      if (action === "journey-mobilemenu") {
        state.mobileOpen = !state.mobileOpen;
        return '[data-action="journey-mobilemenu"]';
      }
      return null;
    }

    function closeMobile() { state.mobileOpen = false; }

    return {
      band: band,
      render: render,
      renderSubnav: renderSubnav,
      sectionLabel: sectionLabel,
      normalize: normalize,
      handleAction: handleAction,
      closeMobile: closeMobile
    };
  };
})();
