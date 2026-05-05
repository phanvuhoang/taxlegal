/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  "#e6f4ec",
          100: "#c2e4ce",
          200: "#9dd3af",
          300: "#73c28e",
          400: "#4db473",
          500: "#028a39",  // main brand color
          600: "#027a32",
          700: "#01692a",
          800: "#015722",
          900: "#00431a",
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
