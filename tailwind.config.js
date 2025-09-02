/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // habilita control manual con la clase 'dark' en <html> o <body>
  content: [
    './templates/**/*.html',
    './*/templates/**/*.html',
    './static/js/**/*.js',
    './node_modules/flowbite/**/*.js'
  ],
  safelist: [
    // Mantener utilidades de color comunes por patrón y variantes
    {
      pattern: /(bg|text|border|ring)-(lime|blue|cyan|emerald|green|red|gray)-(100|200|300|400|500|600|700|800|900)/,
      variants: ['hover', 'focus', 'active'],
    },
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  require('flowbite/plugin'),
  require('@tailwindcss/typography')
  ],
  // Configuración de DaisyUI
  daisyui: {
    themes: [
      // Tema personalizado principal
      {
        app: {
          primary: '#1d4ed8',
          secondary: '#9333ea',
          accent: '#0d9488',
          neutral: '#1f2937',
          'base-100': '#ffffff',
          info: '#0ea5e9',       // Color para badge-info
          success: '#10b981',    // badge-success
          warning: '#f59e0b',    // badge-warning
          error: '#ef4444',      // badge-error
        },
      },
      "light",
      "dark",
      "cupcake",
      "synthwave",
      "retro",
      "cyberpunk",
      "valentine",
      "halloween",
      "garden",
      "forest",
      "aqua",
      "lofi",
      "pastel",
      "fantasy",
      "wireframe",
      "black",
      "luxury",
      "dracula",
      "cmyk",
      "autumn",
      "business",
      "acid",
      "lemonade",
      "night",
      "coffee",
      "winter"
    ],
    base: true, // applies background color and foreground color for root element by default
    styled: true, // include daisyUI colors and design decisions for all components
    utils: true, // adds responsive and modifier utility classes
    prefix: "", // prefix for daisyUI classnames (components, modifiers and responsive class names. Not colors)
    logs: true, // Shows info about daisyUI version and used config in the console when building your CSS
    themeRoot: ":root", // The element that receives theme color CSS variables
  },
}
