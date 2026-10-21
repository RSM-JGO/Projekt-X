from django.contrib.auth import views as auth_views

from .forms import EmailAuthenticationForm


class LoginView(auth_views.LoginView):
    template_name = "accounts/anmelden.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    """Abmelden nur per POST (Django 5 lehnt GET mit 405 ab). Die Sitzung wird gelöscht."""
