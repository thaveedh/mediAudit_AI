/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        ink: {
          950: '#05070d',
          900: '#080b14',
          800: '#0d1220',
          700: '#151c2e',
        },
        mint: {
          300: '#7bf1c4',
          400: '#3fe0a8',
          500: '#17c98d',
          600: '#0ea36f',
        },
      },
      boxShadow: {
        glow: '0 0 60px -20px rgba(23, 201, 141, 0.65)',
        panel: '0 30px 80px -40px rgba(0, 0, 0, 0.9)',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        float: 'float 8s ease-in-out infinite',
        shimmer: 'shimmer 2.4s linear infinite',
      },
    },
  },
  plugins: [],
}
