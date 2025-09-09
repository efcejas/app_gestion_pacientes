# Documentación del Proyecto CMI

Este directorio centraliza la documentación viva del proyecto.

## Índice
- Arquitectura general (`arquitectura.md`)
- Modelos y diseño de datos (`modelos.md`)
- Frontend y estilos (Tailwind) (`TAILWIND_README.md`)
- Orthanc
  - Instalación y configuración inicial (`orthanc/instalacion.md`)
  - Plan de integración / sincronización (`integracion/orthanc_sync.md`)
- Flujo de informes médicos (`informes/proceso_informe.md`)
- Email y credenciales (ver README principal)

## Convenciones
- Formato: Markdown.
- Idioma: Español (es-AR).
- Un archivo por tema. Nombres en minúsculas con guiones bajos.
- Imágenes (si se agregan): `docs/img/`.
- Commits que cambien decisiones arquitectónicas deben actualizar estos documentos.

## Próximos documentos sugeridos
- `seguridad.md`
- `auditoria.md`
- `roadmap.md`

## Estado actual
- UI migrada a Tailwind (modo oscuro, componentes con Flowbite/Alpine donde aplica).
- Eliminado Bootstrap de los templates (se mantienen utilidades `add_class` en templates para estilizar widgets de formularios).
- SMTP con Gmail: usar App Password (16 chars sin espacios) y SSL 465.
