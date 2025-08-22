from django import template
from datetime import datetime

register = template.Library()

@register.filter
def clean_name(value):
    """Reemplaza ^ por espacio en nombres DICOM"""
    if not value:
        return ""
    return value.replace("^", " ")

@register.filter
def first_modality(value):
    """Devuelve solo la primera modalidad (ej: MR de MR\SR)"""
    if not value:
        return ""
    # asegurarse que sea string
    value = str(value)
    return value.split("\\")[0]

@register.filter(name="dicom_date")
def dicom_date(value, formato="dd/mm/yy"):
    """Convierte una fecha DICOM (YYYYMMDD) a formato legible.

    Uso en plantilla:
        {{ s.study_date|dicom_date }}              -> 17/02/24
        {{ s.study_date|dicom_date:"dd/mm/yyyy" }} -> 17/02/2024

    Si la cadena no es válida retorna cadena vacía.
    """
    if not value:
        return ""
    val = str(value).strip()
    if len(val) != 8 or not val.isdigit():
        return ""
    try:
        dt = datetime.strptime(val, "%Y%m%d").date()
    except ValueError:
        return ""

    fmt_map = {
        "dd/mm/yy": "%d/%m/%y",
        "dd/mm/yyyy": "%d/%m/%Y",
        "yyyy-mm-dd": "%Y-%m-%d",
    }
    py_fmt = fmt_map.get(formato.lower(), "%d/%m/%y")
    return dt.strftime(py_fmt)
