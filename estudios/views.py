from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .services import client


@login_required
def lista_estudios(request):
    studies_ids = client.list_studies()
    studies = []

    for sid in studies_ids:
        tags = client.get_study_shared_tags(sid)

        def get_tag_value(code):
            return tags.get(code, {}).get("Value", "")

        studies.append({
            "id": sid,
            "patient_name": get_tag_value("0010,0010"),
            "patient_id": get_tag_value("0010,0020"),
            "study_description": get_tag_value("0008,1030"),
            "study_date": get_tag_value("0008,0020"),
            "study_time": get_tag_value("0008,0030"),
            "modality": get_tag_value("0008,0061"),
        })

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
