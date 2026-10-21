import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import normalize_email


class Command(BaseCommand):
    help = "Legt ein Konto mit fachlicher Administratorrolle (is_admin) an."

    def add_arguments(self, parser):
        parser.add_argument("--email", help="E-Mail-Adresse (sonst Abfrage)")
        parser.add_argument("--name", help="Anzeigename (sonst Abfrage)")
        parser.add_argument(
            "--mit-django-admin",
            action="store_true",
            help="Zusätzlich Zugang zur technischen Oberfläche /admin (is_staff, is_superuser)",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        email = normalize_email(options["email"] or input("E-Mail-Adresse: "))
        if not email:
            raise CommandError("Die E-Mail-Adresse ist Pflicht.")
        if User.objects.filter(email=email).exists():
            raise CommandError("Für diese E-Mail-Adresse gibt es bereits ein Konto.")
        name = (options["name"] or input("Anzeigename: ")).strip()
        if not name:
            raise CommandError("Der Anzeigename ist Pflicht.")

        password = getpass.getpass("Passwort: ")
        if password != getpass.getpass("Passwort wiederholen: "):
            raise CommandError("Die Passwörter stimmen nicht überein.")
        probe = User(email=email, display_name=name)
        try:
            validate_password(password, user=probe)
        except ValidationError as exc:
            raise CommandError(" ".join(exc.messages)) from None

        technisch = options["mit_django_admin"]
        User.objects.create_user(
            email=email,
            password=password,
            display_name=name,
            is_admin=True,
            is_staff=technisch,
            is_superuser=technisch,
        )
        self.stdout.write(self.style.SUCCESS(f"Administrator {email} angelegt."))
