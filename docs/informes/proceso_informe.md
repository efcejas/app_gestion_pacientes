# Proceso de Informe Médico

## Estados
- draft: editable.
- final: PDF generado, bloqueado.
- annulled: requiere privilegio especial, conserva hash previo.

## Flujo
1. Médico abre Study sin Report final.
2. Completa formulario estructurado.
3. Guarda borrador (persistencia JSON).
4. Al finalizar:
   - Render HTML (plantilla).
   - Generar PDF (WeasyPrint u otro).
   - Calcular hash SHA256.
   - Guardar y bloquear.
5. Descarga / consulta readonly.

## Anulación
- Registra entrada en AuditLog.
- Conserva historial (hash previo + timestamp).

## Plantillas
`ReportTemplate` con placeholders: {{ hallazgos }}, {{ conclusiones }}, etc.

## Seguridad
- Solo autor edita borrador.
- Revisión futura (doble firma) opcional.

## Futuro
- Firma digital avanzada.
- Versionado de informes (historial editable).
