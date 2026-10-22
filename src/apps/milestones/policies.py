"""Rechte für Meilensteine, Lieferobjekte, Freigaben und Termine (Etappe 4a).

- Lesen: alle aktiven Mitglieder des Projekts (auch Management) und der Administrator.
- Schreiben (Meilensteine, Lieferobjekte, Planversionen, Prognose/Ist, Freigaben):
  Projektleiter und Administrator (Entscheidung 004).
- Zusätzlich: Die als verantwortlich eingetragene Person mit aktiver Rolle Projektleiter oder
  Mitarbeiter darf den Status ihres eigenen Lieferobjekts setzen (Benutzerentscheidung 22.10.).

Schalter use_admin wie in apps.tasks.policies: so lässt sich bestimmen, ob eine Aktion nur
dank Administratorbefugnis erlaubt ist und als Administratoraktion zu kennzeichnen ist.
"""

from apps.projects import policies as project_policies
from apps.projects.models import ProjectRole

SCHREIBROLLEN = {ProjectRole.PROJEKTLEITER, ProjectRole.MITARBEITER}


def _active(user):
    return bool(user and user.is_authenticated and user.is_active)


def can_view(user, project):
    return project_policies.can_view_project(user, project)


def can_manage(user, project, *, use_admin=True):
    """Meilensteine, Lieferobjekte, Planversionen, Prognose/Ist und Freigaben ändern."""
    if not _active(user):
        return False
    if use_admin and user.is_admin:
        return True
    return ProjectRole.PROJEKTLEITER in project_policies.active_roles(user, project)


def can_set_deliverable_status(user, deliverable, *, use_admin=True):
    if not _active(user):
        return False
    if use_admin and user.is_admin:
        return True
    roles = project_policies.active_roles(user, deliverable.project)
    if ProjectRole.PROJEKTLEITER in roles:
        return True
    return deliverable.responsible_id == user.pk and bool(roles & SCHREIBROLLEN)


def can_be_responsible(user, project):
    """Verantwortlich kann nur ein aktiver Projektleiter oder Mitarbeiter sein."""
    return _active(user) and bool(project_policies.active_roles(user, project) & SCHREIBROLLEN)


def acts_as_admin(check, user, *args):
    """True, wenn die Aktion nur dank Administratorbefugnis erlaubt ist."""
    return bool(
        _active(user)
        and user.is_admin
        and check(user, *args)
        and not check(user, *args, use_admin=False)
    )
