"""Utilidades de la app informes: sanitización y helpers de snapshot.

Centraliza lógica repetida para:
 - Sanitizar HTML de contenido de informe.
 - Construir snapshot/estructura de metadatos de estudio desde tags Orthanc.

Mantener aquí para reducir duplicación en vistas y facilitar test unitario futuro.
"""
from __future__ import annotations

from typing import Dict, Any
import hashlib

try:  # bleach es obligatorio en runtime, pero fallback defensivo por si falta en un entorno aislado.
    import bleach  # type: ignore
except Exception:  # pragma: no cover - fallback raro
    bleach = None  # type: ignore

ALLOWED_REPORT_TAGS = [
    'p','br','strong','em','ul','ol','li','h1','h2','h3','h4','blockquote',
    'span','u','sub','sup','a','code','s','del','mark','hr'
]
ALLOWED_REPORT_ATTRS = {
    'span': ['style'],
    'p': ['style'],
    'h1': ['style'],
    'h2': ['style'],
    'h3': ['style'],
    'h4': ['style'],
    'blockquote': ['style'],
    'mark': ['style'],
    'a': ['href','title','target','rel'],
}

def sanitize_report_html(html: str) -> str:
    """Devuelve HTML sanitizado según whitelist.

    - Elimina tags/eventos peligrosos (<script>, atributos on*).
    - Conserva estilos inline solo en span (pendiente limitar propiedades CSS con CssSanitizer).
    """
    if not html:
        return ''
    if bleach is None:
        return html
    # Limitar estilos CSS permitidos a propiedades seguras que usamos en el editor
    try:
        from bleach.css_sanitizer import CSSSanitizer  # type: ignore
        css = CSSSanitizer(allowed_css_properties=[
            'font-size', 'color', 'background-color', 'text-align', 'font-weight', 'font-style', 'text-decoration', 'font-family'
        ])
    except Exception:
        css = None  # type: ignore
    cleaned = bleach.clean(
        html,
        tags=ALLOWED_REPORT_TAGS,
        attributes=ALLOWED_REPORT_ATTRS,
        protocols=['http','https','mailto'],
        strip=True,
        css_sanitizer=css,
    )
    # Fuerza rel="noopener noreferrer" en enlaces con target=_blank
    if '<a' in cleaned:
        from bs4 import BeautifulSoup  # type: ignore
        try:
            soup = BeautifulSoup(cleaned, 'html.parser')
            for a in soup.find_all('a'):
                if a.get('target') == '_blank':
                    rel = (a.get('rel') or [])
                    if isinstance(rel, str):
                        rel = [rel]
                    need = {'noopener','noreferrer'}
                    rel_set = set(rel) | need
                    a['rel'] = ' '.join(sorted(rel_set))
            cleaned = str(soup)
        except Exception:
            pass
    return cleaned


def build_study_info_from_tags(tags: Dict[str, Any] | None) -> Dict[str, Any]:
    """Extrae campos amigables desde el dict de tags compartidos Orthanc.

    Tags de interés:
      - Paciente: 0010,0010 (nombre), 0010,0020 (ID), 0010,0040 (sexo), 0010,0030 (fecha nacimiento)
      - Estudio: 0008,1030 (descripción), 0008,0020 (fecha), 0008,0030 (hora), 0008,0050 (Accession), 0008,0061 (modalities)
    """
    if not tags:
        return {}

    def val(code: str):  # manejamos estructura {code: {"Value": "..."}}
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
        'modalities': val('0008,0061'),
    }


# ---- Hashing / Firma demo ----

def hash_content(html: str) -> str:
    """SHA256 hex del contenido HTML (UTF-8, ignora errores)."""
    if html is None:
        html = ''
    return hashlib.sha256(html.encode('utf-8', errors='ignore')).hexdigest()


def hash_pdf_bytes(data: bytes | None) -> str:
    """SHA256 hex de bytes PDF (cadena vacía si None o vacío)."""
    if not data:
        return ''
    return hashlib.sha256(data).hexdigest()


def demo_signature(html: str, username: str) -> str:
    """Genera firma DEMO estable (prefijo FD-) a partir de contenido + usuario.

    Usa misma lógica anterior para no invalidar firmas ya emitidas.
    """
    payload = (html or '') + (username or '')
    hexhash = hashlib.sha256(payload.encode('utf-8', errors='ignore')).hexdigest()[:32]
    return f"FD-{hexhash}"

