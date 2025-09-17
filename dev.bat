@echo off
setlocal

REM Utilidad: ejecutar migraciones en Heroku
if /I "%1"=="heroku-migrate" goto heroku_migrate

echo 🎨 Iniciando modo desarrollo Tailwind + DaisyUI
echo.
echo 💡 Este script:
echo    ✅ Vigila cambios en CSS y templates
echo    ✅ Recompila automáticamente Tailwind + DaisyUI  
echo    ✅ Ejecuta collectstatic cuando es necesario
echo    ✅ Inicia el servidor Django
echo.
echo 🚀 Abriendo ventanas de desarrollo...
echo.

REM Abrir primera ventana para CSS watch
start cmd /k "title CSS Watch - Tailwind + DaisyUI && cd /d "%~dp0" && npm run build-css-watch"

REM Esperar un poco
timeout /t 2 /nobreak >nul

REM Abrir segunda ventana para Django server  
start cmd /k "title Django Server && cd /d "%~dp0" && set EMAIL_HOST_PASSWORD=& set OVERRIDE_PWD=& python manage.py runserver"

echo ✅ Ventanas de desarrollo abiertas!
echo.
echo 📝 Instrucciones:
echo    - Ventana 1: CSS Watch (recompila automáticamente)
echo    - Ventana 2: Django Server (http://127.0.0.1:8000)
echo    - Cuando hagas cambios importantes, ejecuta: npm run collectstatic
echo.
echo 💡 Para cerrar todo: Ctrl+C en ambas ventanas
pause

goto :eof

:heroku_migrate
echo 🚀 Ejecutando migraciones en Heroku (gestion-servicio-alj)...
heroku run -a gestion-servicio-alj -- python manage.py migrate
if errorlevel 1 (
	echo ❌ Error ejecutando migraciones en Heroku.
	exit /b 1
) else (
	echo ✅ Migraciones aplicadas correctamente en Heroku.
)
goto :eof
