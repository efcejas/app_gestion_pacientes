from django.urls import path
from portal_pacientes.views import HomePacientesView

urlpatterns = [
    path('', HomePacientesView.as_view(), name='home_pacientes'),
]