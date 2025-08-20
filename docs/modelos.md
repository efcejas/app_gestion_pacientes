# Diseño de Modelos (Propuesta)

## Existentes
- Usuario (custom, extiende AbstractUser, campo `rol`).
- OrdenMedica (médico, identificador_paciente, fechas, validez).

## Nuevos (propuestos)
### Patient
- id (Auto)
- external_id / identificador_hash (str)
- nombre (nullable si anonimizado)
- created_at / updated_at

### Study
- id
- study_instance_uid (unique)
- patient (FK Patient)
- modality (str)
- performed_datetime (datetime)
- accession_number (nullable)
- source ("orthanc")
- raw_metadata (JSONField)
- status (enum: pending, ready, reported)
- created_at / updated_at

### Series (opcional si se necesita granularidad)
- id
- study (FK Study)
- series_instance_uid (unique)
- body_part (nullable)
- raw_metadata (JSONField)

### Instance
- id
- series (FK Series)
- sop_instance_uid (unique)
- dicom_orthanc_id (identificador interno de Orthanc)
- thumbnail_path (nullable)
- raw_metadata (JSONField)

### Report
- id
- study (FK Study, unique constraint 1:1 por ahora)
- medico (FK Usuario)
- status (draft, final, annulled)
- content_json (JSONField)
- html_rendered (TextField)
- pdf_file (FileField)
- hash_pdf (str)
- final_at (datetime nullable)
- created_at / updated_at

### ReportTemplate (si se implementa)
- id
- nombre
- especialidad
- body (plantilla con placeholders)

### AuditLog
- id
- actor (FK Usuario nullable si sistema)
- action (str)
- object_type (str) / object_id
- metadata (JSONField)
- created_at

## Relaciones Clave
- Patient 1..n Study
- Study 1..n Series 1..n Instance
- Study 1..1 Report (fase inicial)

## Notas
- `raw_metadata` preserva flexibilidad ante cambios DICOM.
- `status` de Study se deriva: reported si Report final existe.
- Se puede omitir Series inicialmente (Instance referenciando directo Study).
- Estado actual (2025-08-19): UI consume Orthanc en vivo; aún no se persiste `Study` ni `Report`. Próximo paso: materializar modelo `Study` (clave `study_instance_uid`) y `Report` 1:1; `AccessionNumber` opcional editable si falta.
