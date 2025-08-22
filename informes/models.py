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
	study_instance_uid = models.CharField(max_length=128, unique=True, help_text='Study Instance UID (0020,000D)')

	accession_number = models.CharField(max_length=64, blank=True, null=True)
	autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='reportes')
	contenido = models.TextField(blank=True)
	estado = models.CharField(max_length=16, choices=ESTADOS, default=ESTADO_DRAFT, db_index=True)
	creado = models.DateTimeField(auto_now_add=True)
	actualizado = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-creado']
		indexes = [
			models.Index(fields=['study_internal_id']),
			models.Index(fields=['estado']),
		]
		verbose_name = 'Informe'
		verbose_name_plural = 'Informes'
		constraints = [
			models.UniqueConstraint(fields=['study_internal_id'], name='uniq_report_by_internal_study')
		]

	def __str__(self):
		return f"Informe {self.study_instance_uid} ({self.estado})"

	@property
	def es_final(self):
		return self.estado == self.ESTADO_FINAL

	@property
	def puede_editar(self):
		return not self.es_final
