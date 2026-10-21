from django.conf import settings


def environment(request):
    """Kennzeichnet die Entwicklungsumgebung dezent in der Oberfläche."""
    return {"is_dev_environment": settings.DEBUG}
