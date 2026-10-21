from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from apps.core.views import health

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="projects:list"), name="home"),
    path("health/", health, name="health"),
    path("", include("apps.accounts.urls")),
    path("projekte/", include("apps.projects.urls")),
    path("", include("apps.tasks.urls")),
]

# Technische Oberfläche /admin nur in der Entwicklung; in Demo und Prod nicht geroutet
if settings.PX_INSTANCE == "dev":
    urlpatterns.append(path("admin/", admin.site.urls))
