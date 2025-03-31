from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import Usuario
from django.contrib.auth.password_validation import password_validators_help_text_html
from django.contrib.auth import get_user_model

# Formulario para el registro de usuarios

class RegistroUsuarioForm(UserCreationForm):
    rol = forms.ChoiceField(choices=Usuario.ROLES, label="Rol")

    class Meta:
        model = Usuario
        fields = ["username", "email", "rol", "password1", "password2"]
        
# Formulario para la autenticación de usuarios

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="",  # No mostrar el label
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # Clase de Bootstrap
            'placeholder': 'Ingrese su usuario',  # Placeholder
            'autofocus': True,  # Enfocar automáticamente este campo
        })
    )
    password = forms.CharField(
        label="",  # No mostrar el label
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',  # Clase de Bootstrap
            'placeholder': 'Ingrese su contraseña',  # Placeholder
        })
    )

    class Meta:
        model = Usuario
        fields = ['username', 'password']

Usuario = get_user_model()

class CambioContrasenaForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña actual',
        })
    )

    new_password1 = forms.CharField(
        label="",
        help_text=password_validators_help_text_html(),  # HTML con <ul><li>...
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nueva contraseña',
        })
    )

    new_password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su nueva contraseña',
        })
    )

    class Meta:
        model = Usuario
        fields = ['old_password', 'new_password1', 'new_password2']