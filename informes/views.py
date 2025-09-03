from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.contrib import messages
from django.urls import reverse
from .models import Report, LogInforme
from .forms import ReportForm
from .pdf_utils import render_report_to_pdf
from django.conf import settings
from estudios.services import client
from functools import lru_cache


def staff_required(u):
	return u.is_authenticated and u.is_staff


@login_required
@user_passes_test(staff_required)
@transaction.atomic
def crear_o_editar(request, study_id=None, report_id=None):
	"""Crea (por study_id Orthanc) o edita un informe.
	Reglas:
	  - Solo staff (decorador) y solo autor puede editar.
	  - Informe final: solo lectura.
	  - get_or_create protegido por select_for_update para concurrencia.
	"""
	report = None
	shared = None
	viewer_url = None
	study_info = {}

	@lru_cache(maxsize=256)
	def shared_tags_cached(sid):
		return client.get_study_shared_tags(sid)

	def build_study_info(tags):
		if not tags:
			return {}
		def val(code):
			return (tags.get(code, {}) or {}).get('Value') or ''
		name_raw = val('0010,0010')
		patient_name = name_raw.replace('^', ' ').strip() if isinstance(name_raw, str) else name_raw
		return {
			'patient_name': patient_name,
			'patient_id': val('0010,0020'),
			'patient_sex': val('0010,0040'),
			'birth_date': val('0010,0030'),
			'study_description': val('0008,1030'),
			'study_date': val('0008,0020'),
			'study_time': val('0008,0030'),
			'accession_number': val('0008,0050'),
			' modalities': val('0008,0061'),
		}

	if report_id:
		report = get_object_or_404(Report.objects.select_for_update(), pk=report_id)
		study_id = report.study_internal_id
		try:
			shared = shared_tags_cached(study_id)
			uid_tmp = shared.get('0020,000d', {}).get('Value')
			if uid_tmp:
				viewer_url = f"{client.base_url}/ohif/viewer?StudyInstanceUIDs={uid_tmp}"
			study_info = build_study_info(shared)
		except Exception:
			pass
	else:
		try:
			tags = shared_tags_cached(study_id)
		except Exception as e:
			messages.error(request, f"Error obteniendo estudio: {e}")
			return redirect('estudios:lista_estudios')
		uid = tags.get('0020,000d', {}).get('Value') or ''
		accession = tags.get('0008,0050', {}).get('Value') or None
		shared = tags
		study_info = build_study_info(shared)
		if uid:
			viewer_url = f"{client.base_url}/ohif/viewer?StudyInstanceUIDs={uid}"
		if not uid:
			messages.error(request, 'No se pudo obtener el StudyInstanceUID.')
			return redirect('estudios:lista_estudios')
		# Buscamos el último reporte por study_internal_id
		qs = Report.objects.select_for_update().filter(study_internal_id=study_id).order_by('-version')
		last_report = qs.first()
		if last_report and last_report.es_final:
			# Creamos nueva versión (borrador) con version+1
			report = Report.objects.create(
				study_instance_uid=uid,
				study_internal_id=study_id,
				accession_number=accession,
				autor=request.user,
				version=last_report.version + 1
			)
		else:
			if last_report:
				report = last_report
			else:
				report = Report.objects.create(
					study_instance_uid=uid,
					study_internal_id=study_id,
					accession_number=accession,
					autor=request.user,
					version=1
				)

	# Permisos de autor
	if report and report.autor_id != request.user.id:
		messages.error(request, 'Solo el autor puede editar este informe.')
		return redirect('estudios:lista_estudios')

	if request.method == 'POST':
		form = ReportForm(request.POST, instance=report)
		if form.is_valid():
			form.instance.autor = report.autor  # evitar cambio
			# Sanitizar contenido HTML (baseline)
			try:
				import bleach
			except Exception:
				bleach = None
			if bleach:
				allowed_tags = ['p','br','strong','em','ul','ol','li','h1','h2','h3','h4','blockquote','span','u','sub','sup']
				allowed_attrs = {'span': ['style']}
				form.instance.contenido = bleach.clean(form.instance.contenido, tags=allowed_tags, attributes=allowed_attrs, strip=True)
			if report.es_final:
				messages.warning(request, 'Informe finalizado: no se puede modificar.')
				return redirect('informes:editar', report.id)
			form.save()
			# Log de guardado draft
			from django.conf import settings as _s
			LogInforme.objects.create(
				report=form.instance,
				accion='draft_save',
				usuario=request.user,
				contenido_hash=form.instance.contenido_hash or '',
				pdf_hash=form.instance.pdf_hash or '',
				report_version=form.instance.version,
				template_version=getattr(_s, 'REPORT_TEMPLATE_VERSION', '1.0.0')
			)
			if 'finalizar' in request.POST:
				if not form.instance.contenido.strip():
					messages.error(request, 'No podés finalizar un informe vacío.')
				else:
					form.instance.estado = Report.ESTADO_FINAL
					form.instance.save(update_fields=['estado'])
					# Hash contenido y firma demo (si falta)
					import hashlib
					content_bytes = form.instance.contenido.encode('utf-8', errors='ignore')
					form.instance.contenido_hash = hashlib.sha256(content_bytes).hexdigest()
					updates = ['estado', 'contenido_hash']
					if not form.instance.firma_digital:
						payload = (form.instance.contenido + form.instance.autor.username).encode('utf-8', errors='ignore')
						hexhash = hashlib.sha256(payload).hexdigest()[:32]
						form.instance.firma_digital = f"FD-{hexhash}"  # demo
						updates.append('firma_digital')
					form.instance.save(update_fields=updates)
					# Log finalize (pre PDF hash)
					from django.conf import settings as _s2
					LogInforme.objects.create(
						report=form.instance,
						accion='finalize',
						usuario=request.user,
						contenido_hash=form.instance.contenido_hash,
						pdf_hash='',
						report_version=form.instance.version,
						template_version=getattr(_s2, 'REPORT_TEMPLATE_VERSION', '1.0.0')
					)
					# Guardar snapshot inmutable si no existe
					if not form.instance.study_snapshot:
						form.instance.study_snapshot = study_info
						form.instance.save(update_fields=['study_snapshot'])
					# Generar PDF (usa snapshot para consistencia)
					pdf_context = {'study_info': form.instance.study_snapshot or study_info}
					success, content_file, err = render_report_to_pdf(form.instance, context_extra=pdf_context)
					if success:
						filename = f"reporte_{form.instance.id}.pdf"
						# Leer bytes ANTES de guardar (Django consume el file al guardar)
						pdf_bytes = content_file.read()
						import hashlib as _hashlib
						form.instance.pdf_hash = _hashlib.sha256(pdf_bytes).hexdigest() if pdf_bytes else ''
						from django.core.files.base import ContentFile as _CF
						form.instance.pdf_file.save(filename, _CF(pdf_bytes), save=True)
						form.instance.save(update_fields=['pdf_hash'])
						messages.success(request, 'Informe finalizado y PDF generado.')
					else:
						messages.warning(request, f'Informe finalizado, pero falló la generación del PDF: {err}')
					return redirect('informes:ver_final', form.instance.id)
			messages.success(request, 'Borrador guardado.')
			return redirect(reverse('informes:editar', args=[report.id]))
	else:
		form = ReportForm(instance=report)

	# Readonly si finalizado
	if report and report.es_final:
		form.fields['contenido'].widget.attrs['readonly'] = True

	return render(request, 'informes/editar.html', {
		'form': form,
		'report': report,
		'study_id': study_id,
		'shared': shared,
		'viewer_url': viewer_url,
		'study_info': study_info,
	})


@login_required
@user_passes_test(staff_required)
@transaction.atomic
def finalizar(request, report_id: int):
	report = get_object_or_404(Report, pk=report_id)
	if request.method != 'POST':
		return redirect('informes:editar', report_id)
	if report.es_final:
		messages.info(request, 'El informe ya estaba finalizado.')
		return redirect('informes:editar', report_id)
	if not report.contenido.strip():
		messages.error(request, 'No podés finalizar un informe vacío.')
		return redirect('informes:editar', report_id)
	# Sanitizar antes de congelar
	try:
		import bleach
	except Exception:
		bleach = None
	if bleach:
		allowed_tags = ['p','br','strong','em','ul','ol','li','h1','h2','h3','h4','blockquote','span','u','sub','sup']
		allowed_attrs = {'span': ['style']}
		report.contenido = bleach.clean(report.contenido, tags=allowed_tags, attributes=allowed_attrs, strip=True)
		report.save(update_fields=['contenido'])
	report.estado = Report.ESTADO_FINAL
	report.save(update_fields=['estado'])
	# Hash contenido y firma demo si falta
	import hashlib
	content_bytes = report.contenido.encode('utf-8', errors='ignore')
	report.contenido_hash = hashlib.sha256(content_bytes).hexdigest()
	updates = ['estado', 'contenido_hash']
	if not report.firma_digital:
		payload = (report.contenido + report.autor.username).encode('utf-8', errors='ignore')
		report.firma_digital = 'FD-' + hashlib.sha256(payload).hexdigest()[:32]
		updates.append('firma_digital')
	report.save(update_fields=updates)
	# Obtener snapshot (si no existe, construir y guardar ahora)
	if not report.study_snapshot:
		try:
			shared = client.get_study_shared_tags(report.study_internal_id)
			def val(code):
				return (shared.get(code, {}) or {}).get('Value') or ''
			name_raw = val('0010,0010')
			patient_name = name_raw.replace('^', ' ').strip() if isinstance(name_raw, str) else name_raw
			report.study_snapshot = {
				'patient_name': patient_name,
				'patient_id': val('0010,0020'),
				'patient_sex': val('0010,0040'),
				'birth_date': val('0010,0030'),
				'study_description': val('0008,1030'),
				'study_date': val('0008,0020'),
				'study_time': val('0008,0030'),
				'accession_number': val('0008,0050'),
			}
			report.save(update_fields=['study_snapshot'])
		except Exception:
			report.study_snapshot = {}
	success, content_file, err = render_report_to_pdf(report, context_extra={'study_info': report.study_snapshot})
	if success:
		filename = f"reporte_{report.id}.pdf"
		# Leer bytes antes de guardar
		pdf_bytes = content_file.read()
		report.pdf_hash = hashlib.sha256(pdf_bytes).hexdigest() if pdf_bytes else ''
		from django.core.files.base import ContentFile as _CF
		report.pdf_file.save(filename, _CF(pdf_bytes), save=True)
		report.save(update_fields=['pdf_hash'])
		# Log PDF hash (actualizar log finalize más reciente de este report agregando pdf_hash y pdf_size)
		last_finalize = report.logs.filter(accion='finalize').order_by('-timestamp').first()
		if last_finalize:
			last_finalize.pdf_hash = report.pdf_hash
			last_finalize.pdf_size = len(pdf_bytes) if pdf_bytes else 0
			last_finalize.save(update_fields=['pdf_hash','pdf_size'])
		messages.success(request, 'Informe finalizado y PDF generado.')
	else:
		messages.warning(request, f'Informe finalizado, pero falló la generación del PDF: {err}')
	return redirect('estudios:lista_estudios')


@login_required
@user_passes_test(staff_required)
def ver_final(request, report_id: int):
	report = get_object_or_404(Report, pk=report_id, estado=Report.ESTADO_FINAL)
	# Mostrar siempre snapshot (no volver a pedir a Orthanc salvo para viewer URL)
	study_info = report.study_snapshot or {}
	viewer_url = None
	try:
		shared = client.get_study_shared_tags(report.study_internal_id)
		uid = (shared.get('0020,000d', {}) or {}).get('Value')
		if uid:
			viewer_url = f"{client.base_url}/ohif/viewer?StudyInstanceUIDs={uid}"
	except Exception:
		pass
	return render(request, 'informes/ver_final.html', {
		'report': report,
		'shared': shared,
		'viewer_url': viewer_url,
		'study_info': study_info,
	})


