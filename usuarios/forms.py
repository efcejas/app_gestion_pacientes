from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from .models import Usuario
from django.contrib.auth.password_validation import password_validators_help_text_html
from django.contrib.auth import get_user_model
from .widgets import TailwindClearableFileInput

# Formulario para el registro de usuarios

class RegistroUsuarioForm(UserCreationForm):
    username = forms.CharField(
        label="Nombre de usuario",
        help_text="Hasta 150 caracteres. Solo letras, números y los símbolos @ . + - _",
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese un nombre de usuario único',
            'autofocus': True,
            'autocomplete': 'username'
        })
    )
    
    first_name = forms.CharField(
        label="Nombre",
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese su nombre',
        })
    )
    
    last_name = forms.CharField(
        label="Apellido",
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese su apellido',
        })
    )
    
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ingrese su correo electrónico',
        })
    )
    rol = forms.ChoiceField(
        choices=Usuario.ROLES, label="Rol",
        widget=forms.Select(attrs={
            # clases aplicadas en templates via add_class
        })
    )
    password1 = forms.CharField(
        label="Contraseña",
        help_text=password_validators_help_text_html(),  # 🔥 Esto incluye los requisitos
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingrese su contraseña',
        })
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        help_text="Ingrese la misma contraseña para confirmar.",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirme su contraseña',
        })
    )

    class Meta:
        model = Usuario
        fields = ["username", "first_name", "last_name", "email", "rol", "password1", "password2"]
        
# Formulario para la autenticación de usuarios

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="",  # No mostrar el label
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese su usuario',  # Placeholder
            'autofocus': True,  # Enfocar automáticamente este campo
        })
    )
    password = forms.CharField(
        label="",  # No mostrar el label
        widget=forms.PasswordInput(attrs={
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
            'placeholder': 'Ingrese su contraseña actual',
        })
    )

    new_password1 = forms.CharField(
        label="",
        help_text=password_validators_help_text_html(),  # HTML con <ul><li>...
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingrese su nueva contraseña',
        })
    )

    new_password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
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
            'placeholder': 'Ingrese su correo electrónico',
        })
    )

    class Meta:
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Ingrese su correo electrónico'}),
        }

class RestablecerPasswordNuevaForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingrese su nueva contraseña'
        }),
        help_text=password_validators_help_text_html()
    )
    new_password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirme su nueva contraseña'
        })
    )

class FirmaMedicoForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['signature_image']
        widgets = {
            'signature_image': forms.ClearableFileInput(attrs={
                'accept': 'image/png,image/jpeg',
            })
        }
    def clean_signature_image(self):
        f = self.cleaned_data.get('signature_image')
        if not f:
            return f
        if f.size > 2 * 1024 * 1024:
            raise forms.ValidationError('La imagen no puede superar 2MB.')
        import os
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg']:
            raise forms.ValidationError('Formato no soportado. Usa PNG o JPG.')
        return f

class UsuarioPerfilForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email", "signature_image"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "placeholder": "Nombre",
                "class": "w-full rounded border border-gray-300 text-gray-800 dark:text-gray-100 placeholder-gray-400 leading-relaxed tracking-wide focus:border-blue-500 focus:ring-blue-500 text-sm bg-white dark:bg-gray-900",
            }),
            "last_name": forms.TextInput(attrs={
                "placeholder": "Apellido",
                "class": "w-full rounded border border-gray-300 text-gray-800 dark:text-gray-100 placeholder-gray-400 leading-relaxed tracking-wide focus:border-blue-500 focus:ring-blue-500 text-sm bg-white dark:bg-gray-900",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Correo",
                "class": "w-full rounded border border-gray-300 text-gray-800 dark:text-gray-100 placeholder-gray-400 leading-relaxed tracking-wide focus:border-blue-500 focus:ring-blue-500 text-sm bg-white dark:bg-gray-900",
            }),
            "signature_image": TailwindClearableFileInput(attrs={
                "id": "file_input",
                "accept": "image/png,image/jpeg",
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Etiquetas amigables
        self.fields["first_name"].label = "Nombre"
        self.fields["last_name"].label = "Apellido"
        self.fields["email"].label = "Correo"
        # Ayuda para el archivo acorde a validaciones
        self.fields["signature_image"].help_text = "PNG o JPG (máx. 2 MB). Recomendado: fondo transparente."
    def clean_signature_image(self):
        f = self.cleaned_data.get('signature_image')
        if not f:
            return f
        if f.size > 2 * 1024 * 1024:
            raise forms.ValidationError('La imagen no puede superar 2MB.')
        import os
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg']:
            raise forms.ValidationError('Formato no soportado. Usa PNG o JPG.')
        return f
