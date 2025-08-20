from django.urls import path
from . import views

app_name = 'estudios'

urlpatterns = [
    # /estudios/
    path('', views.lista_estudios, name='lista_estudios'),

    # /estudios/<study_id>/
    path('<str:study_id>/', views.detalle_estudio, name='detalle_estudio'),

    # /estudios/<study_id>/series/
    path('<str:study_id>/series/', views.lista_series, name='lista_series'),

    # /estudios/<study_id>/series/<series_id>/
    path('<str:study_id>/series/<str:series_id>/', views.detalle_serie, name='detalle_serie'),

    # /estudios/<study_id>/series/<series_id>/instances/
    path(
        '<str:study_id>/series/<str:series_id>/instances/',
        views.lista_instancias,
        name='lista_instancias'
    ),

    # (Opcional) acceso directo por instancia, útil para vistas/descargas puntuales:
    # /estudios/instances/<instance_id>/
    path('instances/<str:instance_id>/', views.detalle_instancia, name='detalle_instancia'),
]
