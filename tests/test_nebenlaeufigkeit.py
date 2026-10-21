"""Projektleiterregel bei gleichzeitigen Änderungen über zwei Datenbankverbindungen."""

import threading

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection

from apps.projects import services
from apps.projects.models import ProjectRole, ProjectRoleAssignment

PL, MA = ProjectRole.PROJEKTLEITER, ProjectRole.MITARBEITER


def _parallel(*aufgaben):
    """Startet die Aufgaben gleichzeitig in eigenen Threads (je eigene DB-Verbindung)."""
    start = threading.Barrier(len(aufgaben))
    ergebnisse = [None] * len(aufgaben)

    def lauf(i, aufgabe):
        try:
            start.wait(timeout=10)
            aufgabe()
            ergebnisse[i] = "ok"
        except ValidationError:
            ergebnisse[i] = "abgelehnt"
        except PermissionDenied:
            ergebnisse[i] = "keine Befugnis"
        except Exception as exc:  # pragma: no cover - Fehlerdiagnose
            ergebnisse[i] = repr(exc)
        finally:
            connection.close()

    threads = [threading.Thread(target=lauf, args=(i, a)) for i, a in enumerate(aufgaben)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    return ergebnisse


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("wiederholung", range(3))
def test_zwei_gleichzeitige_entfernungen_lassen_einen_projektleiter_uebrig(welt, wiederholung):
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    # Zweiter Projektleiter: ma
    services.change_roles(actor=u["pl"], project=a, membership=m["ma"], roles=[MA, PL])

    ergebnisse = _parallel(
        lambda: services.remove_member(actor=u["admin"], project=a, membership=m["pl"]),
        lambda: services.remove_member(actor=u["admin"], project=a, membership=m["ma"]),
    )

    assert sorted(ergebnisse) == ["abgelehnt", "ok"]
    aktive_pl = ProjectRoleAssignment.objects.filter(
        membership__project=a,
        membership__ended_at__isnull=True,
        role=PL,
        ended_at__isnull=True,
    ).count()
    assert aktive_pl == 1


@pytest.mark.django_db(transaction=True)
def test_deaktivierung_und_entfernung_gleichzeitig(welt):
    """Konto des einen PL deaktivieren, während der andere PL entfernt wird."""
    from apps.accounts.services import update_account_flags

    u, a, m = welt["users"], welt["a"], welt["memberships"]
    services.change_roles(actor=u["pl"], project=a, membership=m["ma"], roles=[MA, PL])

    ergebnisse = _parallel(
        lambda: update_account_flags(actor=u["admin"], user=u["pl"], is_active=False),
        lambda: services.remove_member(actor=u["admin"], project=a, membership=m["ma"]),
    )

    assert sorted(ergebnisse) == ["abgelehnt", "ok"]
    assert ProjectRoleAssignment.objects.filter(
        membership__project=a,
        membership__ended_at__isnull=True,
        membership__user__is_active=True,
        role=PL,
        ended_at__isnull=True,
    ).exists()


@pytest.mark.django_db(transaction=True)
def test_zwei_projektleiter_entfernen_sich_gegenseitig(welt):
    """Rechte werden erst nach der Projektsperre geprüft: Der zweite Aufruf kommt von einer
    Person, die inzwischen kein Projektleiter mehr ist, und wird abgewiesen."""
    u, a, m = welt["users"], welt["a"], welt["memberships"]
    services.change_roles(actor=u["pl"], project=a, membership=m["ma"], roles=[MA, PL])

    ergebnisse = _parallel(
        lambda: services.remove_member(actor=u["ma"], project=a, membership=m["pl"]),
        lambda: services.remove_member(actor=u["pl"], project=a, membership=m["ma"]),
    )

    assert sorted(ergebnisse) == ["keine Befugnis", "ok"]
    assert (
        ProjectRoleAssignment.objects.filter(
            membership__project=a, membership__ended_at__isnull=True, role=PL, ended_at__isnull=True
        ).count()
        == 1
    )
