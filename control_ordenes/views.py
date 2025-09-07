import json
from datetime import datetime

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
from .forms import OrdenMedicaFiltroForm
from control_ordenes.forms import OrdenMedicaForm


class OrdenMedicaAnonimaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = OrdenMedica
    form_class = OrdenMedicaForm
    template_name = 'control_ordenes/orden_form.html'
    # Redirigir a la página de inicio después de crear la orden
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.medico = self.request.user
        messages.success(self.request, "Orden médica creada con éxito.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "No se pudo crear la orden. Revisá los datos e intentá nuevamente.")
        return super().form_invalid(form)

    def test_func(self):
        user = self.request.user
        return (
            getattr(user, 'rol', None) == 'medico'
            or user.groups.filter(name="Administrativos con permisos médicos").exists()
        )


class OrdenesDelMedicoListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = OrdenMedica
    template_name = 'control_ordenes/lista_ordenes.html'
    context_object_name = 'ordenes'

    def get_queryset(self):
        queryset = OrdenMedica.objects.filter(renovada=False)
        form = OrdenMedicaFiltroForm(self.request.GET)

        if form.is_valid():
            identificador = form.cleaned_data.get('identificador')
            fecha_emision = form.cleaned_data.get('fecha_emision')
            fecha_vencimiento = form.cleaned_data.get('fecha_vencimiento')

            if identificador:
                queryset = queryset.filter(
                    identificador_paciente__icontains=identificador)
            if fecha_emision:
                queryset = queryset.filter(fecha_emision=fecha_emision)
            if fecha_vencimiento:
                # Suponiendo que tienes un método fecha_vencimiento()
                # Si es un campo, usa queryset.filter(fecha_vencimiento=fecha_vencimiento)
                queryset = [
                    o for o in queryset if o.fecha_vencimiento() == fecha_vencimiento]

        # Ordenamiento
        sort = self.request.GET.get('sort', 'fecha_vencimiento')
        direction = self.request.GET.get('dir', 'asc')
        reverse = direction == 'desc'

        if sort == 'fecha_emision':
            return sorted(queryset, key=lambda o: o.fecha_emision, reverse=reverse)
        else:
            return sorted(queryset, key=lambda o: o.fecha_vencimiento(), reverse=reverse)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_form'] = OrdenMedicaFiltroForm(self.request.GET)
        # Totales generales (no renovadas)
        base_qs = OrdenMedica.objects.filter(renovada=False)
        total = base_qs.count()
        vencidas = 0
        proximas = 0
        vigentes = 0
        for o in base_qs:  # usa la prop dias_restantes calculada en Python
            dr = o.dias_restantes
            if dr < 0:
                vencidas += 1
            elif dr <= 10:
                proximas += 1
            else:
                vigentes += 1
        context['stats'] = {
            'total': total,
            'vencidas': vencidas,
            'proximas': proximas,
            'vigentes': vigentes,
        }
        try:
            context['mostradas'] = len(context.get('ordenes', []))
        except TypeError:
            context['mostradas'] = 0
        # QS sin parametros de orden para evitar duplicados y flicker en los links de ordenamiento
        q = self.request.GET.copy()
        for k in ['sort', 'dir']:
            if k in q:
                del q[k]
        context['qs_no_sort'] = q.urlencode()
        # Serialización básica para ordenamiento en cliente (Alpine)
        ordenes = context.get('ordenes', [])
        data = []
        for o in ordenes:
            try:
                fv = o.fecha_vencimiento()
                data.append({
                    'id': o.id,
                    'identificador': o.identificador_paciente,
                    'fecha_emision_iso': o.fecha_emision.isoformat() if hasattr(o.fecha_emision, 'isoformat') else str(o.fecha_emision),
                    'fecha_emision_label': o.fecha_emision.strftime('%d/%m/%Y'),
                    'fecha_vencimiento_iso': fv.isoformat() if hasattr(fv, 'isoformat') else str(fv),
                    'fecha_vencimiento_label': fv.strftime('%d/%m/%Y'),
                    'dias_validez': o.dias_validez,
                    'dias_restantes': o.dias_restantes,
                    'renovada': o.renovada,
                })
            except Exception:
                pass
        # Proveer JSON válido para el frontend (Alpine)
        context['ordenes_data'] = data  # compat
        context['ordenes_data_json'] = json.dumps(data, ensure_ascii=False)
        return context

    def test_func(self):
        user = self.request.user
        return (
            getattr(user, 'rol', None) == 'medico'
            or user.groups.filter(name="Administrativos con permisos médicos").exists()
        )

@csrf_exempt
@require_POST
def renovar_orden(request, orden_id):
    try:
        data = json.loads(request.body)
        nueva_fecha_emision = data.get('nueva_fecha_emision')
        nueva_validez = int(data.get('nueva_validez'))

        orden = OrdenMedica.objects.get(id=orden_id)
        orden.fecha_emision = datetime.strptime(
            nueva_fecha_emision, "%Y-%m-%d").date()
        orden.dias_validez = nueva_validez
        orden.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt  # Puedes quitar esto si usas correctamente el CSRF token
@require_POST
@login_required
def editar_orden_modal(request, pk):
    try:
        data = json.loads(request.body)
        orden = OrdenMedica.objects.get(pk=pk)
        orden.identificador_paciente = data['identificador_paciente']
        orden.fecha_emision = data['fecha_emision']
        orden.dias_validez = data['dias_validez']
        orden.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_POST
@login_required
def eliminar_orden_modal(request, pk):
    try:
        orden = OrdenMedica.objects.get(pk=pk)
        orden.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
