from django.urls import path
from .views import OrdenMedicaAnonimaCreateView, OrdenesDelMedicoListView, editar_orden_modal
from control_ordenes import views

app_name = 'control_ordenes'

urlpatterns = [
    path('nueva/', OrdenMedicaAnonimaCreateView.as_view(), name='crear_orden'),
    path('mis-ordenes/', OrdenesDelMedicoListView.as_view(), name='lista_ordenes'),
    path('renovar/<int:orden_id>/', views.renovar_orden, name='renovar_orden'),
    path('orden/<int:pk>/editar-modal/', editar_orden_modal, name='orden_editar_modal'),
]
