# Arquitectura General

## Visión
Aplicación Django modular que gestiona usuarios, órdenes médicas e integra un servidor DICOM Orthanc para ingestión de estudios y generación de informes clínicos.

## Componentes
- Django (núcleo web / backend)
- Apps internas: `usuarios`, `control_ordenes`, `estudios`, `informes`.
- Orthanc (servidor DICOM) en `http://localhost:8042`.
- Frontend: Tailwind + DaisyUI (migración desde Bootstrap en progreso).
- Base de datos: SQLite (dev) → Postgres (prod previsto).
- WhiteNoise para estáticos.

## Flujo alto nivel
1. Equipo de ecografía envía estudio DICOM a Orthanc.
2. Orthanc almacena y expone metadatos vía REST / DICOMweb.
3. Django sincroniza (polling/eventos) y/o consulta en vivo en fase inicial.
4. Médico abre estudio en OHIF (`/ohif/viewer?StudyInstanceUIDs=<UID>`).
5. Se genera informe (draft → final) asociado al Study (actualmente sin modelo `Study`; se usa `study_internal_id` + snapshot guardado al finalizar).
6. Render PDF y bloqueo de informe (estado `final`). Si se necesita modificar, se crea nueva versión (`version` +1) sin sobrescribir la final previa.
7. Auditoría específica: `LogInforme` guarda eventos `draft_save` y `finalize` con hashes, versión de plantilla y tamaño PDF.

## Principios
- Separación de capas: vistas delgadas, lógica en servicios.
- Idempotencia en ingestión de estudios por UID.
- Seguridad: acceso mínimo necesario, eliminación de endpoints sin CSRF.
- Evolución incremental: iteraciones pequeñas.

## Decisiones Abiertas
- Método definitivo de ingestión (webhook vs polling).
- Almacenamiento de instancias DICOM local vs solo metadatos.
- Uso de Celery para tareas diferidas.

## Métricas a monitorear (futuro)
- Latencia ingestión (Orthanc → Django).
- Cobertura de informes (estudios reportados / total).
- Errores en sincronización.

## Notas recientes
- 2025-08-20: Cliente Orthanc con cache LRU para resolver `StudyInstanceUID`.
- 2025-09-02: Implementado versionado de informes y logging (`LogInforme`). Añadidos hashes de contenido y PDF y snapshot inmutable DICOM básico.
	- Se parametriza branding (institución, logo) y versión de plantilla (`REPORT_TEMPLATE_VERSION`).
	- Sanitización HTML con `bleach` (baseline).
 - 2025-09-05: Refactor utilidades (`informes/utils.py`) centraliza sanitización, hashing y firma demo. Mejorada lógica de descubrimiento de logo en PDF (`pdf_utils.py`) usando `staticfiles.finders`, rutas `static/` y `staticfiles/` y heurística de nombres (`logo_cmi.png`, `CMIlogo.png`, variantes). Eliminado comando obsoleto de regeneración de PDFs.

## Gestión de Logo en PDF
La función `render_report_to_pdf` busca el logo en este orden:
1. `LOGO_PDF_FILENAME` (settings) vía `staticfiles.finders` (`img/<fname>` o `<fname>`).
2. Rutas locales: `static/img/<fname>` y `staticfiles/img/<fname>`.
3. Variantes comunes de nombre: `logo_cmi.png`, `CMIlogo.png`, `cmi_logo.png`, `logo-cmi.png`.
4. Heurística: archivos que inicien con `logo` o coincidan con patrones (`CMIlogo*`, `cmi*logo*`) en `static/img` y `staticfiles/img`.

Se incorpora como Data URI (PNG o JPEG) si el archivo ≥10 bytes y con cabecera válida. Si no se encuentra, el PDF se genera sin logo (log nivel INFO).

## Utilidades Centralizadas
Archivo `informes/utils.py` provee:
- `sanitize_report_html`
- `build_study_info_from_tags`
- `hash_content`, `hash_pdf_bytes`
- `demo_signature`

Objetivo: reducir duplicación en vistas y facilitar tests unitarios futuros.
