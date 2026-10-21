from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("anmelden/", views.LoginView.as_view(), name="login"),
    path("abmelden/", views.LogoutView.as_view(), name="logout"),
]
