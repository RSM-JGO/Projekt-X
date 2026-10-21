from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("arbeitsplatz/", views.workplace, name="workplace"),
    path("arbeitsplatz/aufgabe-neu/", views.personal_task_create, name="personal_create"),
    path("projekte/<uuid:public_id>/aufgaben/neu/", views.project_task_create, name="create"),
    path("projekte/<uuid:public_id>/buckets/", views.buckets, name="buckets"),
    path(
        "projekte/<uuid:public_id>/buckets/<int:bucket_id>/",
        views.bucket_update,
        name="bucket_update",
    ),
    path("aufgaben/<uuid:public_id>/", views.task_detail, name="detail"),
    path("aufgaben/<uuid:public_id>/bearbeiten/", views.task_edit, name="edit"),
    path("aufgaben/<uuid:public_id>/abschliessen/", views.task_complete, name="complete"),
    path("aufgaben/<uuid:public_id>/wiedereroeffnen/", views.task_reopen, name="reopen"),
]
