from django.shortcuts import render
from django.views.generic import TemplateView

class HomePacientesView(TemplateView):
    template_name = "portal_pacientes/home.html"
    
class QuienesSomosView(TemplateView):
    template_name = "portal_pacientes/quienes_somos.html"
    
class UbicacionesYContactosView(TemplateView):
    template_name = "portal_pacientes/ubicaciones_y_contactos.html"

class TailwindTestView(TemplateView):
    template_name = "portal_pacientes/tailwind_test.html"

class BaseTailwindDemoView(TemplateView):
    template_name = "portal_pacientes/base_tailwind_demo.html"

class FlowbiteDaisyuiDemoView(TemplateView):
    template_name = "portal_pacientes/flowbite_daisyui_demo.html"
