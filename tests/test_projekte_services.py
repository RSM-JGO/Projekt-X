"""Service-Ebene: Rechte, Projektleiterregel, Protokoll (Kriterien V07a 5, 6, 7, 8)."""

import datetime

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection, transaction
from django.urls import reverse

from apps.audit.models import AppendOnlyError, AuditLog
from apps.projects import policies, services
from apps.projects.models import Project, ProjectMembership, ProjectRole, ProjectRoleAssignment
from apps.projects.selectors import accessible_projects

PL, MA, MG = ProjectRole.PROJEKTLEITER, ProjectRole.MITARBEITER, ProjectRole.MANAGEMENT


def _active_roles(membership):
    return set(
        ProjectRoleAssignment.objects.filter(
            membership=membership, ended_at__isnull=True
        ).values_list("role", flat=True)
    )


# ---------- Kriterium 5: Anlegen ----------


@pytest.mark.django_db
def test_anlegende_person_wird_projektleiter(make_user):
    creator = make_user(can_create_projects=True)
    project = services.create_project(
        actor=creator,
        name="Neu",
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 6, 30),
    )
    membership = ProjectMembership.objects.get(project=project, user=creator)
    assert membership.is_active
    assert _active_roles(membership) == {PL}
    assert project.created_by == creator
    actions = set(AuditLog.objects.filter(project=project).values_list("action", flat=True))
    assert actions == {"project.created", "membership.added"}


@pytest.mark.django_db
def test_anlegen_ueber_oberflaeche_macht_zum_projektleiter(client, make_user):
    creator = make_user(can_create_projects=True)
    client.force_login(creator)
    response = client.post(
        reverse("projects:create"),
        {"name": "Über UI", "start_date": "2026-01-01", "end_date": "2026-03-01"},
    )
    project = Project.objects.get(name="Über UI")
    assert response.url == reverse("projects:detail", args=[project.public_id])
    assert policies.active_roles(creator, project) == {PL}


@pytest.mark.django_db
@pytest.mark.parametrize("befugnis", [{}, {"can_delete_projects": True}])
def test_anlegen_ohne_befugnis_wird_im_service_abgelehnt(make_user, befugnis):
    user = make_user(**befugnis)
    with pytest.raises(PermissionDenied):
        services.create_project(
            actor=user,
            name="X",
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 1, 2),
        )
    assert not Project.objects.exists()


@pytest.mark.django_db
def test_ende_vor_beginn_wird_abgelehnt(make_user, client):
    admin = make_user(is_admin=True)
    with pytest.raises(ValidationError):
        services.create_project(
            actor=admin,
            name="X",
            start_date=datetime.date(2026, 2, 1),
            end_date=datetime.date(2026, 1, 1),
        )
    client.force_login(admin)
    response = client.post(
        reverse("projects:create"),
        {"name": "X", "start_date": "2026-02-01", "end_date": "2026-01-01"},
    )
    assert response.status_code == 200
    assert "Das Ende darf nicht vor dem Beginn liegen." in response.content.decode()
    assert not Project.objects.exists()


@pytest.mark.django_db
def test_datenbank_prueft_zeitraum(welt):
    with pytest.raises(IntegrityError), transaction.atomic():
        Project.objects.filter(pk=welt["a"].pk).update(start_date=datetime.date(2030, 1, 1))


# ---------- Kriterium 8 auf Service-Ebene ----------


@pytest.mark.django_db
@pytest.mark.parametrize("person", ["ma", "mgmt", "creator", "nobody", "pl_b"])
def test_service_lehnt_unberechtigte_aenderungen_ab(welt, person):
    actor = welt["users"][person]
    a, m, u = welt["a"], welt["memberships"], welt["users"]
    aufrufe = [
        lambda: services.update_project(actor=actor, project=a, name="Gehackt"),
        lambda: services.add_member(actor=actor, project=a, user=u["nobody"], roles=[MA]),
        lambda: services.change_roles(actor=actor, project=a, membership=m["ma"], roles=[PL]),
        lambda: services.remove_member(actor=actor, project=a, membership=m["mgmt"]),
    ]
    vorher = AuditLog.objects.count()
    for aufruf in aufrufe:
        with pytest.raises(PermissionDenied):
            aufruf()
    a.refresh_from_db()
    assert a.name == "Projekt A"
    assert AuditLog.objects.count() == vorher
    assert _active_roles(m["ma"]) == {MA}
    assert m["mgmt"].__class__.objects.get(pk=m["mgmt"].pk).is_active


@pytest.mark.django_db
def test_deaktiviertes_konto_hat_keine_rechte(welt):
    pl = welt["users"]["pl"]
    pl.is_active = False
    pl.save()
    assert not policies.can_view_project(pl, welt["a"])
    assert not policies.can_edit_project(pl, welt["a"])
    assert not accessible_projects(pl).exists()
    with pytest.raises(PermissionDenied):
        services.update_project(actor=pl, project=welt["a"], name="X")


@pytest.mark.django_db
def test_policies_einzeln(welt):
    u, a, b = welt["users"], welt["a"], welt["b"]
    assert policies.can_view_project(u["ma"], a) and not policies.can_view_project(u["ma"], b)
    assert policies.can_view_project(u["admin"], b)
    assert policies.can_edit_project(u["pl"], a) and not policies.can_edit_project(u["pl"], b)
    assert not policies.can_edit_project(u["mgmt"], a)
    assert policies.can_manage_members(u["admin"], a)
    assert not policies.can_manage_members(u["ma"], a)
    assert policies.can_create_project(u["creator"]) and not policies.can_create_project(u["ma"])
    assert policies.can_create_project(u["admin"])
    assert policies.acts_as_admin(u["admin"], a) and not policies.acts_as_admin(u["pl"], a)
    assert policies.can_edit_project(u["admin"], a) and policies.can_edit_project(u["admin"], b)


@pytest.mark.django_db
def test_rechte_ergeben_sich_aus_vereinigung_der_rollen(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    services.change_roles(actor=u["pl"], project=a, membership=m["mgmt"], roles=[MG, PL])
    assert policies.can_edit_project(u["mgmt"], a)


# ---------- Kriterium 6: letzter Projektleiter ----------


@pytest.mark.django_db
def test_letzter_projektleiter_kann_nicht_entfernt_werden(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    with pytest.raises(ValidationError):
        services.remove_member(actor=u["pl"], project=a, membership=m["pl"])
    with pytest.raises(ValidationError):
        services.remove_member(actor=u["admin"], project=a, membership=m["pl"])
    m["pl"].refresh_from_db()
    assert m["pl"].is_active
    assert _active_roles(m["pl"]) == {PL}


@pytest.mark.django_db
def test_letzter_projektleiter_kann_rolle_nicht_abgeben(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    with pytest.raises(ValidationError):
        services.change_roles(actor=u["pl"], project=a, membership=m["pl"], roles=[MA])
    assert _active_roles(m["pl"]) == {PL}


@pytest.mark.django_db
def test_letzter_projektleiter_ueber_oberflaeche_abgelehnt(client, welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    client.force_login(u["pl"])
    response = client.post(reverse("projects:member_remove", args=[a.public_id, m["pl"].pk]))
    assert response.status_code == 400
    assert "mindestens einen aktiven Projektleiter" in response.content.decode()
    response = client.post(
        reverse("projects:member_roles", args=[a.public_id, m["pl"].pk]), {"roles": [MA]}
    )
    assert response.status_code == 200
    assert "mindestens einen aktiven Projektleiter" in response.content.decode()
    assert _active_roles(m["pl"]) == {PL}


@pytest.mark.django_db
def test_projektleiter_entfernbar_wenn_ein_weiterer_existiert(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    services.change_roles(actor=u["pl"], project=a, membership=m["ma"], roles=[MA, PL])
    services.remove_member(actor=u["ma"], project=a, membership=m["pl"])
    m["pl"].refresh_from_db()
    assert not m["pl"].is_active
    assert _active_roles(m["pl"]) == set()


@pytest.mark.django_db
def test_projektleiter_mit_deaktiviertem_konto_zaehlt_nicht(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    services.change_roles(actor=u["pl"], project=a, membership=m["ma"], roles=[MA, PL])
    u["ma"].is_active = False
    u["ma"].save()
    with pytest.raises(ValidationError):
        services.remove_member(actor=u["admin"], project=a, membership=m["pl"])


# ---------- Mitgliedschaftsregeln ----------


@pytest.mark.django_db
def test_mitgliedschaft_braucht_mindestens_eine_rolle(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    with pytest.raises(ValidationError):
        services.add_member(actor=u["pl"], project=a, user=u["nobody"], roles=[])
    with pytest.raises(ValidationError):
        services.change_roles(actor=u["pl"], project=a, membership=m["ma"], roles=[])
    assert _active_roles(m["ma"]) == {MA}


@pytest.mark.django_db
def test_hoechstens_eine_aktive_mitgliedschaft(welt):
    u, a = welt["users"], welt["a"]
    with pytest.raises(ValidationError):
        services.add_member(actor=u["pl"], project=a, user=u["ma"], roles=[MG])
    with pytest.raises(IntegrityError), transaction.atomic():
        ProjectMembership.objects.create(project=a, user=u["ma"])


@pytest.mark.django_db
def test_hoechstens_eine_aktive_zuordnung_je_rolle(welt):
    m, u = welt["memberships"], welt["users"]
    with pytest.raises(IntegrityError), transaction.atomic():
        ProjectRoleAssignment.objects.create(membership=m["ma"], role=MA, assigned_by=u["pl"])


@pytest.mark.django_db
def test_wiederaufnahme_nach_austritt_erzeugt_neue_mitgliedschaft(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    services.remove_member(actor=u["pl"], project=a, membership=m["ma"])
    neu = services.add_member(actor=u["pl"], project=a, user=u["ma"], roles=[MG])
    assert neu.pk != m["ma"].pk
    assert ProjectMembership.objects.filter(project=a, user=u["ma"]).count() == 2


@pytest.mark.django_db
def test_mitgliedschaft_eines_anderen_projekts_wird_abgelehnt(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    with pytest.raises(ValidationError):
        services.remove_member(actor=u["admin"], project=a, membership=m["ma_b"])


# ---------- Kriterium 7: Protokoll ----------


@pytest.mark.django_db
def test_rollen_und_mitgliedschaftsaenderungen_werden_protokolliert(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    services.change_roles(actor=u["pl"], project=a, membership=m["ma"], roles=[MA, MG])
    eintrag = AuditLog.objects.filter(action="membership.roles_changed").get()
    assert eintrag.actor == u["pl"]
    assert eintrag.project == a
    assert eintrag.object_type == "projects.ProjectMembership"
    assert eintrag.object_id == str(m["ma"].pk)
    assert eintrag.old_values == {"user": "ma@test.invalid", "roles": ["MITARBEITER"]}
    assert eintrag.new_values == {"user": "ma@test.invalid", "roles": ["MITARBEITER", "MANAGEMENT"]}
    assert eintrag.created_at is not None
    assert not eintrag.as_admin

    services.remove_member(actor=u["admin"], project=a, membership=m["mgmt"])
    ende = AuditLog.objects.filter(action="membership.ended").get()
    assert ende.actor == u["admin"] and ende.as_admin
    assert ende.old_values == {"user": "mgmt@test.invalid", "roles": ["MANAGEMENT"]}

    added = AuditLog.objects.filter(action="membership.added", project=a)
    assert {e.new_values["user"] for e in added} == {
        "pl@test.invalid",
        "ma@test.invalid",
        "mgmt@test.invalid",
    }


@pytest.mark.django_db
def test_projektaenderung_protokolliert_alt_und_neu(welt):
    u, a = welt["users"], welt["a"]
    services.update_project(
        actor=u["pl"], project=a, name="Projekt A neu", end_date=datetime.date(2027, 1, 31)
    )
    eintrag = AuditLog.objects.filter(action="project.updated").get()
    assert eintrag.actor == u["pl"] and not eintrag.as_admin
    assert eintrag.old_values == {"name": "Projekt A", "end_date": "2026-12-31"}
    assert eintrag.new_values == {"name": "Projekt A neu", "end_date": "2027-01-31"}


@pytest.mark.django_db
def test_unveraenderte_speicherung_erzeugt_keinen_eintrag(welt):
    u, a = welt["users"], welt["a"]
    vorher = AuditLog.objects.count()
    services.update_project(actor=u["pl"], project=a, name="Projekt A")
    assert AuditLog.objects.count() == vorher


@pytest.mark.django_db
def test_abgelehnte_aenderung_hinterlaesst_keinen_eintrag(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    vorher = AuditLog.objects.count()
    with pytest.raises(ValidationError):
        services.remove_member(actor=u["pl"], project=a, membership=m["pl"])
    assert AuditLog.objects.count() == vorher


@pytest.mark.django_db
def test_protokoll_ist_nur_anfuegbar(welt):
    eintrag = AuditLog.objects.first()
    with pytest.raises(AppendOnlyError):
        eintrag.save()
    with pytest.raises(AppendOnlyError):
        eintrag.delete()
    with pytest.raises(AppendOnlyError):
        AuditLog.objects.all().update(action="x")
    with pytest.raises(AppendOnlyError):
        AuditLog.objects.all().delete()
    # Auch direktes SQL wird vom Datenbank-Trigger abgewiesen
    with pytest.raises(Exception, match="nur anfuegbar"), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("UPDATE audit_auditlog SET action = 'x'")
    with pytest.raises(Exception, match="nur anfuegbar"), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM audit_auditlog")
    # TRUNCATE: Trigger ist nur in der Testdatenbank abgeschaltet (conftest), hier wieder an
    with pytest.raises(Exception, match="TRUNCATE abgelehnt"), transaction.atomic():
        with connection.cursor() as cursor:
            # Aufgeschobene FK-Prüfungen zuerst ausführen, sonst ist ALTER TABLE nicht erlaubt
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute("ALTER TABLE audit_auditlog ENABLE TRIGGER audit_auditlog_no_truncate")
            cursor.execute("TRUNCATE audit_auditlog")
    assert AuditLog.objects.exists()


@pytest.mark.django_db
def test_administrator_bearbeitet_projekt_als_admin_aktion(welt):
    """Entscheidung 004: Der Administrator darf alles; die Aktion wird gekennzeichnet."""
    u, a = welt["users"], welt["a"]
    services.update_project(actor=u["admin"], project=a, name="Admin-Änderung")
    a.refresh_from_db()
    assert a.name == "Admin-Änderung"
    eintrag = AuditLog.objects.filter(action="project.updated").get()
    assert eintrag.actor == u["admin"] and eintrag.as_admin


@pytest.mark.django_db
def test_administrator_als_projektleiter_ist_keine_admin_aktion(welt):
    u, a = welt["users"], welt["a"]
    services.add_member(actor=u["pl"], project=a, user=u["admin"], roles=[PL])
    services.update_project(actor=u["admin"], project=a, name="Als PL")
    assert not AuditLog.objects.filter(action="project.updated").get().as_admin


@pytest.mark.django_db
def test_projektleiterregel_gilt_auch_fuer_administrator(welt):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    with pytest.raises(ValidationError):
        services.change_roles(actor=u["admin"], project=a, membership=m["pl"], roles=[MA])
    with pytest.raises(ValidationError):
        services.remove_member(actor=u["admin"], project=a, membership=m["pl"])
    assert _active_roles(m["pl"]) == {PL}


@pytest.mark.django_db
def test_administrator_verwaltet_mitglieder_protokolliert(welt):
    u, a = welt["users"], welt["a"]
    services.add_member(actor=u["admin"], project=a, user=u["nobody"], roles=[MA])
    eintrag = AuditLog.objects.filter(action="membership.added", actor=u["admin"]).get()
    assert eintrag.as_admin
