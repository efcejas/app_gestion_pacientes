# Modelos - Estado Actual y Evolución

## Implementados en el código

### Usuario (`usuarios.Usuario`)
Extiende `AbstractUser`. Campos estándar + banderas staff.

### Report (`informes.Report`)
Representa un informe médico vinculado a un estudio en Orthanc mediante:
- `study_internal_id`: ID interno Orthanc (string) indexado.
- `study_instance_uid`: UID DICOM (no unique ahora para permitir versiones).
- `version`: entero secuencial (constraint de unicidad compuesta `(study_internal_id, version)`).
- `autor`: FK Usuario (PROTECT).
- `contenido`: HTML (sanitizado con bleach al guardar/finalizar).
- `estado`: `draft` | `final`.
- `pdf_file`: archivo PDF generado al finalizar.
- `firma_digital`: firma DEMO (hash truncado, sin validez legal).
- `contenido_hash`: SHA256 del HTML final (inmutable tras finalización).
- `pdf_hash`: SHA256 del binario PDF.
- `study_snapshot`: JSON inmutable de metadata paciente/estudio capturada al finalizar.
- Timestamps `creado` / `actualizado`.

Indices: por `study_internal_id`, `estado`.
Constraint: UniqueConstraint(`study_internal_id`, `version`).

Semántica de versionado: cada vez que un informe final existe y se requiere una nueva modificación, se crea una nueva fila con `version = versión_anterior + 1` en estado `draft`.

### LogInforme (`informes.LogInforme`)
Registro inmutable de eventos clave por informe:
- `report`: FK → Report.
- `accion`: `draft_save` | `finalize`.
- `usuario`: actor.
- `timestamp`: auto.
- `contenido_hash`, `pdf_hash`: valores conocidos en el momento (pdf_hash se completa luego de generar PDF y se actualiza el último log `finalize`).
- `report_version`: copia del número de versión del Report asociado.
- `template_version`: versión declarada en settings (`REPORT_TEMPLATE_VERSION`).
- `pdf_size`: bytes del PDF al finalizar.

Uso: auditoría y trazabilidad forense (qué, quién, cuándo y con qué artefactos).

## Sanitización de Contenido
Se usa `bleach` con whitelist de tags: `p, br, strong, em, ul, ol, li, h1..h4, blockquote, span, u, sub, sup` y atributo `style` solo en `span`. (Pendiente: restringir CSS permitido con `CssSanitizer`).

## Flujo de Versionado (resumen)
1. Si existe un Report `draft` para `study_internal_id`, se reutiliza.
2. Si el último Report está `final`, crear nueva fila con `version = last.version + 1`.
3. Guardar borrador = crea log `draft_save`.
4. Finalizar:
	- Sanitiza contenido.
	- Calcula `contenido_hash` y firma demo si falta.
	- Guarda snapshot si no existía.
	- Crea log `finalize` (sin `pdf_hash` aún).
	- Genera PDF → calcula `pdf_hash` → actualiza campo en Report y completa log (pdf_hash + pdf_size).

## Diferencias vs Diseño Inicial Propuesto
- Se pospone la materialización de modelos `Patient`, `Study`, `Series`, `Instance`: por ahora se consulta Orthanc en vivo y se almacena un snapshot en `Report` final.
- `AuditLog` genérico reemplazado por un modelo específico `LogInforme` más directo para las necesidades actuales.
- Se prioriza integridad (hashes, snapshot) y versionado mínimo antes de introducir plantillas parametrizadas.

## Próximos Cambios Potenciales
- Modelo `Study` para dejar de depender del live call en vistas (uid + accession + caching).
- Normalizar paciente (`Patient`) y evitar duplicación en snapshots.
- Introducir estado `annulled` con lógica de trazabilidad y bloqueo extra.
- Motor de plantillas (`ReportTemplate`).
- Firma digital avanzada con sellado de tiempo.
- Endpoints/acciones para comparar versiones (diff HTML y metadatos).
