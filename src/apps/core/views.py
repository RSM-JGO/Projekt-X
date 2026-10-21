import logging

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def health(request):
    """Gesundheitsprüfung für Betrieb und Bereitstellung, ohne Projektdaten."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        database = "ok"
    except Exception:
        logger.exception("Gesundheitsprüfung: Datenbank nicht erreichbar")
        database = "error"
    status = 200 if database == "ok" else 503
    return JsonResponse(
        {"status": "ok" if status == 200 else "error", "database": database}, status=status
    )
