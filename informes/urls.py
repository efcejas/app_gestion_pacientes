from django.urls import path
from . import views

app_name = 'informes'

urlpatterns = [
    path('crear/<str:study_id>/', views.crear_o_editar, name='crear'),
    path('editar/<int:report_id>/', views.crear_o_editar, name='editar'),
    path('finalizar/<int:report_id>/', views.finalizar, name='finalizar'),
    path('ver/<int:report_id>/', views.ver_final, name='ver_final'),
]
