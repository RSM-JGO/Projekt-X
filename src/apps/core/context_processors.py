from django.conf import settings

from .version import version_label, version_tooltip


def environment(request):
    """Kennzeichnet die Entwicklungsumgebung dezent; Versionsanzeige nur für Angemeldete."""
    user = getattr(request, "user", None)
    angemeldet = bool(user and user.is_authenticated)
    return {
        "is_dev_environment": settings.DEBUG,
        "version_label": version_label() if angemeldet else "",
        "version_tooltip": version_tooltip() if angemeldet else "",
    }
