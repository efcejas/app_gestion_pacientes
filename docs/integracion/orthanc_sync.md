# Plan de Integración Orthanc ↔ Django

## Objetivo
Ingerir estudios DICOM desde Orthanc, registrar metadatos en Django y habilitar la generación de informes.

## Estrategia Fase 1 (Polling)
1. Management command `sync_orthanc_studies`.
2. Consultas REST:
   - GET /studies
   - GET /studies/{id}/shared-tags
   - GET /studies/{id}/instances
3. Idempotencia por `StudyInstanceUID`.
4. Guardar metadatos JSON crudos.

## Fase 2 (Eventos / Webhook)
- Endpoint Django `/orthanc/events/`.
- Orthanc postea cambios (requires plugin/ajuste de config).
- Cola / tarea asíncrona para ingestión pesada.

## Variables de entorno
```
ORTHANC_BASE_URL=http://localhost:8042
ORTHANC_USER=admin
ORTHANC_PASSWORD=... (no commitear)
```

## Estructura de Código (propuesta)
```
app_gestion_pacientes/
  integraciones/
    __init__.py
    orthanc/
      __init__.py
      client.py      # Llamados HTTP
      parser.py      # Normalización opcional
      service.py     # Orquestación ingestión
      exceptions.py
  estudios/         # Nueva app futura
    models.py
    services.py
```

## Campos mínimos del Study
- UID
- Paciente (o hash)
- Modalidad
- Fecha/hora performance
- AccessionNumber (si existe)
- raw_metadata

## Flujo Polling
1. Obtener lista de studies.
2. Para cada uno no registrado → detalles + registrar.
3. Marcar timestamp de última ejecución (cache/archivo simple).

## Métricas (recopilar luego)
- Nuevos estudios ingeridos.
- Duplicados ignorados.
- Errores de autenticación / red.

## Riesgos Iniciales
- Volumen grande → optimizar luego.
- Campos faltantes → usar defaults y loggear.

## Próximo Paso
Implementar esqueleto de `client.py` y modelos básicos.

---
## Estado Actual (2025-08-19)

Se implementó una integración inicial basada en vistas funcionales y un cliente simple (`estudios/services.py`):

### Cliente Orthanc (`OrthancClient`)
Métodos disponibles:
- `list_studies()` → IDs internos Orthanc
- `get_study_metadata(study_id)` → incluye `MainDicomTags.StudyInstanceUID`
- `get_study_shared_tags(study_id)` → tags básicos (PatientName, etc.)
- `list_series_in_study(study_id)`
- `list_instances_in_series(series_id)`
- `get_series_metadata(series_id)`
- `get_instance_metadata(instance_id)`

Uso actual en UI: N+1 (lista IDs y para cada uno consulta tags). Optimizable luego usando QIDO-RS.

### App `estudios`
Rutas jerárquicas creadas:
```
/estudios/                      (lista_estudios)
/estudios/<study_id>/           (detalle_estudio)
/estudios/<study_id>/series/    (lista_series)
/estudios/<study_id>/series/<series_id>/instances/ (lista_instancias)
/estudios/instances/<instance_id>/  (detalle_instancia)
```

Templates básicos en `templates/estudios/` para exploración de la jerarquía.

### Pendiente inmediato
1. Incluir `StudyInstanceUID` y `AccessionNumber` en lista (requiere `get_study_metadata`).
2. Construir URL OHIF: `/ohif/viewer?StudyInstanceUIDs=<UID>` (abrir nueva pestaña).
3. Añadir botón "Informar" (placeholder) → futura creación de `Report`.
4. Definir estrategia caché (evitar exceso de requests en listas grandes).

### Riesgos / Consideraciones
- Latencia por múltiples llamadas secuenciales.
- Campos faltantes (AccessionNumber) requieren fallback UI.
- Ausencia de paginación si crece el volumen.

### Roadmap Corto (próximas iteraciones)
| Iteración | Entrega | Notas |
|-----------|---------|-------|
| 1 | Enriquecer lista con UID + Accession + botones OHIF/Informar | Mantener N+1 temporal |
| 2 | Modelo `Study` + `Report` mínimo y migraciones | Persistir metadatos clave |
| 3 | Comando `sync_orthanc_studies` (polling básico) | Idempotencia por UID |
| 4 | Cache / QIDO-RS para reducir N+1 | Evaluar DICOMweb |
| 5 | Flujo informe (draft→final) + PDF | Auditoría básica |

### Variables de entorno efectivas
```
ORTHANC_BASE_URL=http://localhost:8042
ORTHANC_USERNAME=admin
ORTHANC_PASSWORD=********
```

### Decisiones abiertas (marcar antes de modelo)
- ¿Un informe por estudio o múltiples? (actual propuesta: 1:1)
- ¿Requerir AccessionNumber obligatorio? (si falta → editable manual)
- Estados definitivos del informe (draft, final, annulled ?)

---
