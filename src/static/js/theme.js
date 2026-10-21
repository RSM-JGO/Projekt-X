/*
 * Hell/Dunkel-Umschalter ohne Option "System".
 * Gespeicherte Wahl im localStorage; ohne Wahl gilt beim ersten Öffnen die Windows-Einstellung.
 * Wird im <head> geladen, damit beim Seitenaufbau nicht kurz die falsche Ansicht erscheint.
 */
(function () {
  "use strict";
  var KEY = "px-theme";

  function stored() {
    try { return window.localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function store(value) {
    try { window.localStorage.setItem(KEY, value); } catch (e) { /* ohne Speicher weiter */ }
  }

  function initial() {
    var value = stored();
    if (value === "light" || value === "dark") { return value; }
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function apply(value) {
    if (value !== "dark") { value = "light"; }
    document.documentElement.setAttribute("data-theme", value);
    var toggle = document.querySelector("[data-theme-toggle]");
    if (!toggle) { return; }
    var isDark = value === "dark";
    var label = isDark ? "Helle Ansicht" : "Dunkle Ansicht";
    toggle.setAttribute("aria-pressed", isDark ? "true" : "false");
    toggle.setAttribute("aria-label", label);
    toggle.setAttribute("title", label);
    var icon = toggle.querySelector(".theme-toggle__icon");
    if (icon) { icon.textContent = isDark ? "☀" : "☾"; }
  }

  apply(initial());

  document.addEventListener("DOMContentLoaded", function () {
    apply(document.documentElement.getAttribute("data-theme"));
    var toggle = document.querySelector("[data-theme-toggle]");
    if (!toggle) { return; }
    toggle.addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      apply(next);
      store(next);
    });
  });
})();
