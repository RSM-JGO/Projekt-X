"""Etappe 4a: Projektnavigation, Orientierungsleiste, Übersicht (Cockpit), Gestaltungsregeln.

Serverseitig prüfbare Merkmale; die Darstellung im Browser (Hell/Dunkel, 375 px) ist hier nicht
getestet. Abnahmekriterien 2 (Leiste/Menü), 9, 10 und 12 (soweit serverseitig prüfbar).
"""

import re

import pytest
from django.contrib.staticfiles import finders
from django.urls import reverse

from apps.milestones import services
from apps.milestones.models import Deliverable, Milestone
from apps.milestones.selectors import SECTIONS

REIHENFOLGE = [
    "Übersicht",
    "Steckbrief &amp; Auftrag",
    "Kommunikation",
    "Termine &amp; Zeitstrahl",
    "Aufgaben",
    "Risiken &amp; Chancen",
    "Änderungen &amp; Entscheidungen",
    "Produkt &amp; Pilot",
    "Berichte",
    "Dokumente",
    "Abschluss &amp; Lessons Learned",
]
GEBAUT = {"Übersicht", "Termine &amp; Zeitstrahl", "Aufgaben"}


def uebersicht(client, welt, person="pl"):
    client.force_login(welt["users"][person])
    return client.get(reverse("projects:detail", args=[welt["a"].public_id])).content.decode()


def subnav(html):
    start = html.index('<div class="app-nav__sub subnav"')
    return html[start : html.index("</div>", start)]


@pytest.mark.django_db
def test_menue_zeigt_bereiche_in_reihenfolge_aus_entscheidung_006(client, welt):
    menu = subnav(uebersicht(client, welt))
    positions = [menu.index(label) for label in REIHENFOLGE]
    assert positions == sorted(positions)
    assert [label for _key, label, _url in SECTIONS] == [
        x.replace("&amp;", "&") for x in REIHENFOLGE
    ]


@pytest.mark.django_db
def test_nicht_gebaute_bereiche_sind_nicht_anklickbar(client, welt):
    menu = subnav(uebersicht(client, welt))
    items = re.findall(
        r'<li>\s*(<a class="subnav__item[^"]*" href="[^"]+"'
        r'|<span class="subnav__item is-disabled")[\s\S]*?</li>',
        menu,
    )
    assert len(items) == 11
    for chunk in re.findall(r"<li>[\s\S]*?</li>", menu):
        label = next(lbl for lbl in REIHENFOLGE if lbl in chunk)
        if label in GEBAUT:
            assert '<a class="subnav__item' in chunk
        else:
            assert (
                'aria-disabled="true"' in chunk and "folgt später" in chunk and "<a " not in chunk
            )


@pytest.mark.django_db
def test_menue_zeigt_status_und_offene_lieferobjekte_des_aktuellen_meilensteins(client, welt):
    a, pl = welt["a"], welt["users"]["pl"]
    d = Deliverable.objects.get(
        milestone__project=a, milestone__code="M0", title="Projektsteckbrief"
    )
    services.set_deliverable_status(actor=pl, project=a, deliverable=d, status="IN_ARBEIT")
    # Mit Termin wird bewertet (ohne Termin: „nicht bewertet“, siehe test_etappe4a_review.py)
    services.change_date(
        actor=pl,
        project=a,
        milestone=Milestone.objects.get(project=a, code="M0"),
        kind="PROGNOSE",
        value=services.today(),
        reason="Test",
    )
    menu = subnav(uebersicht(client, welt))
    # M0: Steckbrief hat 2 Lieferobjekte (1 in Arbeit), Kommunikation 2 (beide fehlen)
    steckbrief = re.search(
        r"<li>(?:(?!</li>)[\s\S])*Steckbrief &amp; Auftrag[\s\S]*?</li>", menu
    ).group(0)
    assert "M0: 2 offen" in steckbrief and "●" in steckbrief and ">offen<" in steckbrief
    kommunikation = re.search(r"<li>(?:(?!</li>)[\s\S])*Kommunikation[\s\S]*?</li>", menu).group(0)
    assert (
        "M0: 2 offen" in kommunikation
        and "○" in kommunikation
        and "nicht begonnen" in kommunikation
    )
    termine = re.search(
        r"<li>(?:(?!</li>)[\s\S])*Termine &amp; Zeitstrahl[\s\S]*?</li>", menu
    ).group(0)
    assert "offen</span>" not in termine  # M0 braucht nichts aus Termine
    assert "Aktuell:" in menu and "M0 Start Projektauftrag" in menu


@pytest.mark.django_db
def test_orientierungsleiste_mit_anklickbaren_meilensteinen(client, welt):
    a = welt["a"]
    html = uebersicht(client, welt, "mgmt")
    for m in Milestone.objects.filter(project=a):
        assert reverse("milestones:detail", args=[a.public_id, m.public_id]) in html
    assert 'aria-label="Abschnitte und Meilensteine"' in html
    assert "j-orient__step is-current" in html  # M0 ist aktuell
    assert "Orientierung – kein festes Phasenmodell" in html


@pytest.mark.django_db
def test_projektmenue_fuer_das_handy_ohne_javascript(client, welt):
    html = uebersicht(client, welt)
    assert '<details class="j-mobilemenu">' in html and "Projektmenü: Übersicht" in html
    css = open(finders.find("css/app.css"), encoding="utf-8").read()
    assert ".app-nav__sub { display: none; }" in css and ".j-mobilemenu { display: block; }" in css


@pytest.mark.django_db
def test_meilensteinseite_mit_vor_und_zurueck(client, welt):
    a = welt["a"]
    m1 = Milestone.objects.get(project=a, code="M1")
    client.force_login(welt["users"]["ma"])
    html = client.get(
        reverse("milestones:detail", args=[a.public_id, m1.public_id])
    ).content.decode()
    assert "‹ M0 Start Projektauftrag" in html and "M2 Pilotfreigabe ›" in html
    assert m1.goal in html and "Pflicht" in html and "optional" in html
    assert 'Bereich: <a href="' + reverse("milestones:schedule", args=[a.public_id]) in html
    assert 'Risiken &amp; Chancen <span class="muted">(folgt später)</span>' in html
    assert "0 von 5" in html or "nicht bewertet" in html


@pytest.mark.django_db
def test_uebersicht_cockpit(client, welt):
    a, pl = welt["a"], welt["users"]["pl"]
    html = uebersicht(client, welt, "mgmt")
    assert "Aktueller Abschnitt" in html and "1. Auftragsklärung" in html
    assert "Nächste Schritte" in html and "Projektsteckbrief (fehlt)" in html
    for kachel in ("Nächste Termine", "Offene Freigaben", "Aufgaben", "Team"):
        assert f">{kachel}</h2>" in html
    assert reverse("projects:team", args=[a.public_id]) in html
    assert "Mats Arbeiter" in html and "Mona Management" in html
    assert reverse("tasks:board", args=[a.public_id]) in html
    # Auflagen aus einer orangen Freigabe erscheinen als nächster Schritt
    Deliverable.objects.filter(milestone__project=a, milestone__code="M0").update(
        status="VORHANDEN"
    )
    services.grant_approval(
        actor=pl,
        project=a,
        milestone=Milestone.objects.get(project=a, code="M0"),
        light="ORANGE",
        decision="Ja",
        decided_on=services.today(),
        conditions="Stakeholder nachschärfen",
    )
    html = uebersicht(client, welt, "mgmt")
    assert (
        "Auflage aus M0 Start Projektauftrag erfüllen" in html
        and "Stakeholder nachschärfen" in html
    )
    assert "2. Initiierung" in html


@pytest.mark.django_db
def test_team_seite_und_mitgliederverwaltung_eingebunden(client, welt):
    a = welt["a"]
    client.force_login(welt["users"]["pl"])
    html = client.get(reverse("projects:team", args=[a.public_id])).content.decode()
    assert "Mitglied hinzufügen" in html and "Rollen ändern" in html
    assert 'class="app-nav__sub subnav"' in html
    response = client.post(
        reverse("projects:member_add", args=[a.public_id]),
        {"user": welt["users"]["nobody"].pk, "roles": ["MITARBEITER"]},
    )
    assert response.url == reverse("projects:team", args=[a.public_id])


@pytest.mark.django_db
def test_aufgaben_bereich_zeigt_bisheriges_board(client, aufgaben):
    a = aufgaben["a"]
    client.force_login(aufgaben["users"]["ma"])
    html = client.get(reverse("tasks:board", args=[a.public_id])).content.decode()
    assert "Aufgaben nach Bucket" in html and "Aufgabe MA" in html
    assert (
        'class="subnav__item is-active" href="' + reverse("tasks:board", args=[a.public_id]) in html
    )


# ---------- Gestaltungsregeln (Kriterium 12, serverseitig prüfbar) ----------


def _css_4a():
    css = open(finders.find("css/app.css"), encoding="utf-8").read()
    return css[css.index("Etappe 4a: Projektnavigation") : css.index("/* F23:")]


def test_neue_stile_ohne_farbige_schrift():
    """Schrift dunkel/hellgrau: Statusfarben (Linienfarben) nur für Flächen, Linien, Symbole."""
    block = _css_4a()
    assert not re.search(r"(?<![-\w])color:\s*var\(--(mint|peach|rose|sky|brand)", block)


def test_zoomsperre_f23_bleibt_und_steht_am_ende():
    css = open(finders.find("css/app.css"), encoding="utf-8").read()
    assert css.rstrip().endswith("text-size-adjust: 100%; }")
    assert "input, select, textarea { font-size: max(16px, 1rem); }" in css


@pytest.mark.django_db
def test_zoomsperre_und_darkmode_auf_projektseiten(client, welt):
    html = uebersicht(client, welt)
    assert "maximum-scale=1, user-scalable=no" in html
    assert "data-theme-toggle" in html and "js/theme.js" in html


def test_schmale_ansicht_regeln_vorhanden():
    """Unter 760 px: Leiste kompakt, Raster einspaltig, Lieferobjekte einspaltig."""
    block = _css_4a()
    mobile = block[block.index("@media (max-width: 759.98px)") :]
    for regel in (
        ".j-orient__list { display: none; }",
        ".deliv { grid-template-columns: minmax(0, 1fr); }",
    ):
        assert regel in mobile
    assert "grid-template-columns: minmax(0, 1fr); grid-auto-rows: auto;" in block


@pytest.mark.django_db
def test_status_immer_mit_text_und_grau_fuer_unbekannt(client, welt):
    html = uebersicht(client, welt)
    for icon in re.findall(
        r'<span class="jstate__icon tone-(\w+)" aria-hidden="true">([^<]*)</span>'
        r'(<span class="[^"]*">[^<]+</span>)?',
        html,
    ):
        tone, symbol, text = icon
        if symbol:
            assert text, f"Statussymbol {symbol} ohne Text"
        if symbol in ("○", "–"):
            assert tone == "neutral"
