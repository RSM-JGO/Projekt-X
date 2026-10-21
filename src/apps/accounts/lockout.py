"""Schutz gegen Passwortraten mit django-axes.

Zwei Sperren mit unterschiedlichen Grenzwerten:
- je normalisierter E-Mail-Adresse und IP-Adresse: AXES_FAILURE_LIMIT (5) Fehlversuche,
- je IP-Adresse allein (viele Adressen ausprobiert): LOGIN_IP_FAILURE_LIMIT (30) Fehlversuche,
jeweils innerhalb von AXES_COOLOFF_TIME (15 Minuten).

axes 8 vergleicht das Maximum über alle Sperrparameter mit einem einzigen Grenzwert. Ein
aufrufbarer AXES_FAILURE_LIMIT weiß nicht, welcher Parameter gerade geprüft wird. Deshalb
ergänzt ein eigener Handler die IP-Sperre auf Basis derselben axes-Tabelle.
"""

from axes.attempts import get_cool_off_threshold
from axes.conf import settings
from axes.handlers.database import AxesDatabaseHandler
from axes.models import AccessAttempt
from axes.signals import user_locked_out
from django.db.models import Sum

from .models import normalize_email


def lockout_username(request, credentials):
    """Zählt Fehlversuche je normalisierter E-Mail-Adresse.

    Ohne Normalisierung ließe sich die Sperre durch andere Groß-/Kleinschreibung umgehen.
    """
    value = None
    if credentials:
        value = credentials.get("username") or credentials.get("email")
    if not value and request is not None:
        value = request.POST.get("username")
    return normalize_email(value)


class LoginLockoutHandler(AxesDatabaseHandler):
    def ip_failures(self, request):
        ip_address = getattr(request, "axes_ip_address", None)
        if not ip_address:
            return 0
        total = AccessAttempt.objects.filter(
            ip_address=ip_address, attempt_time__gte=get_cool_off_threshold(request)
        ).aggregate(total=Sum("failures_since_start"))["total"]
        return total or 0

    def _ip_locked(self, request):
        return bool(
            settings.AXES_LOCK_OUT_AT_FAILURE
            and self.ip_failures(request) >= settings.LOGIN_IP_FAILURE_LIMIT
        )

    def is_locked(self, request, credentials=None):
        return super().is_locked(request, credentials) or self._ip_locked(request)

    def user_login_failed(self, sender, credentials, request=None, **kwargs):
        super().user_login_failed(sender, credentials, request=request, **kwargs)
        if request is None or getattr(request, "axes_locked_out", False):
            return
        if self._ip_locked(request):
            request.axes_locked_out = True
            request.axes_credentials = credentials
            user_locked_out.send(
                "axes",
                request=request,
                username=lockout_username(request, credentials),
                ip_address=request.axes_ip_address,
            )
