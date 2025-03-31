from django.urls import path
from .views import RegistroUsuarioView, HomeView
from django.contrib.auth import views as auth_views
from .forms import LoginForm, CambioContrasenaForm

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    
    # Rutas relacionadas con el registro y authentication de usuarios
    path("registro/", RegistroUsuarioView.as_view(), name="registro"),
    path("login/", auth_views.LoginView.as_view(template_name="usuarios/login.html", authentication_form=LoginForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password_change/", auth_views.PasswordChangeView.as_view(template_name="usuarios/password_change.html", form_class=CambioContrasenaForm), name="password_change"),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(template_name="usuarios/password_change_done.html"), name="password_change_done"),
]
