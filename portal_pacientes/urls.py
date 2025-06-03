from django.urls import path
from portal_pacientes.views import QuienesSomosView, UbicacionesYContactosView, HomePacientesView

urlpatterns = [
    path('', HomePacientesView.as_view(), name='home_pacientes'),
    # path('quienes-somos/', QuienesSomosView.as_view(), name='quienes_somos'),
    # path('ubicaciones-y-contactos/', UbicacionesYContactosView.as_view(), name='ubicaciones_y_contactos'),
]