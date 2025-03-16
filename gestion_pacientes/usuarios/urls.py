from django.urls import path
from .views import RegistroUsuarioView, HomeView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("registro/", RegistroUsuarioView.as_view(), name="registro"),
    path("login/", auth_views.LoginView.as_view(template_name="usuarios/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", HomeView.as_view(), name="home"),
]
