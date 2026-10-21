from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


def normalize_email(email):
    """E-Mail-Adressen werden vollständig klein und ohne Leerraum gespeichert."""
    return (email or "").strip().lower()


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_by_natural_key(self, username):
        # Anmeldung unabhängig von Groß-/Kleinschreibung
        return self.get(email=normalize_email(username))

    def _create_user(self, email, password, **extra_fields):
        email = normalize_email(email)
        if not email:
            raise ValueError("Die E-Mail-Adresse ist Pflicht.")
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # ohne Passwort: nicht nutzbares Passwort
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Technisches Konto für /admin. Der fachliche Administrator ist is_admin."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            raise ValueError("Ein Superuser braucht is_staff=True und is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Benutzerkonto mit Anmeldung per E-Mail-Adresse.

    Befugnisse sind getrennt vom Django-Adminzugang (is_staff/is_superuser):
    - is_admin: fachlicher Administrator (liest alle Projekte, verwaltet Mitgliedschaften)
    - can_create_projects: darf neue Projekte anlegen (kein Zugriff auf bestehende)
    - can_delete_projects: nur Datenmodell; Löschen folgt später
    """

    email = models.EmailField("E-Mail-Adresse", max_length=254, unique=True)
    display_name = models.CharField("Anzeigename", max_length=150)
    is_active = models.BooleanField("aktiv", default=True)
    is_staff = models.BooleanField("Zugang zu /admin", default=False)
    is_admin = models.BooleanField("Administrator", default=False)
    can_create_projects = models.BooleanField("darf Projekte anlegen", default=False)
    can_delete_projects = models.BooleanField("darf Projekte löschen", default=False)
    date_joined = models.DateTimeField("angelegt am", default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["display_name"]

    class Meta:
        verbose_name = "Benutzer"
        verbose_name_plural = "Benutzer"
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="accounts_user_email_ci_unique",
                violation_error_message="Diese E-Mail-Adresse ist bereits vergeben.",
            ),
        ]

    def clean(self):
        super().clean()
        self.email = normalize_email(self.email)

    def save(self, *args, **kwargs):
        self.email = normalize_email(self.email)
        super().save(*args, **kwargs)

    def get_full_name(self):
        return self.display_name

    def get_short_name(self):
        return self.display_name

    def __str__(self):
        return self.display_name or self.email
