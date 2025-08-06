from django.urls import path
from portal_pacientes.views import QuienesSomosView, UbicacionesYContactosView, HomePacientesView, TailwindTestView, BaseTailwindDemoView, FlowbiteDaisyuiDemoView

urlpatterns = [
    path('', HomePacientesView.as_view(), name='home_pacientes'),
    path('quienes-somos/', QuienesSomosView.as_view(), name='quienes_somos'),
    path('tailwind-test/', TailwindTestView.as_view(), name='tailwind_test'),
    path('base-tailwind-demo/', BaseTailwindDemoView.as_view(), name='base_tailwind_demo'),
    path('flowbite-daisyui-demo/', FlowbiteDaisyuiDemoView.as_view(), name='flowbite_daisyui_demo'),
    # path('ubicaciones-y-contactos/', UbicacionesYContactosView.as_view(), name='ubicaciones_y_contactos'),
]