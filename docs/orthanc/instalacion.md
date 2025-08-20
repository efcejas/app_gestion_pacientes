# Documentación Proyecto CMI - Integración Orthanc + Django

## Paso 1: Instalación de Orthanc en Windows

### 1. Descarga
Se descargó Orthanc desde la página oficial:  
https://www.orthanc-server.com/download.php  
Elegir el paquete standalone (ZIP) para portabilidad.

### 2. Instalación / Ubicación
- Se eligió descomprimir en `C:\Orthanc\` para evitar problemas de permisos.
- No requiere instalador; estructura portable.

### 3. Ejecución inicial
- Se ejecutó `Orthanc.exe` para iniciar el servidor.
- URL probada en el navegador: `http://localhost:8042`  
  Usuario: `admin` / Contraseña: `admin123` (cambiar en cuanto sea posible).

### 4. Plugins instalados / habilitados
Se seleccionaron los siguientes componentes:
- Orthanc server (base)
- Basic Orthanc Web Viewer
- OHIF plugin for Orthanc (visualización avanzada)
- Orthanc Explorer 2 user interface (UI moderna)
- DICOMweb support
- General plugins (autorización, conectividad, etc.)

### 5. Verificación básica
- Orthanc abrió correctamente en el navegador.
- Comprobado: se subió un archivo `.dcm` y se validó que apareciera un Study UID.

### 5.1 Registro de versión y hash (reproducibilidad)
Documentar la versión exacta y el checksum del artefacto descargado permite reconstruir el entorno y detectar corrupción o sustitución del archivo.

#### a) Datos a registrar
Completar y conservar este bloque (idealmente versionado en Git):

```
Orthanc
  Versión instalada: 1.12.9
  Fecha de descarga: 2025-08-16
  Fuente oficial: https://www.orthanc-server.com/download.php
  Nombre de archivo: OrthancInstaller-Win64-25.8.1.exe
  SHA256 (local calculado): 7F70C2B49474652BF7A9CEF33F5125B7518D5BF9FBB23B0C852D1D5C55620DD6
  SHA256 (publicado oficial): [PENDIENTE - buscar en web oficial]
  Coincidencia verificada: [PENDIENTE]
```

#### b) Cómo obtener la versión
Opciones:
1. Interfaz web: Menú "About" / "Acerca de" (muestra versión del core y plugins).
2. Línea de comandos (si disponible): `Orthanc.exe --version` (algunas distribuciones lo soportan) o revisar el archivo `Orthanc.exe` propiedades / Detalles.
3. Archivo `CHANGELOG` dentro del ZIP (si provisto).

#### c) Calcular SHA256 en PowerShell (Windows)
Ejecutar (ajustar ruta y nombre de archivo):
```
```powershell
Get-FileHash -Algorithm SHA256 "C:\Orthanc\_artefactos\Orthanc-win64-<version>.zip" | Select-Object -ExpandProperty Hash
```
```

Copiar el valor y pegarlo en el bloque de datos (campo "SHA256 (local calculado)").

#### d) Obtener SHA256 oficial
En la página de descargas suele publicarse un checksum (o un archivo `.sha256`). Registrar ese valor en "SHA256 (publicado oficial)".

#### e) Verificación
- Comparar ambos hashes (deben ser idénticos). 
- Si difieren: volver a descargar y DESCARTAR el archivo sospechoso.

#### f) Sugerencia de archivado interno
- Guardar el ZIP original en un directorio controlado (`C:\Orthanc\_artefactos\`).
- (Opcional) Mantener un archivo `docs/orthanc/CHECKSUMS.md` listando histórico de versiones.

#### g) Ejemplo (rellenar cuando se disponga de datos)
```
Orthanc
  Versión instalada: 1.12.9
  Fecha de descarga: 2025-08-16
  Fuente oficial: https://www.orthanc-server.com
  Nombre de archivo: Orthanc-win64-1.12.3.zip
  SHA256 (local calculado): 2F0E...<truncado>
  SHA256 (publicado oficial): 2F0E...<truncado>
  Coincidencia verificada: SI
```

> Hasta completar los campos, mantener la tarea como pendiente en la checklist.

#### h) Estado actual
- Hash local obtenido (PowerShell `Get-FileHash`).
- Falta capturar hash oficial publicado y comparar.
- No marcar como verificada la coincidencia hasta completar la comparación.

#### i) Firma digital (Authenticode)
La ejecución de `Get-AuthenticodeSignature` sobre el instalador devolvió `Status: NotSigned`. Implicaciones:
1. El binario no está firmado con certificado Authenticode, por lo que Windows no puede validar procedencia.
2. Aumenta la importancia de la verificación de integridad (hash SHA256) y de descargar exclusivamente desde la URL oficial mediante HTTPS.

Mitigaciones recomendadas:
- Conservar captura o salida del comando como evidencia (`docs/orthanc/evidencias/firmas/2025-08-17-authenticode.txt`).
- Verificar regularmente si versiones futuras incorporan firma; si aparece firma, documentar el emisor (Subject) y huella (Thumbprint).
- Mantener aislado el archivo original (sólo lectura) y restringir permisos NTFS al grupo de administradores.
- (Opcional) Escanear el instalador con al menos dos motores AV/EDR corporativos antes de su uso.

Comando usado:
```
Get-AuthenticodeSignature "C:\Users\efcce\Downloads\OrthancInstaller-Win64-25.8.1.exe" | Format-List *
```

Resultado clave: `Status : NotSigned`.

---
## Paso 2: Cargar un estudio DICOM de prueba en Orthanc

### Subida manual desde la interfaz web
1. Abrir Orthanc Explorer en el navegador:  `http://localhost:8042`
2. En el menú lateral, seleccionar **Cargar**.
3. Elegir un archivo con extensión `.dcm`.

### Fuente de archivos de prueba
- Los archivos DICOM de prueba se pueden descargar de:  
  https://www.dicomlibrary.com/  
  (usar el botón *Download anonymized DICOM*).

### Verificación
- Una vez cargado, el estudio aparece listado en **Estudios locales**.
- Al hacer clic sobre el estudio, se abre el visor (OHIF / Stone).
- Se confirma que Orthanc:
  - Puede recibir archivos DICOM.
  - Los almacena en su base local.
  - Permite visualizar las imágenes.

✅ Con esto, Orthanc ya funciona como un PACS mínimo en entorno local.

---
## Configuración Recomendada Posterior

### 6. Archivo de configuración sugerido `Orthanc.json`
Ubicarlo (por ejemplo) en `C:/Orthanc/Configuration/Orthanc.json` y ajustar rutas según necesidad.

```json
{
  "Name": "Orthanc-CMI",
  "StorageDirectory": "C:/Orthanc/Storage",
  "IndexDirectory": "C:/Orthanc/Index",
  "HttpServerEnabled": true,
  "HttpPort": 8042,
  "DicomServerEnabled": true,
  "DicomPort": 4242,
  "RemoteAccessAllowed": false,
  "AuthenticationEnabled": true,
  "RegisteredUsers": { "admin": "CAMBIAR_PASSWORD" },
  "DicomWeb": { "Enable": true, "Root": "/dicom-web/" },
  "Plugins": "C:/Orthanc/Plugins",
  "OverwriteInstances": false,
  "ExecuteLuaEnabled": false,
  "Verbose": false,
  "ConcurrentJobs": 4
}
```

Notas:
- Cambiar la contraseña por defecto inmediatamente.
- Mantener `RemoteAccessAllowed` en `false` mientras sea solo ambiente local.
- Ajustar rutas si se mueve el directorio base.

### 7. Próximos pasos inmediatos
1. Cambiar password del usuario `admin` en config.
2. (En curso) Documentar versión + hash (ver sección 5.1).
3. Definir si se permitirá acceso DICOM externo (configurar firewall/puertos).
4. Preparar variables de entorno en Django para integración (ver `../integracion/orthanc_sync.md`).

### 8. Checklist de salud inicial
| Ítem | Estado |
|------|--------|
| Acceso web 8042 responde | ✅ |
| Credenciales distintas a default | ☐ (pendiente) |
| Archivo `Orthanc.json` creado | ☐ |
| Subida de estudio de prueba | ✅ |
| Verificación OHIF viewer | ✅ |
| Versión + hash documentados | ☐ (falta hash oficial)

Actualizar esta tabla a medida que se completen los pasos.

---
## Changelog
- 2025-08-16: Se integró documentación detallada de instalación inicial y plantilla de configuración.
- 2025-08-16: Añadida sección 5.1 para registro de versión y hash SHA256 de Orthanc.
  - 2025-08-17: Se registró la versión, falta hash SHA256 de Orthanc.
  - 2025-08-17: Hash local calculado almacenado (pendiente comparar con oficial).
  - 2025-08-17: Documentada ausencia de firma Authenticode y mitigaciones.
