from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from . import services
from .models import User, normalize_email


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("email", "display_name")

    def clean_email(self):
        return normalize_email(self.cleaned_data.get("email"))


class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean_email(self):
        return normalize_email(self.cleaned_data.get("email"))

    def clean_is_active(self):
        is_active = self.cleaned_data.get("is_active")
        was_active = (
            self.instance.pk is not None
            and User.objects.filter(pk=self.instance.pk, is_active=True).exists()
        )
        if was_active and not is_active:
            services.ensure_can_deactivate(self.instance)
        return is_active


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Technische Kontoverwaltung über /admin (bis zur eigenen Administrationsoberfläche)."""

    form = UserEditForm
    add_form = UserCreationForm
    ordering = ("email",)
    list_display = ("email", "display_name", "is_active", "is_admin", "can_create_projects")
    list_filter = ("is_active", "is_admin", "can_create_projects", "is_staff")
    search_fields = ("email", "display_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Person", {"fields": ("display_name",)}),
        (
            "Fachliche Befugnisse",
            {"fields": ("is_active", "is_admin", "can_create_projects", "can_delete_projects")},
        ),
        (
            "Technischer Adminzugang",
            {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Zeitpunkte", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "display_name", "password1", "password2"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """In der Admin-Transaktion: Regel erneut mit Sperre prüfen, dann protokollieren."""
        old = None
        if change:
            stored = User.objects.select_for_update().get(pk=obj.pk)
            old = services.account_snapshot(stored)
            if stored.is_active and not obj.is_active:
                services.ensure_can_deactivate(obj, lock=True)
        super().save_model(request, obj, form, change)
        services.record_account_changes(actor=request.user, user=obj, old=old)
