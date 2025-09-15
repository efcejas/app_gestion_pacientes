from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Usuario(AbstractUser):
    ADMINISTRATIVO = "administrativo"
    MEDICO = "medico"

    ROLES = [
        (ADMINISTRATIVO, "Administrativo"),
        (MEDICO, "Médico"),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default=ADMINISTRATIVO)
    signature_image = models.ImageField(upload_to='firmas_medicos/', blank=True, null=True, help_text='PNG con fondo transparente recomendado')

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"

