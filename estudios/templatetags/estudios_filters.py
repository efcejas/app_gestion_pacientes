from django import template

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
