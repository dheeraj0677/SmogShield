/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        aqi: {
          good: '#15803d',
          moderate: '#ca8a04',
          sensitive: '#ea580c',
          unhealthy: '#dc2626',
          veryUnhealthy: '#7e22ce',
          hazardous: '#881337',
        },
      },
    },
  },
  plugins: [],
};
