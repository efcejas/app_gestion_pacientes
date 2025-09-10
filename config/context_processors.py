from django.conf import settings


def feature_flags(request):
    """Expone flags de funcionalidades a las plantillas."""
    return {
        'FEATURE_ESTUDIOS': getattr(settings, 'FEATURE_ESTUDIOS', True),
        'FEATURE_INFORMES': getattr(settings, 'FEATURE_INFORMES', True),
    }
