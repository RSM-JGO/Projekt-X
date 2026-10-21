from django.contrib import admin

from .models import Project, ProjectMembership, ProjectRoleAssignment


class ReadOnlyAdmin(admin.ModelAdmin):
    """Nur Ansicht. Änderungen laufen über die Anwendung, damit Regeln und Protokoll greifen."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Project)
class ProjectAdmin(ReadOnlyAdmin):
    list_display = ("name", "start_date", "end_date", "created_by", "created_at")
    search_fields = ("name",)


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(ReadOnlyAdmin):
    list_display = ("project", "user", "started_at", "ended_at")


@admin.register(ProjectRoleAssignment)
class ProjectRoleAssignmentAdmin(ReadOnlyAdmin):
    list_display = ("membership", "role", "assigned_by", "assigned_at", "ended_at")
