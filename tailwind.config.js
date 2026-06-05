/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/**/*.js',
  ],
  safelist: [
    'pointer-events-none',
    'pointer-events-auto',
    'hidden',
    'line-clamp-1',
    'line-clamp-2',
    'translate-y-0',
    'translate-y-full',
    '-translate-y-full',
  ],
  theme: {
    extend: {
      colors: {
        "primary":                "#ba0013",
        "primary-container":      "#e31e24",
        "on-primary":             "#ffffff",
        "secondary-container":    "#fcaf19",
        "on-secondary-container": "#281800",
        "surface":                "#f9f9fe",
        "surface-container":      "#ededf2",
        "surface-container-low":  "#f3f3f8",
        "surface-container-high": "#e8e8ed",
        "background":             "#f9f9fe",
        "on-surface":             "#1a1c1f",
        "on-surface-variant":     "#5d3f3c",
        "outline":                "#926f6b",
        "outline-variant":        "#e7bdb8",
        "tertiary":               "#5c5b5b",
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "sans-serif"],
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
