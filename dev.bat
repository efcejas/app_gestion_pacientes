@echo off
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
start cmd /k "title Django Server && cd /d "%~dp0" && python manage.py runserver"

echo ✅ Ventanas de desarrollo abiertas!
echo.
echo 📝 Instrucciones:
echo    - Ventana 1: CSS Watch (recompila automáticamente)
echo    - Ventana 2: Django Server (http://127.0.0.1:8000)
echo    - Cuando hagas cambios importantes, ejecuta: npm run collectstatic
echo.
echo 💡 Para cerrar todo: Ctrl+C en ambas ventanas
pause
