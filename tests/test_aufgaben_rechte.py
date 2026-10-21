"""Rechtematrix Aufgaben: Rolle x Aktion x (Aufgabe im eigenen/fremden Projekt,
eigene/fremde persönliche Aufgabe) mit erwarteten Statuscodes (V07b Kriterien 5, 6, 7, 8)."""

import pytest
from django.urls import reverse

from apps.tasks import services
from apps.tasks.models import TaskEvent

OK, REDIRECT, FORBIDDEN, NOT_FOUND = 200, 302, 403, 404
LOGIN, KEIN = "login", "kein_zugriff"

AKTIONEN = ["detail_get", "edit_get", "edit_post", "complete_post", "reopen_post"]


def _zeile(*werte):
    return dict(zip(AKTIONEN, werte, strict=True))


ALLES = _zeile(OK, OK, REDIRECT, REDIRECT, REDIRECT)
ZUGEWIESEN_MA = _zeile(OK, OK, REDIRECT, REDIRECT, FORBIDDEN)  # Mitarbeiter: nicht wiederöffnen
NUR_LESEN = _zeile(OK, FORBIDDEN, FORBIDDEN, FORBIDDEN, FORBIDDEN)
KEIN_ZUGRIFF = _zeile(*[KEIN] * 5)
UNSICHTBAR = _zeile(*[NOT_FOUND] * 5)
ANONYM = _zeile(*[LOGIN] * 5)

# Objekt: t_ma (A, ma zugewiesen), t_pl (A, nur pl zugewiesen), t_b (Projekt B),
# eigen (persönliche Aufgabe der handelnden Person), fremd (persönliche Aufgabe einer anderen)
MATRIX = {
    "anonym": {"t_ma": ANONYM, "t_pl": ANONYM, "t_b": ANONYM, "fremd": ANONYM},
    "admin": {"t_ma": ALLES, "t_pl": ALLES, "t_b": ALLES, "eigen": ALLES, "fremd": ALLES},
    "pl": {"t_ma": ALLES, "t_pl": ALLES, "t_b": KEIN_ZUGRIFF, "eigen": ALLES, "fremd": UNSICHTBAR},
    "ma": {
        "t_ma": ZUGEWIESEN_MA,
        "t_pl": NUR_LESEN,
        "t_b": KEIN_ZUGRIFF,
        "eigen": ALLES,
        "fremd": UNSICHTBAR,
    },
    "mgmt": {
        "t_ma": NUR_LESEN,
        "t_pl": NUR_LESEN,
        "t_b": KEIN_ZUGRIFF,
        "eigen": ALLES,
        "fremd": UNSICHTBAR,
    },
    "ma_b": {
        "t_ma": KEIN_ZUGRIFF,
        "t_pl": KEIN_ZUGRIFF,
        "t_b": ZUGEWIESEN_MA,
        "eigen": ALLES,
        "fremd": UNSICHTBAR,
    },
    "nobody": {
        "t_ma": KEIN_ZUGRIFF,
        "t_pl": KEIN_ZUGRIFF,
        "t_b": KEIN_ZUGRIFF,
        "eigen": ALLES,
        "fremd": UNSICHTBAR,
    },
}

FAELLE = [
    (person, objekt, aktion, erwartet)
    for person, objekte in MATRIX.items()
    for objekt, zeile in objekte.items()
    for aktion, erwartet in zeile.items()
]


def _aufgabe(welt, person, objekt):
    u, t = welt["users"], welt["tasks"]
    if objekt == "eigen":
        return services.create_personal_task(actor=u[person], title="Eigene Notiz")
    if objekt == "fremd":
        return t["p_ma"] if person == "nobody" else t["p_nobody"]
    return t[objekt]


def _assert_status(response, erwartet):
    if erwartet == LOGIN:
        assert response.status_code == 302
        assert response.url.startswith(reverse("accounts:login"))
    elif erwartet == KEIN:
        assert response.status_code == 403
        assert "Kein Zugriff auf dieses Projekt" in response.content.decode()
    else:
        assert response.status_code == erwartet


@pytest.mark.django_db
@pytest.mark.parametrize(("person", "objekt", "aktion", "erwartet"), FAELLE)
def test_rechtematrix_aufgaben(client, aufgaben, person, objekt, aktion, erwartet):
    u = aufgaben["users"]
    task = _aufgabe(aufgaben, person, objekt)
    if aktion == "reopen_post":
        services.complete_task(actor=u["admin"], task=task)
        task.refresh_from_db()
    if person != "anonym":
        client.force_login(u[person])
    vorher = TaskEvent.objects.count()
    pid = task.public_id

    if aktion == "detail_get":
        response = client.get(reverse("tasks:detail", args=[pid]))
    elif aktion == "edit_get":
        response = client.get(reverse("tasks:edit", args=[pid]))
    elif aktion == "edit_post":
        daten = {"title": "Neuer Titel", "version": task.version}
        if task.project_id:
            daten["bucket"] = task.bucket_id
            daten["assignees"] = [a.user_id for a in task.assignments.filter(ended_at=None)]
        response = client.post(reverse("tasks:edit", args=[pid]), daten)
    elif aktion == "complete_post":
        response = client.post(reverse("tasks:complete", args=[pid]))
    else:
        response = client.post(reverse("tasks:reopen", args=[pid]))

    _assert_status(response, erwartet)
    if erwartet in (LOGIN, KEIN, FORBIDDEN, NOT_FOUND):
        assert b"Geheime" not in response.content
        assert TaskEvent.objects.count() == vorher
    if aktion.endswith("_post") and erwartet == REDIRECT:
        assert TaskEvent.objects.count() == vorher + 1
        ereignis = TaskEvent.objects.latest("id")
        assert ereignis.actor == u[person]
        # Administratoraktion nur, wenn es ohne Administratorbefugnis nicht erlaubt wäre
        assert ereignis.as_admin is (person == "admin" and objekt != "eigen")


ANLEGEN = {
    # Person: (A anlegen GET, A anlegen POST, B anlegen GET, Buckets A GET, Buckets A POST)
    "admin": (OK, REDIRECT, OK, OK, REDIRECT),
    "pl": (OK, REDIRECT, KEIN, OK, REDIRECT),
    "ma": (OK, REDIRECT, KEIN, FORBIDDEN, FORBIDDEN),
    "mgmt": (FORBIDDEN, FORBIDDEN, KEIN, FORBIDDEN, FORBIDDEN),
    "ma_b": (KEIN, KEIN, OK, KEIN, KEIN),
    "nobody": (KEIN, KEIN, KEIN, KEIN, KEIN),
}


@pytest.mark.django_db
@pytest.mark.parametrize(("person", "erwartet"), ANLEGEN.items())
def test_rechtematrix_anlegen_und_buckets(client, aufgaben, person, erwartet):
    u, a, b = aufgaben["users"], aufgaben["a"], aufgaben["b"]
    client.force_login(u[person])
    create_a = reverse("tasks:create", args=[a.public_id])
    daten = {"title": "Neu", "bucket": aufgaben["buckets"]["planung"].pk}
    antworten = [
        client.get(create_a),
        client.post(create_a, daten),
        client.get(reverse("tasks:create", args=[b.public_id])),
        client.get(reverse("tasks:buckets", args=[a.public_id])),
        client.post(reverse("tasks:buckets", args=[a.public_id]), {"name": "Neu " + person}),
    ]
    for response, soll in zip(antworten, erwartet, strict=True):
        _assert_status(response, soll)


@pytest.mark.django_db
@pytest.mark.parametrize("person", ["admin", "pl", "ma", "mgmt", "nobody"])
def test_persoenliche_aufgabe_anlegen_fuer_alle(client, welt, person):
    client.force_login(welt["users"][person])
    assert client.get(reverse("tasks:personal_create")).status_code == 200
    response = client.post(reverse("tasks:personal_create"), {"title": "Meine Notiz"})
    assert response.status_code == 302


@pytest.mark.django_db
def test_unbekannte_aufgabe_ist_404(client, welt):
    client.force_login(welt["users"]["admin"])
    uid = "00000000-0000-0000-0000-000000000000"
    assert client.get(f"/aufgaben/{uid}/").status_code == 404
    assert client.post(f"/aufgaben/{uid}/abschliessen/").status_code == 404


@pytest.mark.django_db
def test_abschliessen_nur_per_post(client, aufgaben):
    client.force_login(aufgaben["users"]["pl"])
    task = aufgaben["tasks"]["t_ma"]
    assert client.get(reverse("tasks:complete", args=[task.public_id])).status_code == 405
    assert client.get(reverse("tasks:reopen", args=[task.public_id])).status_code == 405


@pytest.mark.django_db
def test_bucket_eines_anderen_projekts_ist_404(client, aufgaben):
    client.force_login(aufgaben["users"]["pl"])
    fremd = aufgaben["buckets"]["vorbereitung"]
    url = reverse("tasks:bucket_update", args=[aufgaben["a"].public_id, fremd.pk])
    assert client.post(url, {"name": "Gekapert"}).status_code == 404
    fremd.refresh_from_db()
    assert fremd.name == "Vorbereitung"
