from django.urls import path
from .views import OrdenMedicaAnonimaCreateView, OrdenesDelMedicoListView

app_name = 'control_ordenes'

urlpatterns = [
    path('nueva/', OrdenMedicaAnonimaCreateView.as_view(), name='crear_orden'),
    path('mis-ordenes/', OrdenesDelMedicoListView.as_view(), name='lista_ordenes'),
]
