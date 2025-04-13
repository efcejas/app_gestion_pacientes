# usuarios/admin.py o donde esté registrado tu modelo
from django.contrib import admin
from .models import OrdenMedica

@admin.register(OrdenMedica)
class OrdenMedicaAdmin(admin.ModelAdmin):
    list_display = (
        'identificador_paciente',
        'medico',
        'fecha_emision',
        'dias_validez',
        'fecha_vencimiento',
    )
    list_filter = ('dias_validez', 'fecha_emision', 'medico')
    search_fields = ('identificador_paciente', 'medico__username')
    ordering = ('-fecha_emision',)
    verbose_name = "Orden Médica"
    verbose_name_plural = "Órdenes Médicas"

    def fecha_vencimiento(self, obj):
        return obj.fecha_vencimiento()
    fecha_vencimiento.short_description = 'Vence el'
    
    
