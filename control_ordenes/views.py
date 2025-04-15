from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from control_ordenes.forms import OrdenMedicaForm
from .models import OrdenMedica

class OrdenMedicaAnonimaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = OrdenMedica
    form_class = OrdenMedicaForm
    # template_name = 'control_ordenes/orden_form.html'
    # Redirigir a la página de inicio después de crear la orden
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.medico = self.request.user
        messages.success(self.request, "Orden médica creada con éxito.")
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.rol == 'medico'

class OrdenesDelMedicoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = OrdenMedica
    template_name = 'control_ordenes/lista_ordenes.html'
    context_object_name = 'ordenes'
    ordering = ['fecha_emision']

    def get_queryset(self):
        return sorted(
            OrdenMedica.objects.filter(medico=self.request.user),
            key=lambda orden: orden.dias_restantes
        )

    def test_func(self):
        return self.request.user.rol == 'medico'
