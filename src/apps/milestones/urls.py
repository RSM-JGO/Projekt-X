from django.urls import path

from . import views

app_name = "milestones"

# Eingebunden unter projekte/<uuid:public_id>/ (config/urls.py)
urlpatterns = [
    path("termine/", views.schedule, name="schedule"),
    path("termine/zeitraum/aendern/", views.date_change, name="period_change"),
    path("termine/plan/neu/", views.plan_create, name="plan_create"),
    path("termine/plan/<int:number>/", views.plan_detail, name="plan"),
    path("termine/plan/<int:number>/genehmigen/", views.plan_approve, name="plan_approve"),
    path("meilensteine/neu/", views.milestone_add, name="add"),
    path("meilensteine/<uuid:ms_id>/", views.milestone_detail, name="detail"),
    path(
        "meilensteine/<uuid:ms_id>/sichtbarkeit/",
        views.milestone_visibility,
        name="visibility",
    ),
    path("meilensteine/<uuid:ms_id>/termin/", views.date_change, name="date_change"),
    path("meilensteine/<uuid:ms_id>/freigabe/", views.approval_create, name="approve"),
    path(
        "meilensteine/<uuid:ms_id>/lieferobjekte/neu/",
        views.deliverable_add,
        name="deliverable_add",
    ),
    path("lieferobjekte/<uuid:d_id>/bearbeiten/", views.deliverable_edit, name="deliverable_edit"),
    path("lieferobjekte/<uuid:d_id>/status/", views.deliverable_status, name="deliverable_status"),
]
