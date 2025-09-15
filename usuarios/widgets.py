from django.forms.widgets import ClearableFileInput


class TailwindClearableFileInput(ClearableFileInput):
    # Usamos la plantilla dentro de la app 'usuarios' para que APP_DIRS la encuentre
    template_name = 'usuarios/widgets/tailwind_clearable_file_input.html'
    initial_text = ''
    input_text = ''
    clear_checkbox_label = 'Eliminar firma actual'
