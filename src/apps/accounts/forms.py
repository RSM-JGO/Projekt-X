from django import forms
from django.contrib.auth.forms import AuthenticationForm

# Bewusst eine einzige Meldung für unbekanntes Konto, falsches Passwort und
# deaktiviertes Konto, damit die Existenz eines Kontos nicht erkennbar ist.
LOGIN_FEHLER = "E-Mail-Adresse oder Passwort ist nicht korrekt."


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="E-Mail-Adresse",
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Passwort",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "data-password-toggle": ""}
        ),
    )

    error_messages = {
        "invalid_login": LOGIN_FEHLER,
        "inactive": LOGIN_FEHLER,
    }

    def clean(self):
        try:
            return super().clean()
        except forms.ValidationError:
            # Auch formale Fehler nicht weiter aufschlüsseln
            raise forms.ValidationError(LOGIN_FEHLER, code="invalid_login") from None
