"""Rechtematrix Etappe 4a: Person x Aktion x (eigenes/fremdes Projekt) mit erwarteten Statuscodes.

Lesen: aktive Mitglieder (auch Management) und Administrator. Schreiben: Projektleiter und
Administrator; zusätzlich setzt die verantwortliche Person (PL/MA) den Status ihres eigenen
Lieferobjekts (Abnahmekriterien 3 und 6). Nicht-Mitglieder: 403 „Kein Zugriff auf dieses
Projekt“, unbekannte Objekte 404 (Entscheidung 004).
"""

import pytest
from django.urls import reverse

from apps.audit.models import AuditLog
from apps.milestones import services
from apps.milestones.models import Deliverable, Milestone

OK, REDIRECT, FORBIDDEN = 200, 302, 403
LOGIN, KEIN = "login", "kein_zugriff"

LESEN = ["termine_get", "meilenstein_get", "plan_get", "aufgaben_get", "team_get"]
SCHREIBEN = [
    "meilenstein_neu_get",
    "meilenstein_neu_post",
    "ausblenden_post",
    "lieferobjekt_neu_get",
    "lieferobjekt_neu_post",
    "lieferobjekt_bearbeiten_get",
    "lieferobjekt_bearbeiten_post",
    "status_fremd_post",
    "freigabe_get",
    "freigabe_post",
    "plan_neu_get",
    "plan_neu_post",
    "plan_bearbeiten_post",
    "plan_genehmigen_post",
    "termin_get",
    "termin_post",
    "zeitraum_post",
]
AKTIONEN = LESEN + SCHREIBEN + ["status_eigen_post"]

VOLL = {a: OK for a in AKTIONEN} | {a: REDIRECT for a in AKTIONEN if a.endswith("_post")}
NUR_LESEN = {a: OK for a in LESEN} | {a: FORBIDDEN for a in SCHREIBEN + ["status_eigen_post"]}
VERANTWORTLICH = NUR_LESEN | {"status_eigen_post": REDIRECT}
KEIN_ZUGRIFF = {a: KEIN for a in AKTIONEN}
ANONYM = {a: LOGIN for a in AKTIONEN}

# Im eigenen Projekt A ist ma für das Lieferobjekt „eigen“ verantwortlich, mgmt für keines.
MATRIX = {
    ("anonym", "eigen"): ANONYM,
    ("admin", "eigen"): VOLL,
    ("admin", "fremd"): VOLL,
    ("pl", "eigen"): VOLL,
    ("pl", "fremd"): KEIN_ZUGRIFF,
    ("ma", "eigen"): VERANTWORTLICH,
    ("ma", "fremd"): KEIN_ZUGRIFF,
    ("mgmt", "eigen"): NUR_LESEN,
    ("mgmt", "fremd"): KEIN_ZUGRIFF,
    ("nobody", "eigen"): KEIN_ZUGRIFF,
    ("ma_b", "eigen"): KEIN_ZUGRIFF,  # verantwortlich im eigenen Projekt B, hier fremd
}

FAELLE = [
    (person, bereich, aktion, erwartet)
    for (person, bereich), aktionen in MATRIX.items()
    for aktion, erwartet in aktionen.items()
]


@pytest.fixture
def rechte_welt(welt):
    """Verantwortliche: ma für „Projektsteckbrief“ in A, ma_b für „Projektsteckbrief“ in B."""
    for key, lead, member in (("a", "pl", "ma"), ("b", "pl_b", "ma_b")):
        project = welt[key]
        d = Deliverable.objects.get(
            milestone__project=project, milestone__code="M0", title="Projektsteckbrief"
        )
        services.update_deliverable(
            actor=welt["users"][lead],
            project=project,
            deliverable=d,
            responsible=welt["users"][member],
        )
    return welt


def _anfrage(welt, bereich, aktion):
    project = welt["a"] if bereich == "eigen" else welt["b"]
    pid = project.public_id
    m0 = Milestone.objects.get(project=project, code="M0")
    eigen = Deliverable.objects.get(milestone=m0, title="Projektsteckbrief")
    fremd = Deliverable.objects.get(milestone=m0, title="Stakeholderliste")
    heute = services.today().isoformat()
    lead = welt["users"]["pl" if bereich == "eigen" else "pl_b"]
    vorbereitung = None

    def url(name, *args):
        return reverse(name, args=[pid, *args])

    table = {
        "termine_get": ("get", url("milestones:schedule"), None),
        "meilenstein_get": ("get", url("milestones:detail", m0.public_id), None),
        "plan_get": ("get", url("milestones:plan", 1), None),
        "aufgaben_get": ("get", url("tasks:board"), None),
        "team_get": ("get", url("projects:team"), None),
        "meilenstein_neu_get": ("get", url("milestones:add"), None),
        "meilenstein_neu_post": (
            "post",
            url("milestones:add"),
            {"code": "M9", "phase_name": "Extra", "title": "Zusatz", "goal": ""},
        ),
        "ausblenden_post": ("post", url("milestones:visibility", m0.public_id), {"hidden": "1"}),
        "lieferobjekt_neu_get": ("get", url("milestones:deliverable_add", m0.public_id), None),
        "lieferobjekt_neu_post": (
            "post",
            url("milestones:deliverable_add", m0.public_id),
            {"title": "Neu", "area": "termine", "status": "FEHLT"},
        ),
        "lieferobjekt_bearbeiten_get": (
            "get",
            url("milestones:deliverable_edit", fremd.public_id),
            None,
        ),
        "lieferobjekt_bearbeiten_post": (
            "post",
            url("milestones:deliverable_edit", fremd.public_id),
            {
                "title": "Stakeholderliste neu",
                "required": "on",
                "area": "kommunikation",
                "status": "FEHLT",
            },
        ),
        "status_eigen_post": (
            "post",
            url("milestones:deliverable_status", eigen.public_id),
            {"status": "VORHANDEN"},
        ),
        "status_fremd_post": (
            "post",
            url("milestones:deliverable_status", fremd.public_id),
            {"status": "VORHANDEN"},
        ),
        "freigabe_get": ("get", url("milestones:approve", m0.public_id), None),
        "freigabe_post": (
            "post",
            url("milestones:approve", m0.public_id),
            {
                "light": "GRUEN",
                "decision": "Freigegeben",
                "decided_on": heute,
                "confirm_missing": "on",
                "missing_ids": ",".join(str(m["id"]) for m in services.missing_required(m0)),
            },
        ),
        "plan_neu_get": ("get", url("milestones:plan_create"), None),
        "plan_neu_post": ("post", url("milestones:plan_create"), {"reason": "Neuer Stand"}),
        "plan_bearbeiten_post": (
            "post",
            url("milestones:plan", 1),
            {
                "start_date": project.start_date.isoformat(),
                "end_date": project.end_date.isoformat(),
                f"ms_{m0.pk}": project.start_date.isoformat(),
            },
        ),
        "plan_genehmigen_post": ("post", url("milestones:plan_approve", 1), {}),
        "termin_get": ("get", url("milestones:date_change", m0.public_id), None),
        "termin_post": (
            "post",
            url("milestones:date_change", m0.public_id),
            {"kind": "PROGNOSE", "value": heute, "reason": "Test"},
        ),
        "zeitraum_post": (
            "post",
            url("milestones:period_change"),
            {"kind": "PROGNOSE", "point": "ENDE", "value": heute, "reason": "Test"},
        ),
    }
    if aktion == "plan_neu_post":
        # Ein neuer Entwurf setzt voraus, dass kein Entwurf offen ist
        def vorbereitung():
            services.approve_plan_version(
                actor=lead, project=project, version=services.draft_version(project)
            )

    return (*table[aktion], vorbereitung)


@pytest.mark.django_db
@pytest.mark.parametrize(("person", "bereich", "aktion", "erwartet"), FAELLE)
def test_rechtematrix_meilensteine_und_termine(
    client, rechte_welt, person, bereich, aktion, erwartet
):
    methode, url, daten, vorbereitung = _anfrage(rechte_welt, bereich, aktion)
    if vorbereitung:
        vorbereitung()
    if person != "anonym":
        client.force_login(rechte_welt["users"][person])
    vorher = AuditLog.objects.count()

    response = client.post(url, daten) if methode == "post" else client.get(url)

    if erwartet == LOGIN:
        assert response.status_code == 302
        assert response.url.startswith(reverse("accounts:login"))
    elif erwartet == KEIN:
        assert response.status_code == 403
        assert "Kein Zugriff auf dieses Projekt" in response.content.decode()
    else:
        assert response.status_code == erwartet, response.content.decode()[:3000]
    if erwartet in (LOGIN, KEIN, FORBIDDEN):
        assert AuditLog.objects.count() == vorher
        assert b"Geheime Beschreibung" not in response.content
    if methode == "post" and erwartet == REDIRECT:
        assert AuditLog.objects.count() == vorher + 1
        assert AuditLog.objects.latest("id").as_admin is (person == "admin")


UNBEKANNT = "00000000-0000-0000-0000-000000000000"


@pytest.mark.django_db
@pytest.mark.parametrize("person", ["admin", "pl", "nobody"])
@pytest.mark.parametrize(
    "pfad",
    [
        "termine/",
        "aufgaben/",
        "team/",
        "meilensteine/neu/",
        "termine/plan/1/",
        f"meilensteine/{UNBEKANNT}/",
    ],
)
def test_unbekanntes_projekt_ist_404(client, welt, person, pfad):
    client.force_login(welt["users"][person])
    assert client.get(f"/projekte/{UNBEKANNT}/{pfad}").status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize("person", ["admin", "pl"])
def test_objekte_anderer_projekte_ueber_eigene_url_sind_404(client, welt, person):
    a, b = welt["a"], welt["b"]
    client.force_login(welt["users"][person])
    m_b = Milestone.objects.get(project=b, code="M0")
    d_b = m_b.deliverables.first()
    assert (
        client.get(reverse("milestones:detail", args=[a.public_id, m_b.public_id])).status_code
        == 404
    )
    assert (
        client.get(reverse("milestones:approve", args=[a.public_id, m_b.public_id])).status_code
        == 404
    )
    assert (
        client.post(
            reverse("milestones:deliverable_status", args=[a.public_id, d_b.public_id]),
            {"status": "VORHANDEN"},
        ).status_code
        == 404
    )
    assert (
        client.get(
            reverse("milestones:deliverable_edit", args=[a.public_id, d_b.public_id])
        ).status_code
        == 404
    )
    assert client.get(reverse("milestones:plan", args=[a.public_id, 99])).status_code == 404
    assert client.get(f"/projekte/{a.public_id}/meilensteine/{UNBEKANNT}/").status_code == 404
    d_b.refresh_from_db()
    assert d_b.status == "FEHLT"


@pytest.mark.django_db
def test_lesende_sehen_keine_schreibenden_schaltflaechen(client, rechte_welt):
    a = rechte_welt["a"]
    m0 = Milestone.objects.get(project=a, code="M0")
    client.force_login(rechte_welt["users"]["mgmt"])
    html = client.get(
        reverse("milestones:detail", args=[a.public_id, m0.public_id])
    ).content.decode()
    for text in (
        "Freigabe erfassen",
        "Lieferobjekt ergänzen",
        "Ausblenden",
        "Status setzen",
        "Bearbeiten",
    ):
        assert text not in html
    client.force_login(rechte_welt["users"]["ma"])
    html = client.get(
        reverse("milestones:detail", args=[a.public_id, m0.public_id])
    ).content.decode()
    assert html.count("Status setzen") == 1  # nur beim eigenen Lieferobjekt
    assert "Freigabe erfassen" not in html
