const { spawn } = require('child_process');
const chokidar = require('chokidar');
const path = require('path');

console.log('🎨 Iniciando vigilancia de archivos CSS y templates...');

// Vigilar archivos de entrada
const watcher = chokidar.watch([
    './static/styles/input.css',
    './templates/**/*.html',
    './tailwind.config.js'
], {
    ignored: /(^|[\/\\])\../,
    persistent: true
});

let isBuilding = false;

// Función para ejecutar comando
function runCommand(command, args = [], description) {
    return new Promise((resolve, reject) => {
        console.log(`🔧 ${description}...`);
        const process = spawn(command, args, { 
            shell: true,
            stdio: 'inherit'
        });
        
        process.on('close', (code) => {
            if (code === 0) {
                console.log(`✅ ${description} completado`);
                resolve();
            } else {
                console.log(`❌ Error en ${description}`);
                reject();
            }
        });
    });
}

// Función para rebuild completo
async function rebuildCSS() {
    if (isBuilding) return;
    
    isBuilding = true;
    try {
        // 1. Compilar CSS
        await runCommand('npx', ['tailwindcss', '-i', './static/styles/input.css', '-o', './static/styles/tailwind.css'], 'Compilando CSS');
        
        // 2. Recoger archivos estáticos
        await runCommand('python', ['manage.py', 'collectstatic', '--noinput'], 'Recolectando archivos estáticos');
        
        console.log('🎉 Rebuild completo terminado!\n');
    } catch (error) {
        console.log('❌ Error durante el rebuild\n');
    } finally {
        isBuilding = false;
    }
}

// Ejecutar build inicial
rebuildCSS();

// Vigilar cambios
watcher
    .on('change', (path) => {
        console.log(`📝 Archivo modificado: ${path}`);
        rebuildCSS();
    })
    .on('add', (path) => {
        console.log(`➕ Archivo agregado: ${path}`);
        rebuildCSS();
    });

console.log('👀 Vigilando cambios en archivos CSS y templates...');
console.log('Presiona Ctrl+C para detener');
