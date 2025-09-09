# 🚀 Tailwind CSS en CMI - Rama `migracion-tailwind`

Base de estilos unificada con **Tailwind CSS + Flowbite + AlpineJS**. Bootstrap fue removido de los templates.

## 🎨 **Tecnologías agregadas:**

- Tailwind CSS v3
- Flowbite v3 (componentes interactivos)
- AlpineJS v3 (JS reactivo ligero)

## 📁 **Archivos importantes:**

### **Configuración:**
- `tailwind.config.js` - Configuración de Tailwind CSS
- `postcss.config.js` - Configuración de PostCSS
- `package.json` - Dependencias de Node.js
- `static/styles/input.css` - CSS de entrada para Tailwind
- `static/styles/tailwind.css` - CSS compilado (generado automáticamente)

### **Templates:**
- `templates/base_tailwind.html` - Template base con anti-flicker dark mode, toasts y navbar.

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

## 🧩 Patrones usados
- Filtro `add_class` en templates para aplicar clases Tailwind a widgets de Django.
- Anti-flicker de tema en `<head>` y toggle dark mode con Alpine.
- Componentes Flowbite solo si aportan interactividad (tooltips, dropdowns, etc.).

## 🔄 **Flujo de desarrollo:**

1. **Terminal 1:** `npm run build-css` (modo watch)
2. **Terminal 2:** `python manage.py runserver`
3. **Editar:** Cambiar clases en templates HTML
4. **Guardar:** Ctrl+S
5. **Automático:** Tailwind recompila
6. **Refrescar:** F5 en navegador

## 🎯 Estado de migración

- ✅ Base `base_tailwind.html`
- ✅ Autenticación y reseteo de contraseña migrados
- ✅ Listado de órdenes (Alpine + sort cliente)
- ✅ Informes y estudios con badges y botones Tailwind
- ✅ Eliminado Bootstrap en templates

## 📝 Notas importantes
- Modo desarrollo: `npm run build-css` (watch mode)
- Antes de deploy: `npm run build-css-prod` + `collectstatic`
- El CSS generado (`static/styles/tailwind.css`) se incluye para facilitar deploy.

## 🚀 **Próximos pasos:**

1. Migrar páginas principales a `base_tailwind.html`
2. Reemplazar componentes Bootstrap con DaisyUI/Flowbite
3. Optimizar y limpiar CSS no utilizado
4. Merge a main branch

---

Actualizado: 9 de septiembre de 2025  
Estado: 🟢 UI unificada en Tailwind
