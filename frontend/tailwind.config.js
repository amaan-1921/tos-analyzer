/** @type {import('tailwindcss').Config} */
export default {
  content: ["./public/index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#121212',
        'dark-secondary': '#1F2937',
        'light-text': '#E0E0E0',
        'accent-teal': '#00C4B4',
        'risky-red': '#EC5A64',
        'unfair-yellow': '#FBBF24',
      },
    },
  },
  plugins: [],
}