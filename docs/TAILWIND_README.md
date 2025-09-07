# 🚀 Migración a Tailwind CSS - Rama `migracion-tailwind`

Esta rama contiene la migración del proyecto a **Tailwind CSS + DaisyUI + Flowbite** para crear interfaces modernas y responsivas.

## 🎨 **Tecnologías agregadas:**

- **Tailwind CSS v3.4.0** - Framework de utilidades CSS
- **DaisyUI v5.0.50** - Sistema de componentes para Tailwind
- **Flowbite v3.1.2** - Componentes interactivos con JavaScript
- **AlpineJS v3** - JavaScript reactivo ligero

## 📁 **Archivos importantes:**

### **Configuración:**
- `tailwind.config.js` - Configuración de Tailwind CSS
- `postcss.config.js` - Configuración de PostCSS
- `package.json` - Dependencias de Node.js
- `static/styles/input.css` - CSS de entrada para Tailwind
- `static/styles/tailwind.css` - CSS compilado (generado automáticamente)

### **Templates:**
- `templates/base_tailwind.html` - Template base solo con Tailwind
	(Se removieron templates de demo de portal de pacientes)

## ⚡ **Comandos importantes:**

### **Instalación inicial:**
```bash
npm install
```

### **Desarrollo (modo watch):**
```bash
npm run build-css
```
*Mantiene Tailwind compilando automáticamente mientras desarrollas*

### **Producción:**
```bash
npm run build-css-prod
python manage.py collectstatic --noinput
```

### **Servidor Django:**
```bash
python manage.py runserver
```

## 🌐 **URLs de prueba:**

	(Se removieron URLs de demo del portal de pacientes)

## 🔄 **Flujo de desarrollo:**

1. **Terminal 1:** `npm run build-css` (modo watch)
2. **Terminal 2:** `python manage.py runserver`
3. **Editar:** Cambiar clases en templates HTML
4. **Guardar:** Ctrl+S
5. **Automático:** Tailwind recompila
6. **Refrescar:** F5 en navegador

## 🎯 **Migración gradual:**

- ✅ Base template con Tailwind (`base_tailwind.html`)
- ✅ Configuración de DaisyUI y Flowbite
- ✅ Modo oscuro automático
- ✅ Componentes responsivos
- 🔄 Migrar páginas existentes una por una
- 🔄 Reemplazar Bootstrap gradualmente

## 📝 **Notas importantes:**

- **Modo desarrollo:** Siempre usar `npm run build-css` (watch mode)
- **Antes de commit:** Ejecutar `npm run build-css-prod`
- **Archivos CSS:** El `tailwind.css` se incluye en el repo para deployment
- **Compatibilidad:** Funciona junto con Bootstrap temporalmente

## 🚀 **Próximos pasos:**

1. Migrar páginas principales a `base_tailwind.html`
2. Reemplazar componentes Bootstrap con DaisyUI/Flowbite
3. Optimizar y limpiar CSS no utilizado
4. Merge a main branch

---

**Rama creada:** 5 de agosto de 2025  
**Estado:** 🟢 Ready for development
