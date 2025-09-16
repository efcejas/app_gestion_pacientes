from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views

from .views import (
    RegistroConfirmacionView,
    RegistroUsuarioView,
    HomeView,
    PerfilDetalleView,
)
from .forms import (
    LoginForm,
    CambioContrasenaForm,
    RestablecerContrasenaForm,
    RestablecerPasswordNuevaForm,
)

urlpatterns = [
    # Página principal
    path("", HomeView.as_view(), name="home"),

    # Registro
    path("registro/", RegistroUsuarioView.as_view(), name="registro"),
    path("registro/confirmacion/", RegistroConfirmacionView.as_view(), name="registro_confirmacion"),

    # Autenticación
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="usuarios/login.html",
            authentication_form=LoginForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Perfil (solo lectura siempre disponible)
    path("perfil/", PerfilDetalleView.as_view(), name="perfil"),

    # Cambio de contraseña
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="usuarios/password_change.html",
            form_class=CambioContrasenaForm,
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="usuarios/password_change_done.html",
        ),
        name="password_change_done",
    ),

    # Reset de contraseña
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="usuarios/password_reset.html",
            form_class=RestablecerContrasenaForm,
            html_email_template_name="usuarios/password_reset_email.html",
            subject_template_name="usuarios/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="usuarios/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="usuarios/password_reset_confirm.html",
            form_class=RestablecerPasswordNuevaForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="usuarios/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]

# Edición de perfil: solo si el flag está habilitado
if getattr(settings, "FEATURE_PERFIL_EDICION", False):
    from .views import PerfilEditarView

    urlpatterns += [
        path("perfil/editar/", PerfilEditarView.as_view(), name="perfil_editar"),
    ]
