/*
 * Projekt X – Designvorschau
 * Reine Oberflächensimulation ohne Backend. Rechte, Speicherung und
 * Benachrichtigungen werden hier NICHT umgesetzt. Zustand liegt im Speicher
 * und – falls verfügbar – im localStorage dieses Browsers.
 */
(function () {
  "use strict";

  var DATA = window.PX_DATA;
  var TASK_STORE_KEY = "px-design-tasks-v2";
  var THEME_KEY = "px-design-theme";
  var DAY_MS = 86400000;

  /* ---------------- Speicherzugriff (immer abgesichert) ---------------- */

  function storageGet(key) {
    try { return window.localStorage.getItem(key); } catch (e) { return null; }
  }
  function storageSet(key, value) {
    try { window.localStorage.setItem(key, value); return true; } catch (e) { return false; }
  }
  function storageRemove(key) {
    try { window.localStorage.removeItem(key); } catch (e) { /* ohne Speicher weiter */ }
  }

  /* ---------------- Zustand ---------------- */

  function normalizeTask(t) {
    if (!t.priority) { t.priority = "mittel"; }
    if (typeof t.description !== "string") { t.description = ""; }
    return t;
  }

  function cloneTasks() {
    return JSON.parse(JSON.stringify(DATA.tasks)).map(normalizeTask);
  }

  // Gespeicherter Stand (inkl. neu angelegter und gelöschter Aufgaben); bei ungültigen Daten Ausgangszustand
  function loadTasks() {
    var raw = storageGet(TASK_STORE_KEY);
    if (!raw) { return cloneTasks(); }
    try {
      var stored = JSON.parse(raw);
      if (!Array.isArray(stored)) { return cloneTasks(); }
      var valid = stored.every(function (t) {
        return t && typeof t.id === "string" && typeof t.title === "string" &&
          Array.isArray(t.assigneeIds) && Array.isArray(t.history) && Array.isArray(t.comments) &&
          (t.projectId === null || typeof t.projectId === "string") &&
          (t.status === "offen" || t.status === "in-arbeit" || t.status === "erledigt");
      });
      return valid ? stored.map(normalizeTask) : cloneTasks();
    } catch (e) {
      return cloneTasks();
    }
  }

  function defaultKanban() {
    return { view: "board", sort: "asc", q: "", bucket: "", person: "", milestone: "", priority: "", mine: false };
  }

  var state = {
    tasks: loadTasks(),
    kanban: defaultKanban(),
    openTaskId: null,
    lastRouteKey: null
  };

  function saveTasks() {
    storageSet(TASK_STORE_KEY, JSON.stringify(state.tasks));
  }

  /* ---------------- Nachschlagen ---------------- */

  var usersById = Object.create(null);
  DATA.users.forEach(function (u) { usersById[u.id] = u; });
  var projectsById = Object.create(null);
  DATA.projects.forEach(function (p) { projectsById[p.id] = p; });

  var me = usersById[DATA.meta.currentUserId];

  function getTask(id) {
    for (var i = 0; i < state.tasks.length; i++) {
      if (state.tasks[i].id === id) { return state.tasks[i]; }
    }
    return null;
  }
  function getMilestone(project, id) {
    if (!project || !id) { return null; }
    for (var i = 0; i < project.milestones.length; i++) {
      if (project.milestones[i].id === id) { return project.milestones[i]; }
    }
    return null;
  }
  function getBucket(project, id) {
    if (!project || !id) { return null; }
    for (var i = 0; i < project.buckets.length; i++) {
      if (project.buckets[i].id === id) { return project.buckets[i]; }
    }
    return null;
  }
  function userName(id) {
    return usersById[id] ? usersById[id].name : "Unbekannt";
  }

  /* ---------------- Datum ---------------- */

  var WEEKDAYS = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];

  function toUtc(iso) {
    var p = String(iso).slice(0, 10).split("-");
    return Date.UTC(+p[0], +p[1] - 1, +p[2]);
  }
  var TODAY = toUtc(DATA.meta.today);

  function daysFromTo(aIso, bIso) {
    return Math.round((toUtc(bIso) - toUtc(aIso)) / DAY_MS);
  }
  function daysFromToday(iso) {
    return Math.round((toUtc(iso) - TODAY) / DAY_MS);
  }
  function pad(n) { return n < 10 ? "0" + n : String(n); }
  function fmtDate(iso) {
    if (!iso) { return "–"; }
    var p = String(iso).slice(0, 10).split("-");
    return p[2] + "." + p[1] + "." + p[0];
  }
  function fmtDateTime(value) {
    if (!value) { return "–"; }
    var parts = String(value).split(" ");
    return fmtDate(parts[0]) + (parts[1] ? ", " + parts[1] + " Uhr" : "");
  }
  function weekdayOf(iso) {
    return WEEKDAYS[new Date(toUtc(iso)).getUTCDay()];
  }
  function endOfWeekIso() {
    var d = new Date(TODAY);
    var dow = d.getUTCDay();               // 0 = Sonntag
    var add = dow === 0 ? 0 : 7 - dow;
    var end = new Date(TODAY + add * DAY_MS);
    return end.getUTCFullYear() + "-" + pad(end.getUTCMonth() + 1) + "-" + pad(end.getUTCDate());
  }
  function plural(n, one, many) { return n === 1 ? one : many; }

  function dueInfo(task) {
    var diff = daysFromToday(task.due);
    if (task.status === "erledigt") {
      return { cls: "", text: "Fällig war " + fmtDate(task.due) };
    }
    if (diff < 0) {
      var n = -diff;
      return { cls: "due--overdue", text: "Überfällig seit " + n + " " + plural(n, "Tag", "Tagen") + " (" + fmtDate(task.due) + ")" };
    }
    if (diff === 0) { return { cls: "due--today", text: "Heute fällig" }; }
    if (diff === 1) { return { cls: "", text: "Morgen fällig (" + fmtDate(task.due) + ")" }; }
    return { cls: "", text: "Fällig " + fmtDate(task.due) };
  }

  function fmtDeviation(days) {
    if (days === 0) { return { text: "±0 Tage", tone: "mint" }; }
    if (days < 0) { return { text: "−" + (-days) + " " + plural(-days, "Tag", "Tage"), tone: "mint" }; }
    return { text: "+" + days + " " + plural(days, "Tag", "Tage"), tone: days > 10 ? "rose" : "peach" };
  }

  /* ---------------- Hilfen für HTML ---------------- */

  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  var PROJECT_STATUS = {
    "im-plan":    { label: "Im Plan",        icon: "✓", tone: "mint" },
    "beobachten": { label: "Beobachten",     icon: "!",      tone: "peach" },
    "kritisch":   { label: "Kritisch",       icon: "✕", tone: "rose" },
    "veraltet":   { label: "Daten veraltet", icon: "?",      tone: "neutral" }
  };

  function reportAge(project) {
    return project.lastReport ? -daysFromToday(project.lastReport) : null;
  }
  function isReportStale(project) {
    var age = reportAge(project);
    return age === null || age > DATA.meta.staleAfterDays;
  }
  /* Fehlende oder veraltete Berichte führen nie zu „Im Plan“. */
  function effectiveStatus(project) {
    return isReportStale(project) ? "veraltet" : project.reportedStatus;
  }

  function statusBadge(key) {
    var s = PROJECT_STATUS[key];
    return '<span class="badge tone-' + s.tone + '"><span class="badge__icon" aria-hidden="true"><span>' +
      s.icon + "</span></span>" + esc(s.label) + "</span>";
  }

  function taskStatusBadge(task) {
    if (task.status === "in-arbeit") {
      return '<span class="badge tone-sky"><span class="badge__icon" aria-hidden="true"><span>◐</span></span>In Arbeit</span>';
    }
    if (task.status === "erledigt") {
      return '<span class="badge tone-mint"><span class="badge__icon" aria-hidden="true"><span>✓</span></span>Erledigt</span>';
    }
    if (daysFromToday(task.due) < 0) {
      return '<span class="badge tone-rose"><span class="badge__icon" aria-hidden="true"><span>!</span></span>Offen · überfällig</span>';
    }
    return '<span class="badge tone-sky"><span class="badge__icon" aria-hidden="true"><span>○</span></span>Offen</span>';
  }

  function stateDot(task) {
    if (task.status === "erledigt") {
      return '<span class="state-dot is-done" aria-hidden="true">✓</span>';
    }
    if (daysFromToday(task.due) < 0) {
      return '<span class="state-dot is-overdue" aria-hidden="true">!</span>';
    }
    return '<span class="state-dot" aria-hidden="true"></span>';
  }

  function avatar(userId, large) {
    var u = usersById[userId];
    if (!u) { return ""; }
    return '<span class="avatar tone-' + u.tone + (large ? " avatar--lg" : "") + '" title="' + esc(u.name) +
      '" aria-hidden="true">' + esc(u.initials) + "</span>";
  }

  function avatarGroup(ids) {
    var names = ids.map(userName).join(", ");
    return '<span class="avatars" title="Zuständig: ' + esc(names) + '">' +
      ids.map(function (id) { return avatar(id, false); }).join("") +
      '</span><span class="sr-only">Zuständig: ' + esc(names) + "</span>";
  }

  function relationBadge(task) {
    if (!task.projectId) {
      return '<span class="chip tone-neutral">Persönlich · ohne Projekt</span>';
    }
    if (task.assigneeIds.indexOf(me.id) !== -1) {
      return '<span class="chip tone-brand">Mir zugewiesen</span>';
    }
    return '<span class="chip tone-sky">In meinem Projekt</span>';
  }

  function emptyState(icon, title, text, actionHtml) {
    return '<div class="empty-state"><span class="empty-state__icon" aria-hidden="true">' + icon + "</span>" +
      "<h2>" + esc(title) + "</h2>" + (text ? '<p class="muted">' + esc(text) + "</p>" : "") +
      (actionHtml || "") + "</div>";
  }

  function lastCompletion(task) {
    for (var i = task.history.length - 1; i >= 0; i--) {
      if (task.history[i].type === "completed") { return task.history[i]; }
    }
    return null;
  }

  /* ---------------- Ansicht: Mein Arbeitsplatz ---------------- */

  function isRelevantForMe(task) {
    if (task.assigneeIds.indexOf(me.id) !== -1) { return true; }
    var p = task.projectId ? projectsById[task.projectId] : null;
    return !!(p && p.leadId === me.id);
  }

  function byDue(a, b) { return toUtc(a.due) - toUtc(b.due); }

  function taskRow(task) {
    var p = task.projectId ? projectsById[task.projectId] : null;
    var due = dueInfo(task);
    var done = task.status === "erledigt";
    var extra = "";
    if (done) {
      var c = lastCompletion(task);
      extra = c ? '<span>Abgeschlossen von ' + esc(userName(c.by)) + " am " + esc(fmtDateTime(c.at)) + "</span>" : "";
    }
    return '<li><button type="button" class="task-row' + (done ? " is-done" : "") +
      '" data-action="open-task" data-task-id="' + esc(task.id) + '">' +
      stateDot(task) +
      '<span class="task-row__main">' +
        '<span class="task-row__title">' + esc(task.title) +
          '<span class="sr-only">, Status: ' + (done ? "erledigt" : "offen") + "</span></span>" +
        '<span class="task-row__meta">' +
          "<span>" + (p ? esc(p.name) : "Ohne Projekt") + "</span>" +
          (done ? extra : '<span class="due ' + due.cls + '">' + esc(due.text) + "</span>") +
          relationBadge(task) +
        "</span>" +
      "</span>" +
      '<span class="task-row__aside">' + avatarGroup(task.assigneeIds) + "</span>" +
      "</button></li>";
  }

  function taskGroup(title, tasks, emptyText) {
    return '<section class="task-group" aria-label="' + esc(title) + '">' +
      '<h3 class="task-group__title">' + esc(title) + ' <span class="task-group__count">' + tasks.length + "</span></h3>" +
      (tasks.length
        ? '<ul class="task-list">' + tasks.map(taskRow).join("") + "</ul>"
        : '<p class="bucket__empty">' + esc(emptyText) + "</p>") +
      "</section>";
  }

  function renderWorkspace() {
    var mine = state.tasks.filter(isRelevantForMe);
    var open = mine.filter(function (t) { return t.status !== "erledigt"; }).sort(byDue);
    var overdue = open.filter(function (t) { return daysFromToday(t.due) < 0; });
    var today = open.filter(function (t) { return daysFromToday(t.due) === 0; });
    var upcoming = open.filter(function (t) { return daysFromToday(t.due) > 0; });
    var weekEnd = endOfWeekIso();
    var thisWeek = open.filter(function (t) {
      var d = daysFromToday(t.due);
      return d >= 0 && toUtc(t.due) <= toUtc(weekEnd);
    });
    var done = mine.filter(function (t) { return t.status === "erledigt"; }).sort(function (a, b) {
      var ca = lastCompletion(a), cb = lastCompletion(b);
      return (cb ? cb.at : "").localeCompare(ca ? ca.at : "");
    }).slice(0, 4);

    var feedback = DATA.feedback.map(function (f) {
      var t = getTask(f.taskId);
      var p = t && t.projectId ? projectsById[t.projectId] : null;
      var tone = f.kind === "freigabe" ? "brand" : (f.kind === "kommentar" ? "sky" : "neutral");
      return '<li class="feedback">' +
        '<div class="feedback__top"><span class="chip tone-' + tone + '">' + esc(f.label) + "</span>" +
          "<span>" + esc(userName(f.fromId)) + " · " + esc(fmtDate(f.at)) + "</span></div>" +
        '<p class="feedback__text">„' + esc(f.text) + "“</p>" +
        (t ? '<p class="feedback__task">Aufgabe: <button type="button" class="btn btn--small btn--ghost" data-action="open-task" data-task-id="' +
          esc(t.id) + '">' + esc(t.title) + "</button>" + (p ? ' <span class="muted">· ' + esc(p.name) + "</span>" : "") + "</p>" : "") +
        "</li>";
    }).join("");

    return '<div class="page-head">' +
        '<h1 tabindex="-1">Guten Tag, ' + esc(me.name) + "</h1>" +
        '<p class="page-head__meta">' + esc(weekdayOf(DATA.meta.today)) + ", " + esc(fmtDate(DATA.meta.today)) +
          " (Stichtag der Beispieldaten) · Rolle: " + esc(me.role) + "</p>" +
      "</div>" +

      '<ul class="kpis" aria-label="Kennzahlen">' +
        '<li class="kpi kpi--rose"><span class="kpi__value">' + overdue.length + '</span><span class="kpi__label"><strong>Überfällig</strong></span></li>' +
        '<li class="kpi kpi--peach"><span class="kpi__value">' + today.length + '</span><span class="kpi__label"><strong>Heute fällig</strong></span></li>' +
        '<li class="kpi kpi--sky"><span class="kpi__value">' + thisWeek.length + '</span><span class="kpi__label"><strong>Diese Woche</strong> · bis ' + esc(fmtDate(weekEnd)) + "</span></li>" +
        '<li class="kpi kpi--brand"><span class="kpi__value">' + DATA.feedback.length + '</span><span class="kpi__label"><strong>Offene Rückmeldungen</strong></span></li>' +
      "</ul>" +

      '<div class="grid-2">' +
        '<section class="card" aria-labelledby="ws-tasks">' +
          '<div class="card__head"><h2 id="ws-tasks">Meine Aufgaben</h2>' +
            '<div class="legend"><span class="chip tone-brand">Mir zugewiesen</span><span class="chip tone-sky">In meinem Projekt</span><span class="chip tone-neutral">Persönlich</span></div>' +
          "</div>" +
          taskGroup("Überfällig", overdue, "Keine überfälligen Aufgaben.") +
          taskGroup("Heute", today, "Heute ist nichts fällig.") +
          taskGroup("Demnächst", upcoming, "Keine weiteren offenen Aufgaben.") +
        "</section>" +

        '<div class="stack">' +
          '<section class="card" aria-labelledby="ws-feedback">' +
            '<div class="card__head"><h2 id="ws-feedback">Rückmeldungen</h2><span class="card__hint">' + DATA.feedback.length + " offen</span></div>" +
            '<ul class="feedback-list">' + feedback + "</ul>" +
          "</section>" +
          '<section class="card" aria-labelledby="ws-done">' +
            '<div class="card__head"><h2 id="ws-done">Kürzlich erledigt</h2><span class="card__hint">bleiben einsehbar</span></div>' +
            (done.length ? '<ul class="task-list">' + done.map(taskRow).join("") + "</ul>" : '<p class="bucket__empty">Noch nichts erledigt.</p>') +
          "</section>" +
        "</div>" +
      "</div>";
  }

  /* ---------------- Ansicht: Projekte ---------------- */

  function nextMilestone(project) {
    var open = project.milestones.filter(function (m) { return !m.actual; });
    open.sort(function (a, b) { return toUtc(a.approved) - toUtc(b.approved); });
    return open[0] || null;
  }

  function reportCell(project) {
    var age = reportAge(project);
    if (age === null) { return '<span class="chip tone-neutral">Kein Bericht</span>'; }
    return esc(fmtDate(project.lastReport)) +
      (isReportStale(project) ? ' <span class="chip tone-neutral">? veraltet (vor ' + age + " Tagen)</span>" : "");
  }

  function renderProjects() {
    var rows = DATA.projects.map(function (p) {
      var m = nextMilestone(p);
      var lead = usersById[p.leadId];
      return "<tr>" +
        '<td data-label="Projekt"><a class="table__title" href="#/projekt/' + esc(p.id) + '">' + esc(p.name) + "</a>" +
          '<span class="table__sub">' + esc(p.goal) + "</span></td>" +
        '<td data-label="Zeitraum" class="num">' + esc(fmtDate(p.start)) + " – " + esc(fmtDate(p.end)) + "</td>" +
        '<td data-label="Projektleitung"><span class="person-inline">' +
          avatar(p.leadId, false) + "<span>" + esc(lead ? lead.name : "–") + "</span></span></td>" +
        '<td data-label="Status">' + statusBadge(effectiveStatus(p)) + "</td>" +
        '<td data-label="Nächster Meilenstein">' + (m
          ? esc(m.name) + '<span class="table__sub">Plan ' + esc(fmtDate(m.approved)) + " · Prognose " + esc(fmtDate(m.forecast)) + "</span>"
          : '<span class="muted">Keiner offen</span>') + "</td>" +
        '<td data-label="Letzter Statusbericht" class="num">' + reportCell(p) + "</td>" +
        "</tr>";
    }).join("");

    return '<div class="page-head"><h1 tabindex="-1">Projekte</h1>' +
        '<p class="page-head__meta">' + DATA.projects.length + " Beispielprojekte · Status „Daten veraltet“, wenn der letzte Statusbericht älter als " +
        DATA.meta.staleAfterDays + " Tage ist</p></div>" +
      '<div class="table-wrap table-wrap--cards">' +
        '<table class="table table--cards">' +
          '<caption class="sr-only">Projektübersicht (Beispieldaten)</caption>' +
          "<thead><tr><th scope=\"col\">Projekt</th><th scope=\"col\">Zeitraum</th><th scope=\"col\">Projektleitung</th>" +
          "<th scope=\"col\">Status</th><th scope=\"col\">Nächster Meilenstein</th><th scope=\"col\">Letzter Bericht</th></tr></thead>" +
          "<tbody>" + rows + "</tbody>" +
        "</table>" +
      "</div>";
  }

  /* ---------------- Ansicht: Projektdetail ---------------- */


  function milestoneTable(project) {
    var rows = project.milestones.map(function (m) {
      var dev = fmtDeviation(daysFromTo(m.approved, m.actual || m.forecast));
      return "<tr>" +
        '<th scope="row" class="table__title">' + esc(m.name) + "</th>" +
        '<td class="num">' + esc(fmtDate(m.baseline)) + "</td>" +
        '<td class="num">' + esc(fmtDate(m.approved)) + "</td>" +
        '<td class="num">' + (m.actual ? '<span class="muted">–</span>' : esc(fmtDate(m.forecast))) + "</td>" +
        '<td class="num">' + (m.actual ? esc(fmtDate(m.actual)) : '<span class="muted">offen</span>') + "</td>" +
        '<td class="num"><span class="chip tone-' + dev.tone + '">' + esc(dev.text) + "</span>" +
          (m.actual ? ' <span class="table__sub">tatsächlich</span>' : ' <span class="table__sub">Prognose</span>') + "</td>" +
        "</tr>";
    }).join("");
    return '<section class="section section--spaced" aria-labelledby="ms-title">' +
      '<div class="card__head"><h2 id="ms-title">Meilensteine</h2>' +
        '<span class="card__hint">Abweichung = Prognose bzw. Ist gegenüber genehmigtem Plan</span></div>' +
      '<div class="table-wrap"><table class="table table--milestones">' +
        '<caption class="sr-only">Meilensteine mit Plan-, Prognose- und Ist-Terminen</caption>' +
        '<thead><tr><th scope="col">Meilenstein</th><th scope="col">Ursprünglicher Plan</th><th scope="col">Genehmigter Plan</th>' +
        '<th scope="col">Prognose</th><th scope="col">Ist</th><th scope="col">Abweichung</th></tr></thead>' +
        "<tbody>" + rows + "</tbody></table></div>" +
      "</section>";
  }

  /* ---------------- Aufgabenboard (F19 v3): Kanban nach Status ---------------- */

  var STATUS_COLUMNS = [
    { key: "offen", label: "Offen" },
    { key: "in-arbeit", label: "In Arbeit" },
    { key: "erledigt", label: "Erledigt" }
  ];
  var STATUS_LABEL = { "offen": "Offen", "in-arbeit": "In Arbeit", "erledigt": "Erledigt" };

  function projectTasks(p) {
    return state.tasks.filter(function (t) { return t.projectId === p.id; });
  }

  function taskStats(p) {
    var tasks = projectTasks(p);
    return {
      open: tasks.filter(function (t) { return t.status !== "erledigt"; }).length,
      inProgress: tasks.filter(function (t) { return t.status === "in-arbeit"; }).length,
      overdue: tasks.filter(function (t) { return t.status !== "erledigt" && daysFromToday(t.due) < 0; }).length
    };
  }

  function kanbanFiltered(p) {
    var f = state.kanban;
    var q = f.q.toLowerCase();
    var list = projectTasks(p).filter(function (t) {
      if (f.bucket && t.bucketId !== f.bucket) { return false; }
      if (f.person && t.assigneeIds.indexOf(f.person) === -1) { return false; }
      if (f.milestone && t.milestoneId !== f.milestone) { return false; }
      if (f.priority && (t.priority || "mittel") !== f.priority) { return false; }
      if (f.mine && t.assigneeIds.indexOf(me.id) === -1) { return false; }
      if (q && (t.title + " " + (t.description || "")).toLowerCase().indexOf(q) === -1) { return false; }
      return true;
    });
    list.sort(function (a, b) { return f.sort === "desc" ? byDue(b, a) : byDue(a, b); });
    return list;
  }

  // Fälligkeit: überfällig rot, heute orange (nur offene Aufgaben), mit Symbol und Text
  function kanbanDue(task) {
    if (task.status === "erledigt") { return '<span class="muted">Fällig war ' + esc(fmtDate(task.due)) + "</span>"; }
    var diff = daysFromToday(task.due);
    if (diff < 0) {
      return '<span class="badge tone-rose"><span class="badge__icon" aria-hidden="true"><span>!</span></span>überfällig · ' + esc(fmtDate(task.due)) + "</span>";
    }
    if (diff === 0) {
      return '<span class="badge tone-peach"><span class="badge__icon" aria-hidden="true"><span>●</span></span>heute fällig</span>';
    }
    return "<span>Fällig " + esc(fmtDate(task.due)) + "</span>";
  }

  // Priorität ist kein Status: neutrale Darstellung mit Symbol und Text
  function priorityChip(task) {
    var pr = priorityDef(task.priority);
    return '<span class="chip chip--prio chip--prio-' + pr.key + '"><span aria-hidden="true">' + pr.icon + "</span> Priorität " + esc(pr.label) + "</span>";
  }

  function statusSelect(task) {
    return '<label class="kb-status"><span class="sr-only">Status von „' + esc(task.title) + '“ ändern</span>' +
      '<select data-kanban-status="' + esc(task.id) + '">' +
      STATUS_COLUMNS.map(function (c) {
        return '<option value="' + c.key + '"' + (task.status === c.key ? " selected" : "") + ">" + esc(c.label) + "</option>";
      }).join("") + "</select></label>";
  }

  function kanbanCard(task, p) {
    var b = getBucket(p, task.bucketId);
    var m = getMilestone(p, task.milestoneId);
    var done = task.status === "erledigt";
    return '<li class="kb-card' + (done ? " is-done" : "") + '" draggable="true" data-task-id="' + esc(task.id) + '">' +
      '<button type="button" class="kb-card__title" data-action="open-task" data-task-id="' + esc(task.id) + '">' + esc(task.title) + "</button>" +
      '<div class="kb-card__meta">' + kanbanDue(task) + priorityChip(task) + "</div>" +
      (done ? '<p class="kb-card__done">' + esc(lastCompletionText(task)) + "</p>" : "") +
      '<div class="kb-card__chips">' +
        (b ? '<span class="chip tone-neutral">' + esc(b.name) + "</span>" : "") +
        (m ? '<span class="chip tone-brand">◆ ' + esc(m.name) + "</span>" : '<span class="chip chip--quiet">ohne Meilenstein</span>') +
      "</div>" +
      '<div class="kb-card__foot">' + avatarGroup(task.assigneeIds) + statusSelect(task) + "</div>" +
      "</li>";
  }

  function kanbanFilters(p, shown, total) {
    var f = state.kanban;
    var people = [];
    projectTasks(p).forEach(function (t) {
      t.assigneeIds.forEach(function (id) { if (people.indexOf(id) === -1) { people.push(id); } });
    });
    function select(name, label, options, value) {
      return '<label class="kb-filter"><span>' + esc(label) + '</span><select data-kanban-filter="' + name + '">' +
        '<option value="">Alle</option>' +
        options.map(function (o) {
          return '<option value="' + esc(o.value) + '"' + (o.value === value ? " selected" : "") + ">" + esc(o.label) + "</option>";
        }).join("") + "</select></label>";
    }
    return '<p class="kb-concept" role="note">Konzeptskizze: Anlegen, Bearbeiten und Verschieben wirken nur in diesem Browser. „Beispieldaten zurücksetzen“ stellt den Ausgangszustand wieder her.</p>' +
      '<div class="kb-toolbar">' +
      '<div class="kb-filters" role="group" aria-label="Aufgaben filtern">' +
        '<label class="kb-filter kb-filter--search"><span>Suche</span><input type="search" data-kanban-filter="q" value="' + esc(f.q) + '" placeholder="Titel oder Beschreibung"></label>' +
        select("bucket", "Bucket", p.buckets.map(function (b) { return { value: b.id, label: b.name }; }), f.bucket) +
        select("person", "Person", people.map(function (id) { return { value: id, label: userName(id) }; }), f.person) +
        select("milestone", "Meilenstein", p.milestones.map(function (m) { return { value: m.id, label: m.name }; }), f.milestone) +
        select("priority", "Priorität", PRIORITIES.map(function (x) { return { value: x.key, label: x.label }; }), f.priority) +
        '<label class="kb-check"><input type="checkbox" data-kanban-filter="mine"' + (f.mine ? " checked" : "") + "> nur meine</label>" +
      "</div>" +
      '<div class="kb-toolbar__right"><span class="muted kb-shown" aria-live="polite">' + shown + " von " + total + " Aufgaben</span>" +
        '<div class="segmented" role="group" aria-label="Ansicht">' +
          '<button type="button" data-action="kanban-view" data-view="board" aria-pressed="' + (f.view === "board") + '">Board</button>' +
          '<button type="button" data-action="kanban-view" data-view="list" aria-pressed="' + (f.view === "list") + '">Liste</button>' +
        "</div></div>" +
      "</div>";
  }

  function quickAdd(col) {
    return '<form class="kb-quick" data-kanban-quick="' + col.key + '">' +
      '<label class="sr-only" for="kb-new-' + col.key + '">Neue Aufgabe in „' + esc(col.label) + '“</label>' +
      '<input id="kb-new-' + col.key + '" type="text" maxlength="200" placeholder="+ Aufgabe (Titel, Enter)" autocomplete="off">' +
      "</form>";
  }

  // Aufgabenbereich: Board (Spalten Offen/In Arbeit/Erledigt) oder Liste
  function taskBoard(p) {
    var all = projectTasks(p);
    var tasks = kanbanFiltered(p);
    var body;
    if (state.kanban.view === "list") {
      var sortLabel = state.kanban.sort === "desc" ? "absteigend" : "aufsteigend";
      body = tasks.length
        ? '<div class="table-wrap table-wrap--cards"><table class="table table--cards kb-table"><caption class="sr-only">Aufgaben als Liste, sortiert nach Fälligkeit ' + sortLabel + "</caption>" +
          '<thead><tr><th scope="col">Aufgabe</th><th scope="col">Status</th>' +
          '<th scope="col" aria-sort="' + (state.kanban.sort === "desc" ? "descending" : "ascending") + '"><button type="button" class="kb-sort" data-action="kanban-sort">Fälligkeit ' +
            (state.kanban.sort === "desc" ? "▼" : "▲") + '<span class="sr-only"> (' + sortLabel + ", zum Umkehren klicken)</span></button></th>" +
          '<th scope="col">Priorität</th><th scope="col">Zuständig</th><th scope="col">Bucket</th><th scope="col">Meilenstein</th></tr></thead><tbody>' +
          tasks.map(function (t) {
            var b = getBucket(p, t.bucketId);
            var m = getMilestone(p, t.milestoneId);
            return '<tr><td data-label="Aufgabe"><button type="button" class="kb-card__title" data-action="open-task" data-task-id="' + esc(t.id) + '">' + esc(t.title) + "</button></td>" +
              '<td data-label="Status">' + statusSelect(t) + "</td>" +
              '<td data-label="Fälligkeit">' + kanbanDue(t) + "</td>" +
              '<td data-label="Priorität">' + priorityChip(t) + "</td>" +
              '<td data-label="Zuständig">' + avatarGroup(t.assigneeIds) + "</td>" +
              '<td data-label="Bucket">' + (b ? esc(b.name) : "–") + "</td>" +
              '<td data-label="Meilenstein">' + (m ? esc(m.name) : '<span class="muted">–</span>') + "</td></tr>";
          }).join("") + "</tbody></table></div>"
        : emptyState("∅", "Keine Aufgaben für diese Filter", "", "");
    } else {
      body = '<div class="kb-board">' + STATUS_COLUMNS.map(function (c) {
        var inCol = tasks.filter(function (t) { return t.status === c.key; });
        return '<section class="kb-col" data-kanban-drop="' + c.key + '" aria-labelledby="kb-h-' + c.key + '">' +
          '<header class="kb-col__head"><h3 id="kb-h-' + c.key + '">' + esc(c.label) + '</h3><span class="kb-count"><span class="sr-only">Anzahl: </span>' + inCol.length + "</span></header>" +
          quickAdd(c) +
          (inCol.length
            ? '<ul class="kb-list">' + inCol.map(function (t) { return kanbanCard(t, p); }).join("") + "</ul>"
            : '<p class="bucket__empty">Hierher ziehen oder Status ändern</p>') +
          "</section>";
      }).join("") + "</div>" +
      '<p class="card__hint kb-hint">Karten lassen sich zwischen den Spalten ziehen. Ohne Maus: Status über die Auswahl auf der Karte ändern. Karte anklicken öffnet das Detailpanel zum Bearbeiten.</p>';
    }
    return kanbanFilters(p, tasks.length, all.length) + body;
  }

  function setTaskStatus(id, status) {
    var task = getTask(id);
    if (!task || !STATUS_LABEL[status] || task.status === status) { return; }
    if (status === "erledigt") {
      task.history.push({ type: "completed", by: me.id, at: stampNow() });
    } else if (task.status === "erledigt") {
      task.history.push({ type: "reopened", by: me.id, at: stampNow() });
    } else if (status === "in-arbeit") {
      task.history.push({ type: "started", by: me.id, at: stampNow() });
    }
    task.status = status;
    saveTasks();
    renderRoute(false);
    var select = document.querySelector('#main [data-kanban-status="' + id + '"]');
    if (select) { select.focus(); }
    toast("„" + task.title + "“: " + STATUS_LABEL[status] + (status === "erledigt" ? " – " + lastCompletionText(task) : "") + ".");
  }

  function quickCreate(p, status, title) {
    var f = state.kanban;
    var due = new Date(TODAY + 7 * DAY_MS);
    var task = {
      id: "t-neu-" + new Date().getTime(),
      projectId: p.id,
      bucketId: f.bucket || p.buckets[0].id,
      milestoneId: f.milestone || null,
      title: title,
      due: due.getUTCFullYear() + "-" + pad(due.getUTCMonth() + 1) + "-" + pad(due.getUTCDate()),
      status: status,
      priority: f.priority || "mittel",
      assigneeIds: [me.id],
      description: "",
      comments: [],
      history: [{ type: "created", by: me.id, at: stampNow() }]
    };
    if (status === "erledigt") { task.history.push({ type: "completed", by: me.id, at: stampNow() }); }
    state.tasks.push(task);
    saveTasks();
    renderRoute(false);
    var input = document.getElementById("kb-new-" + status);
    if (input) { input.focus(); }
    toast("Aufgabe „" + title + "“ angelegt (nur in diesem Browser).");
  }

  function renderProject(id, section, ms) {
    var p = projectsById[id];
    if (!p) {
      return '<div class="page-head"><h1 tabindex="-1">Projekt nicht gefunden</h1></div>' +
        emptyState("?", "Dieses Beispielprojekt gibt es nicht", "Der Link verweist auf kein Projekt in den Beispieldaten.",
          '<a class="btn" href="#/projekte">Zur Projektübersicht</a>');
    }
    var lead = usersById[p.leadId];
    // Kompakter Projektkopf (F19 v3): Name, Status, Eckdaten in einer Zeile
    return journey.band() +
      '<p class="breadcrumb"><a href="#/projekte">Projekte</a> <span aria-hidden="true">›</span> <span class="muted">' + esc(p.name) + "</span></p>" +
      '<header class="project-compact">' +
        '<div class="project-compact__title"><h1 id="p-title" tabindex="-1">' + esc(p.name) + "</h1>" + statusBadge(effectiveStatus(p)) + "</div>" +
        '<p class="project-compact__facts muted">' + esc(fmtDate(p.start)) + " – " + esc(fmtDate(p.end)) +
          " · Projektleitung " + esc(lead ? lead.name : "–") + " · Auftraggeber " + esc(p.sponsor) + "</p>" +
      "</header>" +
      journey.render(p, section, ms);
  }

  /* ---------------- Ansicht: Management ---------------- */

  function renderManagement() {
    var counts = {};
    DATA.projects.forEach(function (p) {
      var s = effectiveStatus(p);
      counts[s] = (counts[s] || 0) + 1;
    });
    var summary = Object.keys(PROJECT_STATUS).map(function (key) {
      return '<span class="badge tone-' + PROJECT_STATUS[key].tone + '"><span class="badge__icon" aria-hidden="true"><span>' +
        PROJECT_STATUS[key].icon + "</span></span>" + esc(PROJECT_STATUS[key].label) + ": " + (counts[key] || 0) + "</span>";
    }).join("");

    var cards = DATA.projects.map(function (p) {
      var status = effectiveStatus(p);
      var stale = isReportStale(p);
      var age = reportAge(p);
      var upcoming = p.milestones.filter(function (m) { return !m.actual; })
        .sort(function (a, b) { return toUtc(a.approved) - toUtc(b.approved); }).slice(0, 2);
      var ms = upcoming.length ? '<ul class="ms-list">' + upcoming.map(function (m) {
        var dev = fmtDeviation(daysFromTo(m.approved, m.forecast));
        // Veraltete Berichte: Prognose nicht farblich bewerten (nie grün)
        if (stale) { dev = { tone: "neutral", text: "? Prognose veraltet (" + dev.text + ")" }; }
        return '<li class="ms-item"><span class="ms-item__name">' + esc(m.name) + "</span>" +
          '<span class="chip tone-' + dev.tone + '">' + esc(dev.text) + "</span>" +
          '<span class="ms-item__dates">Plan ' + esc(fmtDate(m.approved)) + " · Prognose " + esc(fmtDate(m.forecast)) +
            (m.baseline !== m.approved ? " · ursprünglich " + esc(fmtDate(m.baseline)) : "") + "</span></li>";
      }).join("") + "</ul>" : '<p class="muted">Keine offenen Meilensteine.</p>';

      var lead = usersById[p.leadId];
      return '<article class="card mgmt-card" aria-labelledby="mg-' + esc(p.id) + '">' +
        '<div class="card__head"><div><h2 id="mg-' + esc(p.id) + '"><a href="#/projekt/' + esc(p.id) + '">' + esc(p.name) + "</a></h2>" +
          '<p class="mgmt-card__lead">Projektleitung: ' + esc(lead ? lead.name : "–") + "</p></div>" + statusBadge(status) + "</div>" +
        (stale ? '<p class="note note--inline">Bewertung nicht möglich: letzter Bericht ist ' + (age === null ? "nicht vorhanden" : age + " Tage alt") +
          ". Zuletzt gemeldet: " + esc(PROJECT_STATUS[p.reportedStatus] ? PROJECT_STATUS[p.reportedStatus].label : "unbekannt") + ".</p>" : "") +
        '<div><h3 class="mgmt-card__subtitle">Nächste Meilensteine</h3>' + ms + "</div>" +
        '<p class="report-line"><span class="muted">Letzter Statusbericht:</span> ' + reportCell(p) + "</p>" +
        (p.decision
          ? '<div class="decision"><strong>Entscheidungsbedarf:</strong> ' + esc(p.decision) + "</div>"
          : '<div class="decision decision--none">Kein Entscheidungsbedarf gemeldet.</div>') +
        "</article>";
    }).join("");

    return '<div class="page-head"><h1 tabindex="-1">Management-Übersicht</h1>' +
        '<p class="page-head__meta">Stand ' + esc(fmtDate(DATA.meta.today)) + " · Beispieldaten</p></div>" +
      '<p class="note">Fortschritt wird bewusst über Meilensteine (Plan gegenüber Prognose) und Statusberichte dargestellt, nicht als Anteil erledigter Aufgaben.</p>' +
      '<div class="status-summary" aria-label="Projekte nach Status">' + summary + "</div>" +
      '<div class="mgmt-grid">' + cards + "</div>";
  }

  /* ---------------- Aufgaben-Detail (Dialog) ---------------- */

  var dialog = document.getElementById("task-dialog");
  var lastTriggerTaskId = null;

  function historyText(h) {
    var who = esc(userName(h.by));
    var when = '<time>' + esc(fmtDateTime(h.at)) + "</time>";
    if (h.type === "completed") { return "Abgeschlossen von " + who + " am " + when; }
    if (h.type === "reopened") { return "Wiedergeöffnet von " + who + " am " + when; }
    if (h.type === "started") { return "In Arbeit genommen von " + who + " am " + when; }
    if (h.type === "edited") { return "Bearbeitet von " + who + " am " + when; }
    return "Erstellt von " + who + " am " + when;
  }

  var PRIORITIES = [
    { key: "hoch", label: "hoch", icon: "▲" },
    { key: "mittel", label: "mittel", icon: "■" },
    { key: "niedrig", label: "niedrig", icon: "▼" }
  ];

  function priorityDef(key) {
    return PRIORITIES.filter(function (x) { return x.key === key; })[0] || PRIORITIES[1];
  }

  function stampNow() {
    var now = new Date();
    return DATA.meta.today + " " + pad(now.getHours()) + ":" + pad(now.getMinutes());
  }

  function lastCompletionText(task) {
    var c = lastCompletion(task);
    return c ? "Abgeschlossen von " + userName(c.by) + " am " + fmtDateTime(c.at) : "";
  }

  // Detailpanel zum Bearbeiten (Konzeptskizze: Änderungen nur in diesem Browser)
  function renderDialog(task) {
    var p = task.projectId ? projectsById[task.projectId] : null;
    var b = getBucket(p, task.bucketId);
    var done = task.status === "erledigt";

    function option(value, label, selected) {
      return '<option value="' + esc(value) + '"' + (selected ? " selected" : "") + ">" + esc(label) + "</option>";
    }

    var comments = '<ul class="comments" id="tf-comments">' + task.comments.map(function (c) {
      return '<li class="comment">' + avatar(c.by, false) + '<div class="comment__bubble"><p class="comment__meta">' +
        esc(userName(c.by)) + " · " + esc(fmtDateTime(c.at)) + "</p><p>" + esc(c.text) + "</p></div></li>";
    }).join("") + "</ul>";

    var history = task.history.slice().reverse().map(function (h) {
      return '<li class="is-' + esc(h.type) + '">' + historyText(h) + "</li>";
    }).join("");

    var projectFields = p
      ? '<div class="dlg-row">' +
          '<div class="dlg-field"><label for="tf-bucket">Bucket</label><select id="tf-bucket" name="bucket">' +
            p.buckets.map(function (x) { return option(x.id, x.name, x.id === task.bucketId); }).join("") + "</select></div>" +
          '<div class="dlg-field"><label for="tf-ms">Meilenstein</label><select id="tf-ms" name="milestone">' +
            option("", "kein Meilenstein", !task.milestoneId) +
            p.milestones.map(function (x) { return option(x.id, x.name, x.id === task.milestoneId); }).join("") + "</select></div>" +
        "</div>" +
        '<fieldset class="dlg-field dlg-people"><legend>Zuständig (mehrere möglich)</legend>' +
          DATA.users.map(function (u) {
            return '<label class="dlg-check"><input type="checkbox" name="assignee" value="' + esc(u.id) + '"' +
              (task.assigneeIds.indexOf(u.id) !== -1 ? " checked" : "") + "> " + esc(u.name) + "</label>";
          }).join("") + "</fieldset>"
      : '<p class="muted">Persönliche Aufgabe: ohne Bucket, Meilenstein und Zuweisung.</p>';

    dialog.innerHTML =
      '<form class="dlg" data-task-form="' + esc(task.id) + '" novalidate>' +
        '<div class="dlg__head"><div>' +
          '<p class="dlg__context">' + (p ? esc(p.name) + (b ? " · " + esc(b.name) : "") : "Persönliche Aufgabe · ohne Projekt") + "</p>" +
          '<h2 id="dlg-title" class="dlg__title">' + esc(task.title) + "</h2>" +
          '<div class="dlg__badges">' + taskStatusBadge(task) + relationBadge(task) + "</div>" +
          (done ? '<p class="dlg__done">' + esc(lastCompletionText(task)) + "</p>" : "") +
        "</div>" +
        '<button type="button" class="btn btn--icon btn--ghost" data-action="close-dialog" aria-label="Detailbereich schließen">✕</button>' +
        "</div>" +
        '<div class="dlg__body">' +
          '<p class="dlg-error" id="tf-error" role="alert" hidden></p>' +
          '<div class="dlg-field"><label for="tf-title">Titel</label><input id="tf-title" name="title" type="text" maxlength="200" required value="' + esc(task.title) + '"></div>' +
          '<div class="dlg-field"><label for="tf-desc">Beschreibung</label><textarea id="tf-desc" name="description" rows="3">' + esc(task.description || "") + "</textarea></div>" +
          '<div class="dlg-row">' +
            '<div class="dlg-field"><label for="tf-due">Fälligkeit</label><input id="tf-due" name="due" type="date" value="' + esc(task.due || "") + '"></div>' +
            '<div class="dlg-field"><label for="tf-prio">Priorität</label><select id="tf-prio" name="priority">' +
              PRIORITIES.map(function (x) { return option(x.key, x.label, x.key === (task.priority || "mittel")); }).join("") + "</select></div>" +
          "</div>" +
          projectFields +
          '<section><h3>Kommentare</h3>' + comments +
            '<div class="dlg-field"><label for="tf-comment">Kommentar hinzufügen</label><textarea id="tf-comment" rows="2"></textarea></div>' +
            '<button type="button" class="btn btn--small" data-action="add-comment" data-task-id="' + esc(task.id) + '">Kommentar hinzufügen</button></section>' +
          '<section><h3>Verlauf</h3><ol class="timeline">' + history + "</ol></section>" +
        "</div>" +
        '<div class="dlg__foot">' +
          '<span class="dlg__foot-hint">Konzeptskizze: Änderungen nur in diesem Browser.</span>' +
          '<div class="dlg__actions">' +
            '<button type="button" class="btn btn--danger" data-action="delete-task" data-task-id="' + esc(task.id) + '">Löschen</button>' +
            '<button type="button" class="btn" data-action="toggle-task" data-task-id="' + esc(task.id) + '">' + (done ? "↺ Wiederöffnen" : "✓ Abschließen") + "</button>" +
            '<button type="button" class="btn btn--ghost" data-action="close-dialog">Abbrechen</button>' +
            '<button type="submit" class="btn btn--primary">Speichern</button>' +
          "</div>" +
        "</div>" +
      "</form>";
  }

  function saveTaskForm(form) {
    var task = getTask(form.getAttribute("data-task-form"));
    if (!task) { return; }
    var title = form.elements.title.value.replace(/^\s+|\s+$/g, "");
    var error = form.querySelector("#tf-error");
    if (!title) {
      error.textContent = "Bitte einen Titel eingeben.";
      error.hidden = false;
      form.elements.title.focus();
      return;
    }
    task.title = title;
    task.description = form.elements.description.value;
    task.due = form.elements.due.value || task.due;
    task.priority = form.elements.priority.value;
    if (task.projectId) {
      task.bucketId = form.elements.bucket.value;
      task.milestoneId = form.elements.milestone.value || null;
      var checked = form.querySelectorAll('input[name="assignee"]:checked');
      var ids = [];
      for (var i = 0; i < checked.length; i++) { ids.push(checked[i].value); }
      task.assigneeIds = ids;
    }
    task.history.push({ type: "edited", by: me.id, at: stampNow() });
    saveTasks();
    renderRoute(false);
    renderDialog(task);
    var submit = dialog.querySelector('button[type="submit"]');
    if (submit) { submit.focus(); }
    toast("Gespeichert (nur in diesem Browser).");
  }

  function addComment(id) {
    var task = getTask(id);
    var field = dialog.querySelector("#tf-comment");
    if (!task || !field) { return; }
    var text = field.value.replace(/^\s+|\s+$/g, "");
    if (!text) { field.focus(); return; }
    var comment = { by: me.id, at: stampNow(), text: text };
    task.comments.push(comment);
    saveTasks();
    // Nur die Liste ergänzen, damit ungespeicherte Eingaben im Formular erhalten bleiben
    var listEl = dialog.querySelector("#tf-comments");
    listEl.insertAdjacentHTML("beforeend", '<li class="comment">' + avatar(comment.by, false) + '<div class="comment__bubble"><p class="comment__meta">' +
      esc(userName(comment.by)) + " · " + esc(fmtDateTime(comment.at)) + "</p><p>" + esc(comment.text) + "</p></div></li>");
    field.value = "";
    field.focus();
    toast("Kommentar hinzugefügt.");
  }

  function deleteTask(id) {
    var task = getTask(id);
    if (!task) { return; }
    if (!window.confirm("Aufgabe „" + task.title + "“ wirklich löschen? (Konzeptskizze, nur in diesem Browser)")) { return; }
    state.tasks = state.tasks.filter(function (t) { return t.id !== id; });
    saveTasks();
    lastTriggerTaskId = null;
    closeDialog();
    renderRoute(false);
    toast("Aufgabe gelöscht.");
  }

  function openTask(id) {
    var task = getTask(id);
    if (!task) { return; }
    state.openTaskId = id;
    lastTriggerTaskId = id;
    renderDialog(task);
    if (!dialog.open) {
      if (typeof dialog.showModal === "function") {
        dialog.showModal();
      } else {
        dialog.setAttribute("open", "");
      }
    }
    document.body.classList.add("dialog-open");
    var closeBtn = dialog.querySelector('[data-action="close-dialog"]');
    if (closeBtn) { closeBtn.focus(); }
  }

  function closeDialog() {
    if (!dialog.open && !dialog.hasAttribute("open")) { return; }
    if (typeof dialog.close === "function") {
      dialog.close();            // löst "close" aus
    } else {
      dialog.removeAttribute("open");
      onDialogClosed();
    }
  }

  function onDialogClosed() {
    state.openTaskId = null;
    document.body.classList.remove("dialog-open");
    var target = lastTriggerTaskId
      ? document.querySelector('#main [data-action="open-task"][data-task-id="' + lastTriggerTaskId + '"]')
      : null;
    if (!target) { target = document.querySelector("#main h1"); }
    if (target) { target.focus(); }
  }

  function toggleTask(id) {
    var task = getTask(id);
    if (!task) { return; }
    var now = new Date();
    var stamp = DATA.meta.today + " " + pad(now.getHours()) + ":" + pad(now.getMinutes());
    if (task.status === "erledigt") {
      task.status = "offen";
      task.history.push({ type: "reopened", by: me.id, at: stamp });
      toast("„" + task.title + "“ wurde wiedergeöffnet.");
    } else {
      task.status = "erledigt";
      task.history.push({ type: "completed", by: me.id, at: stamp });
      toast("„" + task.title + "“ wurde abgeschlossen – sichtbar unter „Erledigt“ und „Alle“.");
    }
    saveTasks();
    renderRoute(false);
    renderDialog(task);
    var btn = dialog.querySelector('[data-action="toggle-task"]');
    if (btn) { btn.focus(); }
  }

  /* ---------------- Toast ---------------- */

  var toastEl = document.getElementById("toast");
  var toastTimer = null;
  function toast(message) {
    toastEl.textContent = message;
    toastEl.classList.add("is-visible");
    if (toastTimer) { clearTimeout(toastTimer); }
    toastTimer = setTimeout(function () { toastEl.classList.remove("is-visible"); }, 3500);
  }

  /* ---------------- Darstellung (Hell/Dunkel) ---------------- */

  // Ohne gespeicherte Wahl gilt beim ersten Öffnen die Windows-Einstellung
  function initialTheme() {
    var stored = storageGet(THEME_KEY);
    if (stored === "light" || stored === "dark") { return stored; }
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(value) {
    if (value !== "dark") { value = "light"; }
    document.documentElement.setAttribute("data-theme", value);
    var toggle = document.querySelector('[data-action="toggle-theme"]');
    if (!toggle) { return; }
    var isDark = value === "dark";
    var label = isDark ? "Helle Ansicht" : "Dunkle Ansicht";
    toggle.setAttribute("aria-pressed", isDark ? "true" : "false");
    toggle.setAttribute("aria-label", label);
    toggle.setAttribute("title", label);
    toggle.querySelector(".theme-toggle__icon").textContent = isDark ? "☀" : "☾";
  }

  /* ---------------- Routing ---------------- */

  function parseRoute() {
    var hash = (window.location.hash || "").replace(/^#\/?/, "");
    var parts = hash.split("/");
    var name = parts[0] || "arbeitsplatz";
    if (name === "projekt") {
      if (parts[2] === "m") {
        return { name: "projekt", id: decodeURIComponent(parts[1] || ""), section: "meilenstein", ms: parts[3] || "" };
      }
      return { name: "projekt", id: decodeURIComponent(parts[1] || ""), section: journey.normalize(parts[2] || "uebersicht") };
    }
    if (name === "projekte" || name === "management" || name === "arbeitsplatz") { return { name: name }; }
    return { name: "unbekannt" };
  }

  function updateNav(route) {
    var subnav = document.getElementById("project-subnav");
    if (subnav) {
      subnav.innerHTML = route.name === "projekt" ? journey.renderSubnav(projectsById[route.id] || null, route.section) : "";
    }
    var active = route.name === "projekt" ? "projekte" : route.name;
    var links = document.querySelectorAll(".app-nav__item[data-route]");
    for (var i = 0; i < links.length; i++) {
      if (links[i].getAttribute("data-route") === active) {
        links[i].setAttribute("aria-current", "page");
      } else {
        links[i].removeAttribute("aria-current");
      }
    }
  }

  var TITLES = {
    arbeitsplatz: "Mein Arbeitsplatz",
    projekte: "Projekte",
    management: "Management",
    projekt: "Projekt",
    unbekannt: "Seite nicht gefunden"
  };

  function renderRoute(moveFocus) {
    var route = parseRoute();
    var main = document.getElementById("main");
    var html;
    if (route.name === "arbeitsplatz") { html = renderWorkspace(); }
    else if (route.name === "projekte") { html = renderProjects(); }
    else if (route.name === "management") { html = renderManagement(); }
    else if (route.name === "projekt") { html = renderProject(route.id, route.section, route.ms); }
    else {
      html = '<div class="page-head"><h1 tabindex="-1">Seite nicht gefunden</h1></div>' +
        emptyState("?", "Diese Ansicht gibt es in der Vorschau nicht", "", '<a class="btn" href="#/arbeitsplatz">Zum Arbeitsplatz</a>');
    }
    main.innerHTML = html;
    updateNav(route);

    var title = TITLES[route.name];
    if (route.name === "projekt" && projectsById[route.id]) {
      title = journey.sectionLabel(route.section, route.ms) + " · " + projectsById[route.id].name;
    }
    document.title = title + " – Projekt X (Designvorschau)";

    if (moveFocus) {
      // Bereichswechsel im Projekt: Fokus auf die Bereichsüberschrift, sonst auf h1
      var h1 = (route.name === "projekt" && route.section !== "uebersicht" && main.querySelector("#j-title")) || main.querySelector("h1");
      if (h1) { h1.focus(); }
      window.scrollTo(0, 0);
    }
  }

  /* ---------------- Ereignisse (zentrale Delegation) ---------------- */

  document.addEventListener("click", function (event) {
    var el = event.target.closest ? event.target.closest("[data-action]") : null;
    if (!el) { return; }
    var action = el.getAttribute("data-action");

    if (action === "open-task") {
      openTask(el.getAttribute("data-task-id"));
    } else if (action === "toggle-task") {
      toggleTask(el.getAttribute("data-task-id"));
    } else if (action === "close-dialog") {
      closeDialog();
    } else if (action === "add-comment") {
      addComment(el.getAttribute("data-task-id"));
    } else if (action === "delete-task") {
      deleteTask(el.getAttribute("data-task-id"));
    } else if (action === "kanban-view") {
      state.kanban.view = el.getAttribute("data-view") === "list" ? "list" : "board";
      rerenderAndFocus('[data-action="kanban-view"][data-view="' + state.kanban.view + '"]');
    } else if (action === "kanban-sort") {
      state.kanban.sort = state.kanban.sort === "desc" ? "asc" : "desc";
      rerenderAndFocus('[data-action="kanban-sort"]');
    } else if (action === "toggle-theme") {
      var value = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(value);
      storageSet(THEME_KEY, value);
    } else if (action === "reset-data") {
      storageRemove(TASK_STORE_KEY);
      state.tasks = cloneTasks();
      state.kanban = defaultKanban();
      closeDialog();
      renderRoute(false);
      toast("Beispieldaten wurden zurückgesetzt.");
    } else if (action.indexOf("journey-") === 0) {
      rerenderAndFocus(journey.handleAction(action));
    } else if (action === "skip") {
      event.preventDefault();
      var h1 = document.querySelector("#main h1");
      (h1 || document.getElementById("main")).focus();
    }
  });

  /* Klick auf den abgedunkelten Hintergrund schließt den Detailbereich. */
  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) { closeDialog(); }
  });
  dialog.addEventListener("close", onDialogClosed);

  window.addEventListener("hashchange", function () {
    var key = window.location.hash;
    if (dialog.open) {
      lastTriggerTaskId = null;
      closeDialog();
    }
    var route = parseRoute();
    journey.closeMobile();
    if (route.name === "projekt" && state.lastProjectId !== route.id) { state.kanban = defaultKanban(); }
    state.lastProjectId = route.name === "projekt" ? route.id : null;
    state.lastRouteKey = key;
    renderRoute(true);
  });

  /* ---------------- Konzeptskizze F19 (journey.js) ---------------- */

  var journey = window.PX_JOURNEY({
    esc: esc,
    fmtDate: fmtDate,
    storageGet: storageGet,
    storageSet: storageSet,
    taskBoard: taskBoard,
    taskStats: taskStats,
    today: function () { return DATA.meta.today; }
  });

  function rerenderAndFocus(selector) {
    renderRoute(false);
    var target = selector ? document.querySelector(selector) : null;
    if (target) { target.focus(); }
  }

  /* ---------------- Aufgabenboard: Filter, Formulare, Drag & Drop ---------------- */

  function currentProject() {
    var route = parseRoute();
    return route.name === "projekt" ? projectsById[route.id] || null : null;
  }

  document.addEventListener("change", function (event) {
    var el = event.target;
    var filter = el.getAttribute && el.getAttribute("data-kanban-filter");
    if (filter && filter !== "q") {
      state.kanban[filter] = filter === "mine" ? el.checked : el.value;
      rerenderAndFocus('[data-kanban-filter="' + filter + '"]');
      return;
    }
    var statusId = el.getAttribute && el.getAttribute("data-kanban-status");
    if (statusId) { setTaskStatus(statusId, el.value); }
  });

  // Suche: bei jeder Eingabe filtern, Fokus und Cursor bleiben im Suchfeld
  document.addEventListener("input", function (event) {
    var el = event.target;
    if (!el.getAttribute || el.getAttribute("data-kanban-filter") !== "q") { return; }
    state.kanban.q = el.value;
    var pos = el.selectionStart;
    renderRoute(false);
    var field = document.querySelector('#main [data-kanban-filter="q"]');
    if (field) {
      field.focus();
      try { field.setSelectionRange(pos, pos); } catch (e) { /* nicht unterstützt */ }
    }
  });

  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (form.getAttribute("data-task-form")) {
      event.preventDefault();
      saveTaskForm(form);
      return;
    }
    var status = form.getAttribute("data-kanban-quick");
    if (status) {
      event.preventDefault();
      var input = form.querySelector("input");
      var title = input.value.replace(/^\s+|\s+$/g, "");
      var p = currentProject();
      if (title && p) { quickCreate(p, status, title); }
    }
  });

  var dragId = null;

  document.addEventListener("dragstart", function (event) {
    var card = event.target.closest ? event.target.closest(".kb-card") : null;
    if (!card) { return; }
    dragId = card.getAttribute("data-task-id");
    card.classList.add("is-dragging");
    try { event.dataTransfer.setData("text/plain", dragId); } catch (e) { /* älterer Browser */ }
    event.dataTransfer.effectAllowed = "move";
  });

  document.addEventListener("dragend", function (event) {
    var card = event.target.closest ? event.target.closest(".kb-card") : null;
    if (card) { card.classList.remove("is-dragging"); }
    var over = document.querySelectorAll(".kb-col.is-over");
    for (var i = 0; i < over.length; i++) { over[i].classList.remove("is-over"); }
    dragId = null;
  });

  document.addEventListener("dragover", function (event) {
    var col = event.target.closest ? event.target.closest("[data-kanban-drop]") : null;
    if (!col || !dragId) { return; }
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
    col.classList.add("is-over");
  });

  document.addEventListener("dragleave", function (event) {
    var col = event.target.closest ? event.target.closest("[data-kanban-drop]") : null;
    if (col && !col.contains(event.relatedTarget)) { col.classList.remove("is-over"); }
  });

  document.addEventListener("drop", function (event) {
    var col = event.target.closest ? event.target.closest("[data-kanban-drop]") : null;
    if (!col || !dragId) { return; }
    event.preventDefault();
    var id = dragId;
    dragId = null;
    setTaskStatus(id, col.getAttribute("data-kanban-drop"));
  });

  /* ---------------- Start ---------------- */

  applyTheme(initialTheme());

  document.getElementById("current-user").innerHTML =
    avatar(me.id, true) +
    '<span class="current-user__text"><span>' + esc(me.name) + '</span><span class="current-user__role">Rolle: ' + esc(me.role) + "</span></span>";

  state.lastRouteKey = window.location.hash;
  state.lastProjectId = parseRoute().id || null;
  renderRoute(false);
})();
