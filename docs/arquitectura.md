# Arquitectura General

## Visión
Aplicación Django modular que gestiona usuarios, órdenes médicas y (en evolución) integración con servidor DICOM Orthanc para ingestión de estudios y generación de informes.

## Componentes
- Django (núcleo web / backend)
Apps internas: `usuarios`, `control_ordenes`, `portal_pacientes`, `estudios` (en evolución se sumará `informes`).
- Orthanc (servidor DICOM externo) en `http://localhost:8042`.
- Frontend: Tailwind + DaisyUI (migración desde Bootstrap en progreso).
- Base de datos: SQLite en desarrollo; previsto Postgres en producción.
- WhiteNoise para estáticos.
3. Django sincroniza (polling inicial o eventos) y/o consulta en vivo (fase inicial) y registra/obtiene Study.
4. Médico selecciona estudio, puede abrir visor OHIF (`/ohif/viewer?StudyInstanceUIDs=<UID>`) desde la lista UI.
5. Médico genera informe estructurado.
6. Sistema renderiza informe (HTML + PDF) y lo bloquea al finalizar.
2. Orthanc almacena y expone metadatos vía REST / DICOMweb.
3. Django sincroniza (polling inicial o eventos) y registra Study.
4. Médico selecciona estudio y genera informe estructurado.
5. Sistema renderiza informe (HTML + PDF) y lo bloquea al finalizar.
6. Auditoría registra acciones sobre informes.

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
