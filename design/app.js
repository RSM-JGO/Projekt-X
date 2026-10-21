/*
 * Projekt X – Designvorschau
 * Reine Oberflächensimulation ohne Backend. Rechte, Speicherung und
 * Benachrichtigungen werden hier NICHT umgesetzt. Zustand liegt im Speicher
 * und – falls verfügbar – im localStorage dieses Browsers.
 */
(function () {
  "use strict";

  var DATA = window.PX_DATA;
  var TASK_STORE_KEY = "px-design-tasks-v1";
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

  function cloneTasks() {
    return JSON.parse(JSON.stringify(DATA.tasks));
  }

  function loadTasks() {
    var raw = storageGet(TASK_STORE_KEY);
    if (!raw) { return cloneTasks(); }
    try {
      var stored = JSON.parse(raw);
      var ids = DATA.tasks.map(function (t) { return t.id; }).join("|");
      var storedIds = Array.isArray(stored) ? stored.map(function (t) { return t && t.id; }).join("|") : "";
      if (ids !== storedIds) { return cloneTasks(); }
      var valid = stored.every(function (t) {
        return Array.isArray(t.assigneeIds) && Array.isArray(t.history) && Array.isArray(t.comments) &&
          (t.status === "offen" || t.status === "erledigt");
      });
      return valid ? stored : cloneTasks();
    } catch (e) {
      return cloneTasks();
    }
  }

  var state = {
    tasks: loadTasks(),
    projectFilter: "offen",
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

  var FILTERS = [
    { key: "offen", label: "Offen" },
    { key: "erledigt", label: "Erledigt" },
    { key: "alle", label: "Alle" }
  ];

  function matchesFilter(task) {
    if (state.projectFilter === "alle") { return true; }
    return task.status === state.projectFilter;
  }

  function taskCard(task, project) {
    var m = getMilestone(project, task.milestoneId);
    var due = dueInfo(task);
    var done = task.status === "erledigt";
    return '<li><button type="button" class="task-card' + (done ? " is-done" : "") +
      '" data-action="open-task" data-task-id="' + esc(task.id) + '">' +
      '<span class="task-card__title">' + stateDot(task) + "<span>" + esc(task.title) + "</span></span>" +
      '<span class="task-card__meta">' +
        (m ? '<span class="chip tone-brand">◆ ' + esc(m.name) + "</span>" : '<span class="chip tone-neutral">Ohne Meilenstein</span>') +
        '<span class="due ' + due.cls + '">' + esc(due.text) + "</span>" +
      "</span>" +
      '<span class="task-card__foot">' + avatarGroup(task.assigneeIds) + taskStatusBadge(task) + "</span>" +
      "</button></li>";
  }

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

  function renderProject(id) {
    var p = projectsById[id];
    if (!p) {
      return '<div class="page-head"><h1 tabindex="-1">Projekt nicht gefunden</h1></div>' +
        emptyState("?", "Dieses Beispielprojekt gibt es nicht", "Der Link verweist auf kein Projekt in den Beispieldaten.",
          '<a class="btn" href="#/projekte">Zur Projektübersicht</a>');
    }
    var tasks = state.tasks.filter(function (t) { return t.projectId === p.id; });
    var counts = {
      offen: tasks.filter(function (t) { return t.status === "offen"; }).length,
      erledigt: tasks.filter(function (t) { return t.status === "erledigt"; }).length,
      alle: tasks.length
    };
    var visible = tasks.filter(matchesFilter).sort(byDue);
    var lead = usersById[p.leadId];

    var filterButtons = FILTERS.map(function (f) {
      return '<button type="button" data-action="set-filter" data-filter="' + f.key + '" aria-pressed="' +
        (state.projectFilter === f.key ? "true" : "false") + '">' + esc(f.label) +
        ' <span class="segmented__count">(' + counts[f.key] + ")</span></button>";
    }).join("");

    var board;
    if (!visible.length) {
      var filterLabel = state.projectFilter === "erledigt" ? "erledigten" : (state.projectFilter === "offen" ? "offenen" : "");
      board = emptyState("∅", "Keine " + filterLabel + " Aufgaben",
        "Für diesen Filter gibt es in diesem Projekt keine Aufgaben.",
        state.projectFilter !== "alle" ? '<button type="button" class="btn" data-action="set-filter" data-filter="alle">Alle Aufgaben anzeigen</button>' : "");
    } else {
      board = '<div class="board">' + p.buckets.map(function (b) {
        var inBucket = visible.filter(function (t) { return t.bucketId === b.id; });
        return '<section class="bucket" aria-label="Bucket ' + esc(b.name) + '">' +
          '<div class="bucket__head"><h3>' + esc(b.name) + '</h3><span class="bucket__count">' + inBucket.length + " " +
            plural(inBucket.length, "Aufgabe", "Aufgaben") + "</span></div>" +
          (inBucket.length
            ? '<ul class="task-list">' + inBucket.map(function (t) { return taskCard(t, p); }).join("") + "</ul>"
            : '<p class="bucket__empty">Keine Aufgaben in diesem Filter</p>') +
          "</section>";
      }).join("") + "</div>";
    }

    return '<p class="breadcrumb"><a href="#/projekte">Projekte</a> <span aria-hidden="true">›</span> <span class="muted">' + esc(p.name) + "</span></p>" +
      '<section class="card card--project" aria-labelledby="p-title">' +
        '<div class="project-head"><div>' +
          '<h1 id="p-title" tabindex="-1">' + esc(p.name) + "</h1>" +
          '<p class="muted project-head__goal">' + esc(p.goal) + "</p>" +
        "</div>" + statusBadge(effectiveStatus(p)) + "</div>" +
        '<dl class="facts">' +
          "<div><dt>Zeitraum</dt><dd>" + esc(fmtDate(p.start)) + " – " + esc(fmtDate(p.end)) + "</dd></div>" +
          "<div><dt>Projektleitung</dt><dd>" + esc(lead ? lead.name : "–") + "</dd></div>" +
          "<div><dt>Auftraggeber</dt><dd>" + esc(p.sponsor) + "</dd></div>" +
          "<div><dt>Letzter Statusbericht</dt><dd>" + reportCell(p) + "</dd></div>" +
        "</dl>" +
      "</section>" +

      '<div class="toolbar"><h2>Aufgaben nach Bucket</h2>' +
        '<div class="segmented" role="group" aria-label="Aufgaben filtern">' + filterButtons + "</div>" +
      "</div>" +
      board +
      milestoneTable(p);
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
    return "Erstellt von " + who + " am " + when;
  }

  function renderDialog(task) {
    var p = task.projectId ? projectsById[task.projectId] : null;
    var b = getBucket(p, task.bucketId);
    var m = getMilestone(p, task.milestoneId);
    var due = dueInfo(task);
    var done = task.status === "erledigt";

    var comments = task.comments.length
      ? '<ul class="comments">' + task.comments.map(function (c) {
          return '<li class="comment">' + avatar(c.by, false) + '<div class="comment__bubble"><p class="comment__meta">' +
            esc(userName(c.by)) + " · " + esc(fmtDateTime(c.at)) + "</p><p>" + esc(c.text) + "</p></div></li>";
        }).join("") + "</ul>"
      : '<p class="muted">Noch keine Kommentare.</p>';

    var history = task.history.slice().reverse().map(function (h) {
      return '<li class="is-' + esc(h.type) + '">' + historyText(h) + "</li>";
    }).join("");

    var people = '<ul class="people">' + task.assigneeIds.map(function (id) {
      return "<li>" + avatar(id, false) + "<span>" + esc(userName(id)) + "</span></li>";
    }).join("") + "</ul>";

    dialog.innerHTML =
      '<div class="dlg">' +
        '<div class="dlg__head"><div>' +
          '<p class="dlg__context">' + (p ? esc(p.name) + (b ? " · " + esc(b.name) : "") : "Persönliche Aufgabe · ohne Projekt") + "</p>" +
          '<h2 id="dlg-title" class="dlg__title">' + esc(task.title) + "</h2>" +
          '<div class="dlg__badges">' + taskStatusBadge(task) + relationBadge(task) + "</div>" +
        "</div>" +
        '<button type="button" class="btn btn--icon btn--ghost" data-action="close-dialog" aria-label="Detailbereich schließen">✕</button>' +
        "</div>" +
        '<div class="dlg__body">' +
          "<dl>" +
            "<dt>Fälligkeit</dt><dd><span class=\"due " + due.cls + '">' + esc(due.text) + "</span></dd>" +
            "<dt>Meilenstein</dt><dd>" + (m ? esc(m.name) + ' <span class="muted">(Plan ' + esc(fmtDate(m.approved)) + ")</span>" : '<span class="muted">Kein Meilenstein</span>') + "</dd>" +
            "<dt>Bucket</dt><dd>" + (b ? esc(b.name) : '<span class="muted">–</span>') + "</dd>" +
            "<dt>Zuständig</dt><dd>" + people + "</dd>" +
            (p ? '<dt>Projekt</dt><dd><a href="#/projekt/' + esc(p.id) + '">' + esc(p.name) + "</a></dd>" : "") +
          "</dl>" +
          "<section><h3>Beschreibung</h3><p>" + esc(task.description) + "</p></section>" +
          "<section><h3>Kommentare</h3>" + comments +
            '<p class="muted small-hint">Kommentieren ist in der Vorschau nicht umgesetzt.</p></section>' +
          '<section><h3>Verlauf</h3><ol class="timeline">' + history + "</ol></section>" +
        "</div>" +
        '<div class="dlg__foot">' +
          '<span class="dlg__foot-hint">Simulation: Änderung nur in diesem Browser.</span>' +
          '<button type="button" class="btn ' + (done ? "" : "btn--primary") + '" data-action="toggle-task" data-task-id="' + esc(task.id) + '">' +
            (done ? "↺ Wiederöffnen" : "✓ Abschließen") + "</button>" +
        "</div>" +
      "</div>";
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
    if (name === "projekt") { return { name: "projekt", id: decodeURIComponent(parts[1] || "") }; }
    if (name === "projekte" || name === "management" || name === "arbeitsplatz") { return { name: name }; }
    return { name: "unbekannt" };
  }

  function updateNav(route) {
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
    else if (route.name === "projekt") { html = renderProject(route.id); }
    else {
      html = '<div class="page-head"><h1 tabindex="-1">Seite nicht gefunden</h1></div>' +
        emptyState("?", "Diese Ansicht gibt es in der Vorschau nicht", "", '<a class="btn" href="#/arbeitsplatz">Zum Arbeitsplatz</a>');
    }
    main.innerHTML = html;
    updateNav(route);

    var title = TITLES[route.name];
    if (route.name === "projekt" && projectsById[route.id]) { title = projectsById[route.id].name; }
    document.title = title + " – Projekt X (Designvorschau)";

    if (moveFocus) {
      var h1 = main.querySelector("h1");
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
    } else if (action === "set-filter") {
      state.projectFilter = el.getAttribute("data-filter");
      renderRoute(false);
      var pressed = document.querySelector('#main [data-action="set-filter"][aria-pressed="true"]');
      if (pressed) { pressed.focus(); }
    } else if (action === "toggle-theme") {
      var value = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(value);
      storageSet(THEME_KEY, value);
    } else if (action === "reset-data") {
      storageRemove(TASK_STORE_KEY);
      state.tasks = cloneTasks();
      state.projectFilter = "offen";
      closeDialog();
      renderRoute(false);
      toast("Beispieldaten wurden zurückgesetzt.");
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
    if (route.name === "projekt" && state.lastRouteKey !== key) { state.projectFilter = "offen"; }
    state.lastRouteKey = key;
    renderRoute(true);
  });

  /* ---------------- Start ---------------- */

  applyTheme(initialTheme());

  document.getElementById("current-user").innerHTML =
    avatar(me.id, true) +
    '<span class="current-user__text"><span>' + esc(me.name) + '</span><span class="current-user__role">Rolle: ' + esc(me.role) + "</span></span>";

  state.lastRouteKey = window.location.hash;
  renderRoute(false);
})();
