from django.contrib import admin
from .models import Report, LogInforme



class LogInline(admin.TabularInline):
	model = LogInforme
	extra = 0
	readonly_fields = ('accion','usuario','timestamp','contenido_hash','pdf_hash','report_version','template_version','pdf_size')
	can_delete = False

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
	list_display = ('study_instance_uid', 'study_internal_id', 'version', 'autor', 'estado', 'creado', 'actualizado', 'tiene_pdf', 'firma_breve', 'hash_contenido_corto', 'hash_pdf_corto')
	list_filter = ('estado', 'autor', 'creado')
	search_fields = ('study_instance_uid', 'study_internal_id', 'accession_number')
	readonly_fields = ('creado', 'actualizado', 'pdf_file', 'contenido_hash', 'pdf_hash', 'version')
	inlines = [LogInline]
	# Acción de regenerar PDF eliminada tras estabilizar layout
	ordering = ('-creado',)

	def tiene_pdf(self, obj):
		return bool(obj.pdf_file)
	tiene_pdf.boolean = True
	tiene_pdf.short_description = 'PDF'

	def firma_breve(self, obj):
		return (obj.firma_digital[:12] + '…') if obj.firma_digital else ''
	firma_breve.short_description = 'Firma'

	def hash_contenido_corto(self, obj):
		return obj.contenido_hash[:10] + '…' if obj.contenido_hash else ''
	hash_contenido_corto.short_description = 'Hash Cont.'

	def hash_pdf_corto(self, obj):
		return obj.pdf_hash[:10] + '…' if obj.pdf_hash else ''
	hash_pdf_corto.short_description = 'Hash PDF'

@admin.register(LogInforme)
class LogInformeAdmin(admin.ModelAdmin):
	list_display = ('report','accion','usuario','timestamp','report_version','template_version','pdf_size')
	list_filter = ('accion','usuario','template_version')
	search_fields = ('report__study_internal_id','report__study_instance_uid','contenido_hash','pdf_hash')
	readonly_fields = ('report','accion','usuario','timestamp','contenido_hash','pdf_hash','report_version','template_version','pdf_size')

