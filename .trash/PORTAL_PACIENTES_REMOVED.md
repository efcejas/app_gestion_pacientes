Esta carpeta recopila archivos eliminados del repositorio por solicitud, para una referencia futura potencial.

Registro de limpieza de la app portal_pacientes (para referencia futura)

- Eliminado: app `portal_pacientes` (código, URLs, templates, referencias en docs)
- Fecha: 2025-09-07
- Estado: removida de INSTALLED_APPS y de `config/urls.py`.
- Notas: si se desea reintroducir, crear app nueva con `python manage.py startapp portal_pacientes` y restaurar templates en `templates/portal_pacientes/`.
 - También se eliminaron templates no usados: `templates/base_pacientes.html` y `templates/base_pacientes_dos.html`.
