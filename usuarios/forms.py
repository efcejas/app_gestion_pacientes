from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from .models import Usuario
from django.contrib.auth.password_validation import password_validators_help_text_html
from django.contrib.auth import get_user_model

# Formulario para el registro de usuarios

class RegistroUsuarioForm(UserCreationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        help_text="Hasta 150 caracteres. Solo letras, números y los símbolos @ . + - _",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese un nombre de usuario único',
            'autofocus': True,
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',  # Clase de Bootstrap
            'placeholder': 'Ingrese su correo electrónico',  # Placeholder
        })
    )
    rol = forms.ChoiceField(
        choices=Usuario.ROLES, label="Rol",
        widget=forms.Select(attrs={
            'class': 'form-control',  # Clase de Bootstrap
        })
    )
    password1 = forms.CharField(
        label="Contraseña",
        help_text=password_validators_help_text_html(),  # 🔥 Esto incluye los requisitos
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
        })
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        help_text="Ingrese la misma contraseña para confirmar.",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su contraseña',
        })
    )

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
        
class RestablecerContrasenaForm(PasswordResetForm):
    email = forms.EmailField(
        label="",  # Etiqueta del campo
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su correo electrónico',
        })
    )

    class Meta:
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su correo electrónico'}),
        }

class RestablecerPasswordNuevaForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nueva contraseña'
        }),
        help_text=password_validators_help_text_html()
    )
    new_password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su nueva contraseña'
        })
    )
