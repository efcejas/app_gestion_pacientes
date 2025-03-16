from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Usuario
from .forms import RegistroUsuarioForm

class RegistroUsuarioView(CreateView):
    model = Usuario
    form_class = RegistroUsuarioForm
    template_name = "usuarios/registro.html"
    success_url = reverse_lazy("home")  # Redirige a la página principal después del registro

    def form_valid(self, form):
        usuario = form.save()
        login(self.request, usuario)  # Autentica al usuario tras registrarse
        return super().form_valid(form)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "usuarios/home.html"

