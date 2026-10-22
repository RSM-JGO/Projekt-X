from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="list"),
    path("neu/", views.project_create, name="create"),
    path("<uuid:public_id>/", views.project_detail, name="detail"),
    path("<uuid:public_id>/bearbeiten/", views.project_edit, name="edit"),
    path("<uuid:public_id>/team/", views.team, name="team"),
    path("<uuid:public_id>/mitglieder/neu/", views.member_add, name="member_add"),
    path(
        "<uuid:public_id>/mitglieder/<int:membership_id>/rollen/",
        views.member_roles,
        name="member_roles",
    ),
    path(
        "<uuid:public_id>/mitglieder/<int:membership_id>/entfernen/",
        views.member_remove,
        name="member_remove",
    ),
]
