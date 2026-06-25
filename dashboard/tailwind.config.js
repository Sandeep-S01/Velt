/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          light: '#818CF8',
          DEFAULT: '#4F46E5',
          dark: '#3730A3',
        },
        success: {
          light: '#34D399',
          DEFAULT: '#10B981',
        },
        warning: '#F59E0B',
        danger: '#EF4444',
        info: '#3B82F6',
        neutral: {
          background: '#F9FAFB',
          card: '#FFFFFF',
          lightgray: '#F3F4F6',
          mediumgray: '#9CA3AF',
          darkgray: '#374151',
          charcoal: '#111827',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
