/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: "#121212",
        primary: "#f97316", // Cor do ícone na imagem
        "dark-light": "#1e1e1e", // Um pouco mais claro que o fundo
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
} 