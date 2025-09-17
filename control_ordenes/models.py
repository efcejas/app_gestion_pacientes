# Import necessary modules for Django models
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string

# Import additional utilities
from datetime import date, timedelta

class OrdenMedica(models.Model):
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'medico'},
        related_name='ordenes_emitidas'
    )
    identificador_paciente = models.CharField(
        max_length=50,
        verbose_name="Identificador encriptado del paciente"
    )
    fecha_emision = models.DateField(default=timezone.now)
    dias_validez = models.IntegerField(
        choices=[(30, '30 días'), (60, '60 días'), (90, '90 días')],
        default=90,
        verbose_name="Válido por"
    )
    renovada = models.BooleanField(default=False, verbose_name="¿Renovada?")
    # Auditoría simple / última actividad
    last_action = models.CharField(
        max_length=20,
        blank=True,
        default="",
        choices=[
            ("creada", "Creada"),
            ("renovada", "Renovada"),
            ("editada", "Editada"),
        ],
        verbose_name="Última acción",
    )
    last_action_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha última acción")
    last_actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_operadas',
        verbose_name="Último operador",
    )

    def fecha_vencimiento(self):
        return self.fecha_emision + timedelta(days=self.dias_validez)
    
    @property
    def dias_restantes(self):
        return (self.fecha_vencimiento() - date.today()).days
    
    class Meta:
        verbose_name = "Orden Médica"
        verbose_name_plural = "Órdenes Médicas"
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"Orden de {self.medico} - ID {self.identificador_paciente}"
