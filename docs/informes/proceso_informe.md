# Proceso de Informe Médico

## Estados (implementación actual)
- draft: editable.
- final: bloqueado (se genera PDF al cambiar a este estado).

Estado planificado pero NO implementado aún:
- annulled: requerirá privilegio especial y conservará hash previo.

## Flujo (estado actual vs diseño original)
Actual implementado:
1. Médico (staff) abre un estudio (Orthanc) → `crear_o_editar` hace `get_or_create` de `Report` por `study_instance_uid`.
2. Edita campo HTML libre `contenido` (no hay formulario estructurado todavía).
3. Guarda borrador (estado `draft`).
4. Al presionar finalizar:
   - Se valida que `contenido` no esté vacío.
   - Se cambia a estado `final`.
   - Se renderiza plantilla PDF (`templates/informes/pdf/base_report.html`) con xhtml2pdf.
   - Se guarda archivo en `media/reportes_pdf/` (`pdf_file`).
   - Redirige a vista readonly (`ver_final`).
5. En vista final se muestra el contenido HTML y botones “Ver PDF / Descargar PDF”.

Layout PDF actual: encabezado con logo + institución y banda de datos del paciente (3 columnas: Paciente/DNI | Nac./Estudio | Creado/Finalizado) y firma centrada al pie.

Pendiente (diseño original aún no implementado):
- Formulario estructurado / plantillas dinámicas.
- Hash de integridad (SHA256) del contenido y del PDF.
- Doble firma / revisión.
- Anulación / versionado histórico.

## Anulación
- Registra entrada en AuditLog.
- Conserva historial (hash previo + timestamp).

## Plantillas
Implementado: `base_report.html` mínima (estilos inline, sin Tailwind).
Planificado: modelo `ReportTemplate` con placeholders (`{{ hallazgos }}`, `{{ conclusiones }}`, etc.) y merge automatizado.

## Seguridad
- Solo autor edita borrador.
- Revisión futura (doble firma) opcional.

## Futuro
- Firma digital avanzada.
- Versionado de informes (historial editable / adendas).
- Motor de plantillas parametrizadas.
- Hash y sellado de tiempo.
- Envío por email del PDF final.

## Operaciones de mantenimiento
### Regenerar PDFs existentes
Cuando se modifica la plantilla PDF o se añade lógica (ej. firma), se pueden regenerar los PDFs de informes finalizados.

Comando management:
`python manage.py regenerar_reportes_pdf --force`

Opciones:
- `--id <ID>` procesa solo un informe.
- `--force` regenera aunque ya exista `pdf_file`.
- `--sin-firma` evita calcular firma demo (solo PDF).
- `--limit N` limita la cantidad.

Admin Django: seleccionar informes finalizados y usar la acción "Regenerar PDF (informes final)".
