from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.storage import default_storage
from django.conf import settings
from unittest.mock import patch
from informes.models import Report
import tempfile, os


User = get_user_model()


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test_media'))
class ReportFinalizeTests(TestCase):
	def setUp(self):
		self.client_dj = Client()
		self.user = User.objects.create_user(username='medico', password='pass', is_staff=True, email='m@x.test')
		self.client_dj.login(username='medico', password='pass')

	def tearDown(self):
		# Limpia media de pruebas
		media_root = settings.MEDIA_ROOT
		if os.path.exists(media_root):
			for root, dirs, files in os.walk(media_root, topdown=False):
				for f in files:
					try:
						os.remove(os.path.join(root, f))
					except Exception:
						pass
				for d in dirs:
					try:
						os.rmdir(os.path.join(root, d))
					except Exception:
						pass

	@patch('informes.views.client.get_study_shared_tags')
	def test_crear_y_finalizar_generando_pdf_y_hashes(self, mock_tags):
		"""Flujo completo: creación vía vista crear + finalizar en el mismo POST genera PDF, hashes y snapshot."""
		mock_tags.return_value = {
			'0020,000d': {'Value': '1.2.3.4.5'},
			'0010,0010': {'Value': 'PACIENTE^PRUEBA'},
			'0010,0020': {'Value': '12345678'},
			'0010,0030': {'Value': '19800115'},
			'0010,0040': {'Value': 'M'},
			'0008,1030': {'Value': 'RX TORAX'},
			'0008,0020': {'Value': '20250901'},
			'0008,0030': {'Value': '101010'},
			'0008,0050': {'Value': 'ACC123'},
		}
		url = reverse('informes:crear', args=['ORTHANC_STUDY_ID'])
		resp = self.client_dj.post(url, data={
			'contenido': '<p>Hallazgos normales</p>',
			'finalizar': '1'
		}, follow=True)
		self.assertEqual(resp.status_code, 200)
		report = Report.objects.first()
		self.assertIsNotNone(report)
		self.assertEqual(report.estado, Report.ESTADO_FINAL)
		self.assertTrue(report.pdf_file, 'Se esperaba pdf_file')
		self.assertTrue(report.contenido_hash and len(report.contenido_hash) == 64)
		self.assertTrue(report.pdf_hash and len(report.pdf_hash) == 64)
		self.assertTrue(report.study_snapshot)
		self.assertIn('patient_name', report.study_snapshot)

	def test_finalizar_con_error_orthanc_igualmente_finaliza(self):
		"""Si Orthanc falla al finalizar (ruta /finalizar), el informe debe quedar final y generar PDF/hash."""
		# Crear reporte manualmente (draft)
		report = Report.objects.create(
			study_internal_id='ORTHANC_FAIL',
			study_instance_uid='1.2.3.FAIL',
			autor=self.user,
			contenido='<p>Informe sin metadata</p>'
		)
		url = reverse('informes:finalizar', args=[report.id])
		with patch('informes.views.client.get_study_shared_tags', side_effect=Exception('Orthanc down')):
			resp = self.client_dj.post(url, data={})
		self.assertEqual(resp.status_code, 302)  # redirección post-finalizar
		report.refresh_from_db()
		self.assertEqual(report.estado, Report.ESTADO_FINAL)
		self.assertTrue(report.pdf_file, 'PDF debería existir aun con Orthanc caído')
		self.assertTrue(report.pdf_hash and len(report.pdf_hash) == 64)
		# snapshot puede estar vacío pero campo presente
		# si Orthanc falla, guardamos dict vacío
		self.assertIsNotNone(report.study_snapshot)

	@patch('informes.views.client.get_study_shared_tags')
	def test_sanitizacion_elimina_tags_peligrosos(self, mock_tags):
		"""Al crear/finalizar, debe eliminar <script>, eventos y etiquetas no permitidas como <img>."""
		mock_tags.return_value = {
			'0020,000d': {'Value': '1.2.3.4.5'},
			'0010,0010': {'Value': 'PACIENTE^PRUEBA'},
			'0010,0020': {'Value': '12345678'},
		}
		payload_html = "<script>alert('x')</script><p>Texto <strong>NEGRITA</strong> <img src=x onerror=alert(1)> <span style=\"color:red\" onclick=\"evil()\">Hola</span></p>"
		url = reverse('informes:crear', args=['ORTHANC_SAN'])
		resp = self.client_dj.post(url, data={'contenido': payload_html, 'finalizar': '1'}, follow=True)
		self.assertEqual(resp.status_code, 200)
		report = Report.objects.first()
		self.assertIsNotNone(report)
		# Verificaciones de sanitización
		self.assertNotIn('<script', report.contenido.lower())
		self.assertNotIn('onerror', report.contenido.lower())
		self.assertNotIn('onclick', report.contenido.lower())
		self.assertNotIn('<img', report.contenido.lower(), 'img debería eliminarse por no estar en whitelist')
		self.assertIn('<strong>negrita</strong>'.lower(), report.contenido.lower())
		self.assertIn('<span', report.contenido.lower())
		self.assertIn('style=', report.contenido.lower(), 'style debería permitirse en span')
		self.assertEqual(report.estado, Report.ESTADO_FINAL)

# Create your tests here.
