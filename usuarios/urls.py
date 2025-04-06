from django.urls import path
from .views import RegistroUsuarioView, HomeView
from django.contrib.auth import views as auth_views
from .forms import LoginForm, CambioContrasenaForm, RestablecerContrasenaForm, RestablecerPasswordNuevaForm

urlpatterns = [
    # Página principal
    path("", HomeView.as_view(), name="home"),
    
    # Rutas relacionadas con el registro de usuarios
    path("registro/", RegistroUsuarioView.as_view(), name="registro"),
    
    # Rutas relacionadas con la autenticación de usuarios
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="usuarios/login.html",
            authentication_form=LoginForm
        ),
        name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    
    # Rutas relacionadas con el cambio de contraseña
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="usuarios/password_change.html",
            form_class=CambioContrasenaForm
        ),
        name="password_change"
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="usuarios/password_change_done.html"
        ),
        name="password_change_done"
    ),
    
    # Rutas relacionadas con el restablecimiento de contraseña
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="usuarios/password_reset.html",
            form_class=RestablecerContrasenaForm,
            html_email_template_name="usuarios/password_reset_email.html",  # ✅ esta es la clave
            subject_template_name="usuarios/password_reset_subject.txt",  # opcional
        ),
        name="password_reset"
    ),

    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="usuarios/password_reset_done.html"
        ),
        name="password_reset_done"
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="usuarios/password_reset_confirm.html",
            form_class=RestablecerPasswordNuevaForm  # o podés usar la default
        ),
        name="password_reset_confirm"
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="usuarios/password_reset_complete.html"
        ),
        name="password_reset_complete"
    ),
]
