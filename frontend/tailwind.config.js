/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        ink: "#0F172A",
        clinical: {
          50: "#F0FBFA",
          100: "#D6F3F0",
          200: "#A8E4DD",
          400: "#3FA79A",
          500: "#1F7A6E",
          600: "#146258",
          700: "#0E4A43",
        },
        accent: "#E8A33D",
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 23, 42, 0.06), 0 1px 6px rgba(15, 23, 42, 0.05)",
      },
    },
  },
  plugins: [],
};
