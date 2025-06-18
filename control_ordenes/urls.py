from django.urls import path
from .views import OrdenMedicaAnonimaCreateView, OrdenesDelMedicoListView
from control_ordenes import views

app_name = 'control_ordenes'

urlpatterns = [
    path('nueva/', OrdenMedicaAnonimaCreateView.as_view(), name='crear_orden'),
    path('mis-ordenes/', OrdenesDelMedicoListView.as_view(), name='lista_ordenes'),
    path('renovar/<int:orden_id>/', views.renovar_orden, name='renovar_orden'),
]
