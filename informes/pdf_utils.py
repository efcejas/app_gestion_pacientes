from io import BytesIO
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings
from xhtml2pdf import pisa
import logging
from pathlib import Path

try:
    from django.contrib.staticfiles import finders
except Exception:  # pragma: no cover
    finders = None

logger = logging.getLogger(__name__)


def render_report_to_pdf(report, context_extra=None, template_name='informes/pdf/base_report.html'):
    """Genera un PDF a partir del contenido HTML del reporte.
    Devuelve (success, ContentFile|None, error_str|None)
    """
    context = {
        'report': report,
    }
    # Logo institucional: búsqueda robusta usando staticfiles finders + rutas locales.
    def _load_logo_bytes():
        fname = getattr(settings, 'LOGO_PDF_FILENAME', 'logo_cmi.png')
        alt_names = []
        # Añadir variantes comunes si el nombre configurado no coincide
        common_variants = ['logo_cmi.png', 'CMIlogo.png', 'cmi_logo.png', 'logo-cmi.png']
        for v in common_variants:
            if v.lower() != fname.lower():
                alt_names.append(v)
        # 1) Intentar con finders (respeta STATICFILES_FINDERS, útil en prod).
        candidate_paths = []
        if finders:
            try:
                found = finders.find(f"img/{fname}") or finders.find(fname)
                if isinstance(found, (list, tuple)):
                    candidate_paths.extend([Path(p) for p in found])
                elif found:
                    candidate_paths.append(Path(found))
                # Variantes extra
                for alt in alt_names:
                    found_alt = finders.find(f"img/{alt}") or finders.find(alt)
                    if isinstance(found_alt, (list, tuple)):
                        candidate_paths.extend([Path(p) for p in found_alt])
                    elif found_alt:
                        candidate_paths.append(Path(found_alt))
            except Exception:  # pragma: no cover
                logger.debug('finders.find fallo para logo', exc_info=True)
        # 2) Rutas locales conocidas.
        base = Path(settings.BASE_DIR)
        candidate_paths.extend([
            base / 'static' / 'img' / fname,
            base / 'staticfiles' / 'img' / fname,
        ])
        for alt in alt_names:
            candidate_paths.extend([
                base / 'static' / 'img' / alt,
                base / 'staticfiles' / 'img' / alt,
            ])
        # 3) Heurística: cualquier archivo que empiece por 'logo' en static/img
        static_img = base / 'static' / 'img'
        if static_img.exists():
            for p in static_img.glob('logo*.*'):
                if p not in candidate_paths:
                    candidate_paths.append(p)
        staticfiles_img = base / 'staticfiles' / 'img'
        if staticfiles_img.exists():
            for pattern in ('logo*.*', 'CMIlogo*.*', 'cmi*logo*.*'):
                for p in staticfiles_img.glob(pattern):
                    if p not in candidate_paths:
                        candidate_paths.append(p)
        for p in candidate_paths:
            try:
                if not p.exists() or not p.is_file():
                    continue
                raw = p.read_bytes()
                # Aceptar incluso logos muy pequeños (>=10 bytes) para entornos de prueba
                if len(raw) < 10:
                    continue
                if raw.startswith(b'\x89PNG'):
                    mime = 'image/png'
                elif raw.startswith(b'\xFF\xD8'):
                    mime = 'image/jpeg'
                else:
                    continue
                import base64
                return f'data:{mime};base64,' + base64.b64encode(raw).decode('ascii'), p, mime
            except Exception:  # pragma: no cover
                logger.debug('Error leyendo candidato de logo %s', p, exc_info=True)
        return None, None, None

    data_uri, path_used, mime = _load_logo_bytes()
    if data_uri:
        context['logo_data_uri'] = data_uri
        logger.info('Logo incorporado al PDF: %s (%s)', path_used, mime)
    else:
        logger.info('Logo no encontrado. Revisar LOGO_PDF_FILENAME y rutas static/img/')
    # Información institucional básica (placeholder editable)
    context.setdefault('institucion', {
        'nombre': getattr(settings, 'INSTITUCION_NOMBRE', 'Centro Médico Integral'),
        'linea1': getattr(settings, 'INSTITUCION_LINEA1', ''),
        'linea2': getattr(settings, 'INSTITUCION_LINEA2', ''),
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
