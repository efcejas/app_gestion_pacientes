# Proceso de Informe Médico

## Estados
- draft: editable.
- final: bloqueado (PDF generado, hashes calculados, snapshot capturado).

Planificado (no implementado aún):
- annulled: requiere privilegio especial, mantendrá referencia a versión final previa.

## Flujo (estado actual vs diseño original)
Actual implementado (2025-09-02):
1. Médico (staff) abre un estudio usando `study_internal_id` Orthanc.
2. El sistema toma el último `Report` por `study_internal_id`:
   - Si no existe, crea versión 1 (draft).
   - Si existe y está `draft`, reutiliza.
   - Si el último está `final`, crea nueva versión (`version = last.version + 1`).
3. Edición de `contenido` (HTML libre) con sanitización `bleach` en cada guardado.
4. Guardar borrador crea log `draft_save` (sin pdf_hash).
5. Finalizar valida no vacío, calcula `contenido_hash`, genera firma demo si falta, persiste snapshot DICOM (nombre, ID, sexo, fechas, descripción, accession), crea log `finalize` (pdf_hash vacío todavía).
6. Se genera PDF (xhtml2pdf) con plantilla `base_report.html`, se calcula `pdf_hash` y se actualiza log `finalize` con `pdf_hash` y tamaño en bytes.
7. Vista final (`ver_final`) muestra snapshot congelado y enlaces PDF.

Actualización 2025-09-05:
- Refactor de hashing, firma demo y sanitización a `informes/utils.py`.
- Búsqueda de logo robusta (múltiples rutas y variantes de nombre) antes de generar PDF.

Layout PDF: encabezado con logo parametrizable y datos institución, banda con datos paciente/estudio y firma DEMO al pie (texto “demo, sin validez legal”).

Detección de logo: ver sección en `docs/arquitectura.md` (Gestión de Logo en PDF).

Pendiente:
- Formulario estructurado / plantillas dinámicas.
- Doble firma / revisión.
- Estado `annulled` y trazabilidad cruzada.
- Firma digital avanzada (PKI / TSA / OCSP).

## Versionado y (futura) Anulación
Cada versión final se conserva intacta. Una nueva modificación crea versión nueva. La anulación futura agregará estado y log dedicado sin alterar PDFs previos.

## Plantillas
Implementado: `base_report.html` (minimal, estilos inline compatibles xhtml2pdf). Versionada lógicamente vía `REPORT_TEMPLATE_VERSION` en settings.
Planificado: modelo `ReportTemplate` con placeholders y render dinámico + persistencia de la versión usada en cada informe.

## Seguridad
- Solo autor edita borrador.
- Sanitización HTML para reducir XSS guardado.
- Hashes garantizan integridad básica del contenido y del PDF.
- Firma DEMO evita suplantar un sello real (marcada explícitamente).

## Futuro (prioridad sugerida)
1. Comando de backfill (hashes/snapshots para informes históricos si los hubiera).
2. CssSanitizer para limitar estilos a un subconjunto seguro.
3. Test de versionado (creación de versión 2 tras finalizar versión 1).
4. Botón diff entre versiones (HTML diff simplificado server-side).
5. Estado `annulled` + log dedicado.
6. Firma digital robusta (PKCS#7 / PAdES) + timestamp externo.
7. Modelo `Study` + normalización de `Patient` para reducir llamadas a Orthanc.
8. ReportTemplate + selección al crear.
9. Endpoint API readonly para integraciones externas (JSON + enlace PDF).
10. Comprobación de determinismo (regenerar en memoria y comparar nuevos hashes, o documentar fuentes de variación: timestamps, fonts, orden CSS).

## Operaciones de mantenimiento
Previsto añadir:
- `backfill_report_integrity` (recalcula hashes y crea logs faltantes para registros antiguos).
- `export_report_version --id <ID>` (exporta JSON con snapshot + hashes + base64 PDF para auditoría externa).
