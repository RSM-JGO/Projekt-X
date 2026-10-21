"""Kontoänderungen: Projektleiterregel bei Deaktivierung und Protokoll der Befugnisse."""

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.test import RequestFactory

from apps.accounts import services
from apps.accounts.admin import UserEditForm
from apps.audit.models import AuditLog
from apps.projects import services as project_services
from apps.projects.models import ProjectRole

User = get_user_model()


def _admin_formdaten(user, **aenderungen):
    daten = {
        "email": user.email,
        "display_name": user.display_name,
        "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
    }
    for flag in services.ACCOUNT_FLAGS:
        if getattr(user, flag):
            daten[flag] = "on"
    for key, value in aenderungen.items():
        if value:
            daten[key] = "on"
        else:
            daten.pop(key, None)
    return daten


@pytest.mark.django_db
def test_einziger_projektleiter_wird_erkannt(welt):
    u, a = welt["users"], welt["a"]
    assert services.sole_lead_projects(u["pl"]) == [a]
    assert services.sole_lead_projects(u["ma"]) == []
    project_services.change_roles(
        actor=u["pl"],
        project=a,
        membership=welt["memberships"]["ma"],
        roles=[ProjectRole.PROJEKTLEITER],
    )
    assert services.sole_lead_projects(u["pl"]) == []


@pytest.mark.django_db
def test_service_lehnt_deaktivierung_des_einzigen_projektleiters_ab(welt):
    u = welt["users"]
    with pytest.raises(ValidationError, match="Projekt A"):
        services.update_account_flags(actor=u["admin"], user=u["pl"], is_active=False)
    u["pl"].refresh_from_db()
    assert u["pl"].is_active
    assert not AuditLog.objects.filter(action="account.flags_changed").exists()


@pytest.mark.django_db
def test_service_deaktiviert_und_protokolliert(welt):
    u = welt["users"]
    services.update_account_flags(
        actor=u["admin"], user=u["ma"], is_active=False, can_create_projects=True
    )
    u["ma"].refresh_from_db()
    assert not u["ma"].is_active
    eintrag = AuditLog.objects.get(action="account.flags_changed")
    assert eintrag.actor == u["admin"]
    assert eintrag.object_type == "accounts.User" and eintrag.object_id == str(u["ma"].pk)
    assert eintrag.old_values == {"is_active": True, "can_create_projects": False}
    assert eintrag.new_values == {"is_active": False, "can_create_projects": True}


@pytest.mark.django_db
@pytest.mark.parametrize("person", ["pl", "ma", "creator"])
def test_service_nur_fuer_administratoren(welt, person):
    u = welt["users"]
    with pytest.raises(PermissionDenied):
        services.update_account_flags(actor=u[person], user=u["nobody"], is_admin=True)
    u["nobody"].refresh_from_db()
    assert not u["nobody"].is_admin


@pytest.mark.django_db
def test_admin_formular_lehnt_deaktivierung_ab_und_nennt_projekte(welt):
    pl = welt["users"]["pl"]
    form = UserEditForm(data=_admin_formdaten(pl, is_active=False), instance=pl)
    assert not form.is_valid()
    meldung = " ".join(form.errors["is_active"])
    assert "einziger aktiver Projektleiter" in meldung and "Projekt A" in meldung


@pytest.mark.django_db
def test_admin_formular_erlaubt_deaktivierung_ohne_projektleitung(welt):
    ma = welt["users"]["ma"]
    form = UserEditForm(data=_admin_formdaten(ma, is_active=False), instance=ma)
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_admin_speichern_protokolliert_befugnisaenderungen(welt, make_user):
    superuser = make_user(is_staff=True, is_superuser=True)
    ziel = welt["users"]["nobody"]
    model_admin = admin.site._registry[User]
    request = RequestFactory().post("/admin/")
    request.user = superuser

    form = UserEditForm(
        data=_admin_formdaten(ziel, is_admin=True, can_delete_projects=True, is_staff=True),
        instance=ziel,
    )
    assert form.is_valid(), form.errors
    with transaction.atomic():
        model_admin.save_model(request, form.save(commit=False), form, change=True)

    eintrag = AuditLog.objects.get(action="account.flags_changed")
    assert eintrag.actor == superuser
    assert eintrag.old_values == {
        "is_admin": False,
        "can_delete_projects": False,
        "is_staff": False,
    }
    assert eintrag.new_values == {"is_admin": True, "can_delete_projects": True, "is_staff": True}


@pytest.mark.django_db
def test_admin_speichern_prueft_regel_erneut(welt, make_user):
    """Auch wenn die Formularprüfung umgangen würde, lehnt save_model die Deaktivierung ab."""
    superuser = make_user(is_staff=True, is_superuser=True)
    pl = welt["users"]["pl"]
    request = RequestFactory().post("/admin/")
    request.user = superuser
    pl.is_active = False
    with pytest.raises(ValidationError), transaction.atomic():
        admin.site._registry[User].save_model(request, pl, None, change=True)
    pl.refresh_from_db()
    assert pl.is_active


@pytest.mark.django_db
def test_admin_ohne_aenderung_der_befugnisse_kein_eintrag(welt, make_user):
    superuser = make_user(is_staff=True, is_superuser=True)
    ziel = welt["users"]["ma"]
    request = RequestFactory().post("/admin/")
    request.user = superuser
    ziel.display_name = "Neuer Name"
    with transaction.atomic():
        admin.site._registry[User].save_model(request, ziel, None, change=True)
    assert not AuditLog.objects.filter(object_type="accounts.User").exists()
