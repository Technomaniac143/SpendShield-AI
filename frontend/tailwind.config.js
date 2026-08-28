/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Semantic colors per prompt
        risk: {
          DEFAULT: '#ef4444', // Red: critical risk, blocked payment, integrity failure
          light: '#fef2f2',
          dark: '#b91c1c',
        },
        warning: {
          DEFAULT: '#f59e0b', // Amber: warning, investigation required, moderate risk
          light: '#fffbeb',
          dark: '#b45309',
        },
        safe: {
          DEFAULT: '#10b981', // Green: verified, safe, realized savings
          light: '#ecfdf5',
          dark: '#047857',
        },
        info: {
          DEFAULT: '#3b82f6', // Blue: information, AI activity, system intelligence
          light: '#eff6ff',
          dark: '#1d4ed8',
        },
        slate: {
          850: '#151e2e',
          900: '#0f172a',
          950: '#020617',
        }
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
        'floating': '0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04)',
      },
      borderRadius: {
        'md': '0.375rem',
        'lg': '0.5rem',
      }
    },
  },
  plugins: [],
}
