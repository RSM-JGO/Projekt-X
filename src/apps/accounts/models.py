from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Eigenes Benutzermodell. Fachliche Felder (z. B. Befugnisse) folgen mit dem Rechtemodell."""

    class Meta:
        verbose_name = "Benutzer"
        verbose_name_plural = "Benutzer"

    def __str__(self):
        return self.get_full_name() or self.username
