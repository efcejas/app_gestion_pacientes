from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
	list_display = ('study_instance_uid', 'study_internal_id', 'autor', 'estado', 'creado', 'actualizado', 'tiene_pdf', 'firma_breve')
	list_filter = ('estado', 'autor', 'creado')
	search_fields = ('study_instance_uid', 'study_internal_id', 'accession_number')
	readonly_fields = ('creado', 'actualizado', 'pdf_file')
	# Acción de regenerar PDF eliminada tras estabilizar layout
	ordering = ('-creado',)

	def tiene_pdf(self, obj):
		return bool(obj.pdf_file)
	tiene_pdf.boolean = True
	tiene_pdf.short_description = 'PDF'

	def firma_breve(self, obj):
		return (obj.firma_digital[:12] + '…') if obj.firma_digital else ''
	firma_breve.short_description = 'Firma'

