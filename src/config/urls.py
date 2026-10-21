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
    path("admin/", admin.site.urls),
]
