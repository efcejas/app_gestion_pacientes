# Arquitectura General

## Visión
Aplicación Django modular que gestiona usuarios, órdenes médicas e integra un servidor DICOM Orthanc para ingestión de estudios y generación de informes clínicos.

## Componentes
- Django (núcleo web / backend)
- Apps internas: `usuarios`, `control_ordenes`, `portal_pacientes`, `estudios` (en evolución se sumará `informes`).
- Orthanc (servidor DICOM) en `http://localhost:8042`.
- Frontend: Tailwind + DaisyUI (migración desde Bootstrap en progreso).
- Base de datos: SQLite (dev) → Postgres (prod previsto).
- WhiteNoise para estáticos.

## Flujo alto nivel
1. Equipo de ecografía envía estudio DICOM a Orthanc.
2. Orthanc almacena y expone metadatos vía REST / DICOMweb.
3. Django sincroniza (polling/eventos) y/o consulta en vivo en fase inicial.
4. Médico abre estudio en OHIF (`/ohif/viewer?StudyInstanceUIDs=<UID>`).
5. Se genera informe (draft → final) asociado al Study.
6. Render PDF y bloqueo de informe.
7. Auditoría registra acciones.

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

## Notas recientes (2025-08-20)
- Cliente Orthanc con cache LRU para resolver `StudyInstanceUID`.
- Paquete `templatetags/estudios_filters.py` para formato seguro de valores vacíos.
