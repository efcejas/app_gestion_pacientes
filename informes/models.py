from django.db import models
from django.conf import settings


class Report(models.Model):
	ESTADO_DRAFT = 'draft'
	ESTADO_FINAL = 'final'
	ESTADOS = [
		(ESTADO_DRAFT, 'Borrador'),
		(ESTADO_FINAL, 'Final'),
	]

	# IDs clave
	study_internal_id = models.CharField(max_length=64, db_index=True, help_text='ID interno de Orthanc')
	study_instance_uid = models.CharField(max_length=128, help_text='Study Instance UID (0020,000D)')

	accession_number = models.CharField(max_length=64, blank=True, null=True)
	autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='reportes')
	contenido = models.TextField(blank=True)
	estado = models.CharField(max_length=16, choices=ESTADOS, default=ESTADO_DRAFT, db_index=True)
	creado = models.DateTimeField(auto_now_add=True)
	actualizado = models.DateTimeField(auto_now=True)
	pdf_file = models.FileField(upload_to='reportes_pdf/', blank=True, null=True, help_text='Versión PDF generada al finalizar')
	firma_digital = models.CharField(max_length=256, blank=True, help_text='Representación (demo) de la firma digital del autor')
	contenido_hash = models.CharField(max_length=64, blank=True, help_text='SHA256 del HTML final almacenado')
	pdf_hash = models.CharField(max_length=64, blank=True, help_text='SHA256 del archivo PDF generado')
	study_snapshot = models.JSONField(blank=True, null=True, help_text='Copia inmutable de datos paciente/estudio al finalizar')
	version = models.PositiveIntegerField(default=1, help_text='Número de versión secuencial para el mismo estudio_internal_id')

	class Meta:
		ordering = ['-creado']
		indexes = [
			models.Index(fields=['study_internal_id']),
			models.Index(fields=['estado']),
		]
		verbose_name = 'Informe'
		verbose_name_plural = 'Informes'
		constraints = [
			models.UniqueConstraint(fields=['study_internal_id', 'version'], name='uniq_report_by_internal_study_version')
		]

	def __str__(self):
		return f"Informe {self.study_instance_uid} ({self.estado})"

	@property
	def es_final(self):
		return self.estado == self.ESTADO_FINAL

	@property
	def puede_editar(self):
		return not self.es_final


class LogInforme(models.Model):
	report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='logs')
	accion = models.CharField(max_length=32, help_text='draft_save | finalize')
	usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
	timestamp = models.DateTimeField(auto_now_add=True)
	contenido_hash = models.CharField(max_length=64, blank=True)
	pdf_hash = models.CharField(max_length=64, blank=True)
	report_version = models.PositiveIntegerField(default=1)
	template_version = models.CharField(max_length=16, default='1.0.0')
	pdf_size = models.IntegerField(blank=True, null=True, help_text='Tamaño del PDF en bytes al momento del log')

	class Meta:
		ordering = ['-timestamp']
		verbose_name = 'Log de Informe'
		verbose_name_plural = 'Logs de Informes'

	def __str__(self):
		return f"LogInforme(report={self.report_id}, accion={self.accion}, ts={self.timestamp})"


class Adenda(models.Model):
	"""Adendas sobre un informe finalizado (append-only, no modifican el contenido original).
	Se ordenan cronológicamente y pueden regenerar el PDF combinando cuerpo + adendas.
	"""
	report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='adendas', db_index=True)
	autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='adendas_informes')
	contenido = models.TextField(help_text='Contenido de la adenda (HTML permitido básico).')
	creado = models.DateTimeField(auto_now_add=True)
	actualizado = models.DateTimeField(auto_now=True)
	visible = models.BooleanField(default=True, help_text='Permite ocultar una adenda sin eliminarla.')

	class Meta:
		ordering = ['creado']
		verbose_name = 'Adenda'
		verbose_name_plural = 'Adendas'
		indexes = [
			models.Index(fields=['report', 'creado']),
		]

	def __str__(self):
		return f"Adenda(report={self.report_id}, autor={self.autor_id}, creado={self.creado:%Y-%m-%d %H:%M})"
