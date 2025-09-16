from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from control_ordenes.forms import OrdenMedicaForm
from .models import Usuario
from .forms import RegistroUsuarioForm, FirmaMedicoForm, UsuarioPerfilForm

class RegistroUsuarioView(CreateView):
    model = Usuario
    form_class = RegistroUsuarioForm
    template_name = "usuarios/registro.html"
    success_url = reverse_lazy("registro_confirmacion")  # Redirige a la página de confirmación

    def form_valid(self, form):
        usuario = form.save()
        login(self.request, usuario)  # Autentica al usuario tras registrarse
        return super().form_valid(form)
    
class RegistroConfirmacionView(TemplateView):
    template_name = "usuarios/registro_confirmacion.html"

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "usuarios/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["form"] = OrdenMedicaForm()
        context["es_medico"] = user.is_authenticated and getattr(user, "rol", None) == "medico"
        context["es_admin_medico"] = user.is_authenticated and user.groups.filter(name="Administrativos con permisos médicos").exists()
        return context


"""Vista antigua SubirFirmaView eliminada; ahora la firma se gestiona en PerfilEditarView."""


class PerfilDetalleView(LoginRequiredMixin, TemplateView):
    template_name = "usuarios/perfil.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["usuario"] = self.request.user
        return ctx


class PerfilEditarView(LoginRequiredMixin, TemplateView):
    template_name = "usuarios/perfil_form.html"

    def get(self, request, *args, **kwargs):
        form = UsuarioPerfilForm(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = UsuarioPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil")
        return render(request, self.template_name, {"form": form})