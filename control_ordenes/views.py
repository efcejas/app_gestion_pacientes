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

    def get_queryset(self):
        queryset = OrdenMedica.objects.filter(medico=self.request.user)

        sort = self.request.GET.get('sort', 'fecha_vencimiento')
        direction = self.request.GET.get('dir', 'asc')
        reverse = direction == 'desc'

        if sort == 'fecha_emision':
            return sorted(queryset, key=lambda o: o.fecha_emision, reverse=reverse)
        else:  # default a fecha_vencimiento
            return sorted(queryset, key=lambda o: o.fecha_vencimiento(), reverse=reverse)

    def test_func(self):
        return self.request.user.rol == 'medico'