from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.contrib import messages
from django.urls import reverse
from .models import Report
from .forms import ReportForm
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
		report, created = Report.objects.select_for_update().get_or_create(
			study_instance_uid=uid,
			defaults={
				'study_internal_id': study_id,
				'accession_number': accession,
				'autor': request.user,
			}
		)
		if not created and report.es_final:
			messages.info(request, 'El informe ya está finalizado.')
			return redirect('estudios:lista_estudios')

	# Permisos de autor
	if report and report.autor_id != request.user.id:
		messages.error(request, 'Solo el autor puede editar este informe.')
		return redirect('estudios:lista_estudios')

	if request.method == 'POST':
		form = ReportForm(request.POST, instance=report)
		if form.is_valid():
			form.instance.autor = report.autor  # evitar cambio
			if report.es_final:
				messages.warning(request, 'Informe finalizado: no se puede modificar.')
				return redirect('informes:editar', report.id)
			form.save()
			if 'finalizar' in request.POST:
				if not form.instance.contenido.strip():
					messages.error(request, 'No podés finalizar un informe vacío.')
				else:
					form.instance.estado = Report.ESTADO_FINAL
					form.instance.save(update_fields=['estado'])
					messages.success(request, 'Informe finalizado.')
					return redirect('estudios:lista_estudios')
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
	report.estado = Report.ESTADO_FINAL
	report.save(update_fields=['estado'])
	messages.success(request, 'Informe finalizado.')
	return redirect('estudios:lista_estudios')


@login_required
@user_passes_test(staff_required)
def ver_final(request, report_id: int):
	report = get_object_or_404(Report, pk=report_id, estado=Report.ESTADO_FINAL)
	# Obtener tags para mostrar cabecera
	shared = None
	study_info = {}
	viewer_url = None
	try:
		shared = client.get_study_shared_tags(report.study_internal_id)
		def val(code):
			return (shared.get(code, {}) or {}).get('Value') or ''
		name_raw = val('0010,0010')
		patient_name = name_raw.replace('^', ' ').strip() if isinstance(name_raw, str) else name_raw
		uid = val('0020,000d')
		if uid:
			viewer_url = f"{client.base_url}/ohif/viewer?StudyInstanceUIDs={uid}"
		study_info = {
			'patient_name': patient_name,
			'patient_id': val('0010,0020'),
			'accession_number': val('0008,0050'),
			'study_description': val('0008,1030'),
			'study_date': val('0008,0020'),
			'study_time': val('0008,0030'),
		}
	except Exception:
		pass
	return render(request, 'informes/ver_final.html', {
		'report': report,
		'shared': shared,
		'viewer_url': viewer_url,
		'study_info': study_info,
	})
