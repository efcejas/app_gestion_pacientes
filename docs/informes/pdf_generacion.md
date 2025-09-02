# Generación de PDF de Informes (Estado Actual)

## Resumen
Al finalizar un informe (cambio de `draft` a `final`) se genera automáticamente un PDF a partir del HTML almacenado en el campo `contenido` del modelo `Report`.

## Componentes
- Modelo `Report` (`informes.models`): campo `pdf_file` (`FileField`) almacena el PDF generado (`media/reportes_pdf/`).
- Campo `firma_digital` (demo) almacenando hash SHA256 truncado del contenido + autor (prefijo `FD-`).
- Vista `crear_o_editar`: si el usuario pulsa finalizar, genera y adjunta el PDF antes de redirigir.
- Vista `finalizar`: también soporta finalizar y generar PDF (flujo alternativo directo).
- Utilidad `informes/pdf_utils.py` con `render_report_to_pdf()` usando `xhtml2pdf`.
- Plantilla PDF: `templates/informes/pdf/base_report.html` (layout actualizado: encabezado simplificado y banda 3 columnas; fechas `dd-mm-YYYY`).
- Template visualización final: `templates/informes/ver_final.html` muestra contenido HTML y enlaces "Ver PDF" / "Descargar".

## Librería
Se utiliza `xhtml2pdf==0.2.15`. Limitaciones: soporte CSS parcial. Para calidad tipográfica superior se evaluará migrar a WeasyPrint.

## Flujo Detallado (Finalización)
1. Usuario edita borrador.
2. Envía formulario con acción `finalizar`.
3. Validación: contenido no vacío.
4. Estado => `final`.
5. Si no existe, se genera firma digital demo (`FD-<hash>`).
6. `render_report_to_pdf(report)`:
   - Render de plantilla base.
   - Conversión a PDF.
   - Guarda en `report.pdf_file` con nombre `reporte_<id>.pdf`.
7. Redirección a `informes:ver_final`.

## Errores y Logging
- Si xhtml2pdf falla, se guarda igual el estado `final` y se muestra warning.
- Logger (`informes.pdf_utils`) registra advertencia.

## Decisiones Tomadas
- Se eliminó iframe directo por problemas de visualización; se usa apertura en pestaña nueva.
- `X_FRAME_OPTIONS = 'SAMEORIGIN'` ya no es estrictamente necesario; puede eliminarse.
- Estilos mínimos para compatibilidad PDF.
- Rediseño de plantilla: se quitó título redundante y se centralizó la firma.
- Eliminados: vista de previsualización, acción admin y comando de regeneración tras estabilizar layout.

## Pendientes / Backlog
| Item | Prioridad | Notas |
|------|-----------|-------|
| Hash SHA256 del PDF | Alta | Guardar en campo nuevo `pdf_hash` |
| Plantillas dinámicas | Alta | Modelo `ReportTemplate` |
| Adendas / versionado | Media | Requiere modelo histórico |
| Firma digital | Media | Depende de PKI corporativa |
| Migrar a WeasyPrint | Media | Mejor soporte CSS / fuentes |
| Envío por email del PDF | Media | Requiere configurar backend correo |
| Endpoint API descarga segura | Baja | Para portal pacientes |

## Seguridad
- Solo staff autor puede editar en `draft`.
- Estado `final` bloquea cambios (campo readonly, validación en vista).
- No se valida todavía sanitización profunda del HTML (`contenido`); confiar en personal interno.

## Próximos Pasos Recomendados
1. Añadir hash y almacenar en DB para integridad (incluyendo PDF final).
2. Crear modelo `ReportTemplate` y UI de selección.
3. Migrar a motor más avanzado (WeasyPrint) si se requiere mejor CSS.
4. Implementar adendas (nueva tabla `ReportVersion`).

---
Actualizar este documento con cada cambio significativo del flujo de generación de PDFs.
