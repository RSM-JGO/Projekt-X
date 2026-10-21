from .models import AuditLog


def record(*, actor, action, obj, project=None, old=None, new=None, as_admin=False):
    """Schreibt einen Protokolleintrag. Aufruf innerhalb der Transaktion der Änderung."""
    return AuditLog.objects.create(
        actor=actor,
        actor_label=f"{actor.display_name} <{actor.email}>",
        action=action,
        object_type=obj._meta.label,
        object_id=str(obj.pk),
        project=project,
        as_admin=as_admin,
        old_values=old,
        new_values=new,
    )
