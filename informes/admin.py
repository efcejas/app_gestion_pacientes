from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
	list_display = ('study_instance_uid', 'study_internal_id', 'autor', 'estado', 'creado', 'actualizado')
	list_filter = ('estado', 'autor', 'creado')
	search_fields = ('study_instance_uid', 'study_internal_id', 'accession_number')
	readonly_fields = ('creado', 'actualizado')
	ordering = ('-creado',)
