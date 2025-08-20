from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .services import client

@login_required
def lista_estudios(request):
    studies_ids = client.list_studies()
    studies = []

    def norm_name(v: str) -> str:
        # "APELLIDO^NOMBRE" -> "APELLIDO NOMBRE"
        return (v or "").replace("^", " ").strip()

    def short_modality(v):
        # "MR\SR" -> "MR" ; si ya es lista, toma el primero
        if isinstance(v, list) and v:
            return v[0]
        if isinstance(v, str) and "\\" in v:
            return v.split("\\", 1)[0]
        return v or ""

    for sid in studies_ids:
        tags = client.get_study_shared_tags(sid)

        def get(code):
            return tags.get(code, {}).get("Value", "")

        # UID para el visor OHIF
        study_uid = get("0020,000d")
        viewer_url = (
            f"{settings.ORTHANC_BASE_URL.rstrip('/')}/ohif/viewer?StudyInstanceUIDs={study_uid}"
            if study_uid else None
        )

        studies.append({
            "id": sid,
            "patient_name": norm_name(get("0010,0010")),
            "patient_id": get("0010,0020"),
            "study_description": get("0008,1030"),
            "study_date": get("0008,0020"),
            "study_time": get("0008,0030"),
            "modality": short_modality(get("0008,0061")),
            "viewer_url": viewer_url,
        })

    # Ordenar por fecha y hora descendente (más actuales arriba)
    studies.sort(key=lambda s: (s["study_date"], s["study_time"]), reverse=True)

    return render(request, "estudios/lista_estudios.html", {"studies": studies})

@login_required
def detalle_estudio(request, study_id: str):
    try:
        study_meta = client.get_study_metadata(study_id)        # cacheado
        series = client.list_series_in_study(study_id)
        shared = client.get_study_shared_tags(study_id)         # cacheado
    except Exception as e:
        raise Http404(f"Estudio no encontrado o error Orthanc: {e}")

    context = {
        'study_id': study_id,
        'meta': study_meta,
        'shared': shared,
        'series': series,
    }
    return render(request, 'estudios/detalle_estudio.html', context)


@login_required
def detalle_serie(request, series_id: str):
    try:
        instances = client.list_instances_in_series(series_id)
    except Exception as e:
        raise Http404(f"Serie no encontrada o error Orthanc: {e}")

    context = {
        'series_id': series_id,
        'instances': instances,
    }
    return render(request, 'estudios/detalle_serie.html', context)


@login_required
def lista_series(request, study_id: str):
    try:
        series_ids = client.list_series_in_study(study_id)
    except Exception as e:
        raise Http404(f"Error obteniendo series: {e}")
    # Posible enriquecimiento posterior
    return render(request, 'estudios/lista_series.html', {
        'study_id': study_id,
        'series_ids': series_ids,
    })


@login_required
def lista_instancias(request, study_id: str, series_id: str):
    try:
        instances = client.list_instances_in_series(series_id)
    except Exception as e:
        raise Http404(f"Error obteniendo instancias: {e}")
    return render(request, 'estudios/lista_instancias.html', {
        'study_id': study_id,
        'series_id': series_id,
        'instances': instances,
    })


@login_required
def detalle_instancia(request, instance_id: str):
    try:
        meta = client.get_instance_metadata(instance_id)
    except Exception as e:
        raise Http404(f"Error obteniendo instancia: {e}")
    return render(request, 'estudios/detalle_instancia.html', {
        'instance_id': instance_id,
        'meta': meta,
    })
