import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from .models import OrdenMedica
from control_ordenes.forms import OrdenMedicaForm

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
        queryset = OrdenMedica.objects.filter(medico=self.request.user, renovada=False)

        sort = self.request.GET.get('sort', 'fecha_vencimiento')
        direction = self.request.GET.get('dir', 'asc')
        reverse = direction == 'desc'

        if sort == 'fecha_emision':
            return sorted(queryset, key=lambda o: o.fecha_emision, reverse=reverse)
        else:
            return sorted(queryset, key=lambda o: o.fecha_vencimiento(), reverse=reverse)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregamos las órdenes renovadas al contexto
        context['ordenes_renovadas'] = OrdenMedica.objects.filter(
            medico=self.request.user, renovada=True
        ).order_by('-fecha_emision')
        return context

    def test_func(self):
        return self.request.user.rol == 'medico'


@login_required
@require_POST
@csrf_exempt  # Solo si no estás usando el CSRF token correctamente en el JS, pero mejor evitarlo si se puede
def marcar_orden_renovada(request, pk):
    try:
        orden = OrdenMedica.objects.get(pk=pk, medico=request.user)
        data = json.loads(request.body)
        if data.get("renovada") is True:
            orden.renovada = True
            orden.save()
        return JsonResponse({"success": True})
    except OrdenMedica.DoesNotExist:
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)
