# App Gestión Pacientes (CMI)

Proyecto Django + TailwindCSS + DaisyUI para gestión de pacientes, órdenes, estudios e informes.

## 🧩 Stack principal
- Python / Django 5
- TailwindCSS 3 + DaisyUI + Flowbite
- Whitenoise (static files)
- SQLite (dev) / DATABASE_URL (prod via dj-database-url)
- Gunicorn (Procfile)

## 🚀 Arranque rápido (desarrollo)
```cmd
# 1. Crear / activar venv (si no existe)
python -m venv venv_gestion_pacientes
venv_gestion_pacientes\Scripts\activate

# 2. Dependencias
pip install -r requirements.txt
npm install

# 3. Variables de entorno (.env)
# Mínimo:
# SECRET_KEY=... 
# DEBUG=1
# ALLOWED_HOSTS=localhost,127.0.0.1
# EMAIL_HOST=... (opcional en dev)
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=...
# EMAIL_HOST_PASSWORD=...
# DEFAULT_FROM_EMAIL=...
# ORTHANC_BASE_URL=http://localhost:8042 (si usás Orthanc)

# 4. Migraciones
a python manage.py migrate

# 5. Superusuario (opcional)
python manage.py createsuperuser

# 6. Levantar entorno combinado (Django + Tailwind watch)
npm run dev
```
Abre:
- 🎨 Watch CSS (Tailwind + DaisyUI) – recompila al guardar
- 🚀 Servidor Django: http://127.0.0.1:8000/

Alternativas:
```cmd
npm run dev-css       # Solo watcher de estilos
npm run dev-windows   # Misma idea pero en dos ventanas separadas (batch)
```

## 📦 Scripts NPM clave
| Script | Qué hace |
|--------|----------|
| build-css | Compila (sin minificar) una vez |
| build-css-watch | Compila y observa cambios |
| dev-css | Alias del anterior |
| build-css-prod | Compila minificado para producción |
| dev | Watch CSS + runserver simultáneo (con concurrently) |
| collectstatic | Ejecuta collectstatic (Django) |
| build-and-collect | build-css + collectstatic |

## 🏗 Flujo diario simplificado
1. `npm run dev`
2. Editás templates / views / forms.
3. Refrescás el navegador (Ctrl+F5 si no ves cambios). Nada más.

## 🛠 Cuando reconstruir el CSS
Se hace solo (watch). Manualmente solo necesitas:
- Antes de deploy: `npm run build-css-prod` y luego `python manage.py collectstatic --noinput`.
- Si cambiás `tailwind.config.js`, reiniciá el watcher.

## 🌐 Deploy (ejemplo Heroku / similar)
```cmd
# Asegurate de tener las vars de entorno en el servicio
npm run build-css-prod
python manage.py collectstatic --noinput
# Procfile ya define: web: gunicorn config.wsgi --log-file -
```
Si usás render/fly/railway: mismo build step para CSS antes de servir.

## 🧪 Tests
Pendiente de ampliar. Placeholder: `python manage.py test`.

## 🗂 Estructura relevante
```
config/        # settings, urls
usuarios/      # app de usuarios (AUTH_USER_MODEL)
informes/      # informes médicos
control_ordenes/
estudios/
static/        # input.css -> tailwind.css generado
templates/     # templates globales y por app
```

## 🎨 Tailwind / DaisyUI
- Entrada: `static/styles/input.css`
- Salida generada: `static/styles/tailwind.css`
- Asegurate en tus templates de linkear la salida.
- Safelist en `tailwind.config.js` para colores comunes.

## 🌓 Dark Mode
Se controla con clase `dark` en `<html>` o `<body>` (darkMode: 'class'). DaisyUI maneja los themes.

## 🔐 Auth
- Modelo custom: `usuarios.Usuario`
- LOGIN_URL: `/usuarios/login/`
- LOGIN_REDIRECT_URL: `home`

## 🖼 Static & Media
- Static dev: `STATICFILES_DIRS = [static/]`
- Collect: salida en `staticfiles/`
- Whitenoise sirve estáticos en prod.
- Media: `media/` (configurado pero verificar rutas en templates/views para subir archivos si aplica).

## 🧾 Orthanc (si se integra)
Configurable con `ORTHANC_BASE_URL` (y potencialmente usuario/clave si se habilita auth básica).

## ❓ Problemas comunes
| Síntoma | Revisión |
|---------|----------|
| No carga estilos | ¿`npm run dev` activo? ¿link a tailwind.css correcto? Cache (Ctrl+F5) |
| Clase Tailwind no aparece | Clase construida dinámicamente (no literal) -> agregar a safelist |
| Cambié tailwind.config.js y no refleja | Reiniciar watcher (`Ctrl+C` y `npm run dev`) |
| Error collectstatic | Revisar permisos / variables de entorno / rutas STATIC_* |

## 📄 Licencia
Privado / interno (definir más adelante).

---
Cualquier mejora: editar este README y la doc en `docs/`.
