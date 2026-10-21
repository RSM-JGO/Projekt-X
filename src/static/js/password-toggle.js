/*
 * Passwort anzeigen/verbergen (F22).
 * Fügt an jedes Passwortfeld mit data-password-toggle einen Umschalter ein. Ohne JavaScript
 * gibt es keinen Umschalter, das Feld bleibt normal nutzbar. Keine externen Bibliotheken,
 * kein Inline-Script.
 */
(function () {
  "use strict";

  var EYE = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>';

  function setState(input, button, visible) {
    input.type = visible ? "text" : "password";
    button.setAttribute("aria-pressed", visible ? "true" : "false");
    button.setAttribute("aria-label", visible ? "Passwort verbergen" : "Passwort anzeigen");
    button.querySelector(".password-toggle__text").textContent = visible ? "Verbergen" : "Anzeigen";
  }

  function enhance(input) {
    var wrap = document.createElement("span");
    wrap.className = "password-field";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);

    var button = document.createElement("button");
    button.type = "button";
    button.className = "password-toggle";
    button.setAttribute("aria-controls", input.id);
    button.innerHTML = EYE + '<span class="password-toggle__text"></span>';
    wrap.appendChild(button);
    setState(input, button, false);

    button.addEventListener("click", function () {
      var start = input.selectionStart;
      var end = input.selectionEnd;
      setState(input, button, input.type === "password");
      // Fokus bleibt auf dem Umschalter; Cursorposition im Feld bleibt erhalten
      try { input.setSelectionRange(start, end); } catch (e) { /* nicht unterstützt */ }
    });

    // Beim Absenden immer wieder verbergen, damit der Browser es nicht als Text speichert
    if (input.form) {
      input.form.addEventListener("submit", function () { setState(input, button, false); });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var inputs = document.querySelectorAll('input[type="password"][data-password-toggle]');
    for (var i = 0; i < inputs.length; i++) { enhance(inputs[i]); }
  });
})();
