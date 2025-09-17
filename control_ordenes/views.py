import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from .models import OrdenMedica
from .forms import OrdenMedicaFiltroForm
from control_ordenes.forms import OrdenMedicaForm
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q


class OrdenMedicaAnonimaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = OrdenMedica
    form_class = OrdenMedicaForm
    template_name = 'control_ordenes/orden_form.html'
    # Redirigir a la página de inicio después de crear la orden
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.medico = self.request.user
        # marcar auditoría
        form.instance.last_action = "creada"
        form.instance.last_action_at = timezone.now()
        form.instance.last_actor = self.request.user
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
    paginate_by = 20

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

        # Filtro rápido por estado
        estado = (self.request.GET.get('estado') or '').lower()
        if estado in {'vigentes', 'proximas', 'vencidas'}:
            # convertir a lista para filtrar por propiedad calculada dias_restantes
            iterable = list(queryset)
            if estado == 'vencidas':
                queryset = [o for o in iterable if o.dias_restantes < 0]
            elif estado == 'proximas':
                queryset = [o for o in iterable if 0 <= o.dias_restantes <= 10]
            elif estado == 'vigentes':
                queryset = [o for o in iterable if o.dias_restantes > 10]

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
        # Variable que usa la plantilla para decidir el mensaje cuando no hay resultados
        context['total_ordenes'] = total
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
        # QS sin page para enlaces de paginación preservando filtros y orden
        q2 = self.request.GET.copy()
        if 'page' in q2:
            del q2['page']
        context['qs_no_page'] = q2.urlencode()
        # QS sin 'estado' ni 'page' para armar enlaces de filtros rápidos
        q3 = self.request.GET.copy()
        for k in ['page', 'estado']:
            if k in q3:
                del q3[k]
        context['qs_filters'] = q3.urlencode()
        context['current_estado'] = (self.request.GET.get('estado') or '').lower()
        # Serialización básica para ordenamiento en cliente (Alpine)
        ordenes = context.get('ordenes', [])
        data = []
        for o in ordenes:
            try:
                fv = o.fecha_vencimiento()
                actor = getattr(o, 'last_actor', None)
                actor_label = ''
                if actor:
                    fn = getattr(actor, 'first_name', '') or ''
                    ln = getattr(actor, 'last_name', '') or ''
                    un = getattr(actor, 'username', '') or ''
                    actor_label = (fn + ' ' + ln).strip() or f"@{un}"
                action_label = ''
                try:
                    action_label = o.get_last_action_display() if getattr(o, 'last_action', '') else ''
                except Exception:
                    action_label = getattr(o, 'last_action', '') or ''
                action_at_label = ''
                lat = getattr(o, 'last_action_at', None)
                if lat:
                    try:
                        lat_local = timezone.localtime(lat)
                    except Exception:
                        lat_local = lat
                    try:
                        action_at_label = lat_local.strftime('%d/%m/%Y %H:%M')
                    except Exception:
                        action_at_label = str(lat_local)
                # Normalizar fecha_emision para evitar fallos cuando es string
                fe_iso = ''
                fe_label = ''
                fe = getattr(o, 'fecha_emision', None)
                try:
                    # ISO
                    fe_iso = fe.isoformat() if hasattr(fe, 'isoformat') else str(fe)
                except Exception:
                    fe_iso = str(fe)
                try:
                    fe_label = fe.strftime('%d/%m/%Y') if hasattr(fe, 'strftime') else str(fe)
                except Exception:
                    fe_label = str(fe)
                data.append({
                    'id': o.id,
                    'identificador': o.identificador_paciente,
                    'fecha_emision_iso': fe_iso,
                    'fecha_emision_label': fe_label,
                    'fecha_vencimiento_iso': fv.isoformat() if hasattr(fv, 'isoformat') else str(fv),
                    'fecha_vencimiento_label': fv.strftime('%d/%m/%Y'),
                    'dias_validez': o.dias_validez,
                    'dias_restantes': o.dias_restantes,
                    'renovada': o.renovada,
                    'last_action_label': action_label,
                    'last_action_at_label': action_at_label,
                    'last_actor_label': actor_label,
                })
            except Exception:
                pass
        # Proveer JSON válido para el frontend (Alpine)
        context['ordenes_data'] = data  # compat
        context['ordenes_data_json'] = json.dumps(data, ensure_ascii=False)
        # Usuarios en línea (médicos + administrativos con permisos) en últimos 5 minutos
        User = get_user_model()
        now = timezone.now()
        online_cut = now - timezone.timedelta(minutes=5)
        # Requiere last_login aproximado; como proxy simple usamos last_login >= corte
        online_users = User.objects.filter(
            last_login__isnull=False,
            last_login__gte=online_cut
        ).filter(
            Q(rol='medico') | Q(groups__name='Administrativos con permisos médicos')
        ).distinct().values('id', 'first_name', 'last_name', 'username', 'last_login')
        online_list = list(online_users)
        context['online_users'] = online_list
        return context

    def test_func(self):
        user = self.request.user
        return (
            getattr(user, 'rol', None) == 'medico'
            or user.groups.filter(name="Administrativos con permisos médicos").exists()
        )

@login_required
@require_POST
def renovar_orden(request, orden_id):
    try:
        data = json.loads(request.body)
        nueva_fecha_emision = data.get('nueva_fecha_emision')
        nueva_validez = int(data.get('nueva_validez'))

        orden = OrdenMedica.objects.get(id=orden_id)
        # permiso: propietario o admin con permisos médicos
        user = request.user
        if not (
            getattr(user, 'rol', None) == 'medico' and orden.medico_id == user.id
            or user.groups.filter(name="Administrativos con permisos médicos").exists()
        ):
            return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        orden.fecha_emision = datetime.strptime(
            nueva_fecha_emision, "%Y-%m-%d").date()
        orden.dias_validez = nueva_validez
        orden.last_action = "renovada"
        orden.last_action_at = timezone.now()
        orden.last_actor = user
        orden.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_POST
@login_required
def editar_orden_modal(request, pk):
    try:
        data = json.loads(request.body)
        orden = OrdenMedica.objects.get(pk=pk)
        user = request.user
        if not (
            getattr(user, 'rol', None) == 'medico' and orden.medico_id == user.id
            or user.groups.filter(name="Administrativos con permisos médicos").exists()
        ):
            return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        orden.identificador_paciente = data['identificador_paciente']
        # Asegurar tipos correctos
        try:
            orden.fecha_emision = datetime.strptime(data['fecha_emision'], "%Y-%m-%d").date()
        except Exception:
            # si falla el parseo, devolvemos error controlado
            return JsonResponse({'success': False, 'error': 'Fecha de emisión inválida'}, status=400)
        try:
            orden.dias_validez = int(data['dias_validez'])
        except Exception:
            return JsonResponse({'success': False, 'error': 'Días de validez inválidos'}, status=400)
        orden.last_action = "editada"
        orden.last_action_at = timezone.now()
        orden.last_actor = user
        orden.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_POST
@login_required
def eliminar_orden_modal(request, pk):
    try:
        orden = OrdenMedica.objects.get(pk=pk)
        user = request.user
        if not (
            getattr(user, 'rol', None) == 'medico' and orden.medico_id == user.id
            or user.groups.filter(name="Administrativos con permisos médicos").exists()
        ):
            return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
        orden.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
