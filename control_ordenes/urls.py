from django.urls import path
from .views import OrdenMedicaAnonimaCreateView, OrdenesDelMedicoListView, marcar_orden_renovada

app_name = 'control_ordenes'

urlpatterns = [
    path('nueva/', OrdenMedicaAnonimaCreateView.as_view(), name='crear_orden'),
    path('mis-ordenes/', OrdenesDelMedicoListView.as_view(), name='lista_ordenes'),
    path('marcar_renovada/<int:pk>/', marcar_orden_renovada, name='marcar_renovada'),
]
