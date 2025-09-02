from io import BytesIO
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings
from xhtml2pdf import pisa
import logging

logger = logging.getLogger(__name__)


def render_report_to_pdf(report, context_extra=None, template_name='informes/pdf/base_report.html'):
    """Genera un PDF a partir del contenido HTML del reporte.
    Devuelve (success, ContentFile|None, error_str|None)
    """
    context = {
        'report': report,
    }
    # Logo institucional: restaurar búsqueda múltiple (static y staticfiles) y admitir varios nombres.
    try:
        import base64, os
        from pathlib import Path
        candidates = [
            Path(settings.BASE_DIR) / 'static' / 'img' / 'logo_cmi.png',
            Path(settings.BASE_DIR) / 'static' / 'img' / 'CMIlogo.png',
            Path(settings.BASE_DIR) / 'staticfiles' / 'img' / 'logo_cmi.png',
            Path(settings.BASE_DIR) / 'staticfiles' / 'img' / 'CMIlogo.png',
        ]
        for c in candidates:
            if not c.exists() or not c.is_file():
                continue
            try:
                with open(c, 'rb') as fh:
                    raw = fh.read()
                if len(raw) < 50:  # permitir logos pequeños pero evitar archivos vacíos
                    logger.info('Logo demasiado pequeño, ignorando: %s', c)
                    continue
                mime = 'image/png' if raw.startswith(b'\x89PNG') else ('image/jpeg' if raw.startswith(b'\xFF\xD8') else None)
                if not mime:
                    logger.info('Cabecera de logo no reconocida: %s', c)
                    continue
                data_uri = f'data:{mime};base64,' + base64.b64encode(raw).decode('ascii')
                context['logo_data_uri'] = data_uri
                logger.info('Logo incorporado al PDF: %s (%s)', c, mime)
                break
            except Exception:
                logger.warning('Error leyendo logo %s', c, exc_info=True)
        else:
            logger.info('No se encontró logo válido en rutas previstas.')
    except Exception:
        logger.debug('Error general al preparar logo', exc_info=True)
    # Información institucional básica (placeholder editable)
    context.setdefault('institucion', {
        'nombre': 'Centro Médico Integral',
        'linea1': 'Av. Salud 1234 - Ciudad',
        'linea2': 'Tel: (000) 000-0000 | info@cmi.local',
    })
    if context_extra:
        context.update(context_extra)
    # El cuerpo del informe ya viene como HTML en report.contenido
    html = render_to_string(template_name, context)
    pdf_io = BytesIO()
    result = pisa.CreatePDF(html, dest=pdf_io, encoding='UTF-8')
    if result.err:
        logger.warning('Fallo generación PDF para Report %s', report.id)
        return False, None, 'Error generando PDF'
    return True, ContentFile(pdf_io.getvalue()), None
