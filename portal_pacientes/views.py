from django.shortcuts import render
from django.views.generic import TemplateView

class HomePacientesView(TemplateView):
    template_name = "portal_pacientes/home.html"
