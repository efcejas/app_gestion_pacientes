from django.shortcuts import render
from django.views.generic import TemplateView

class HomePacientesView(TemplateView):
    template_name = "portal_pacientes/home.html"
    
class QuienesSomosView(TemplateView):
    template_name = "portal_pacientes/quienes_somos.html"
    
class UbicacionesYContactosView(TemplateView):
    template_name = "portal_pacientes/ubicaciones_y_contactos.html"
    
