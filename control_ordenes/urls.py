from django.urls import path
from .views import OrdenMedicaAnonimaCreateView

app_name = 'control_ordenes'

urlpatterns = [
    path('nueva/', OrdenMedicaAnonimaCreateView.as_view(), name='crear_orden'),
]
