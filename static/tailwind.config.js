/** @type {import('tailwindcss').Config} */
export default {
  content: [
    // Templates
    '../templates/**/*.html',
    // JavaScript que genera clases dinámicas
    './engines/**/*.js',
    // Ignorar node_modules
    '!**/node_modules/**',
  ],
  
  theme: {
    extend: {
      /* ─────────────────────────────────────────────────────────────
         COLORS (from design tokens)
         ───────────────────────────────────────────────────────────── */
      colors: {
        'luxury': {
          'gold': '#C5A059',
          'gold-light': '#E5C585',
          'gold-dark': '#B08D45',
          'gold-darker': '#8E6E34',
          'black': '#050505',
          'black-deep': '#0a0a0a',
          'dark': '#0f0f0f',
          'charcoal': '#1a1a1a',
          'text': '#f5f5f7',
        },
      },

      /* ─────────────────────────────────────────────────────────────
         FONT FAMILIES
         ───────────────────────────────────────────────────────────── */
      fontFamily: {
        'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        'serif': ['Playfair Display', 'Georgia', 'serif'],
        'mono': ['Fira Code', 'Monaco', 'monospace'],
      },

      /* ─────────────────────────────────────────────────────────────
         FONT SIZES (Major Third Scale)
         ───────────────────────────────────────────────────────────── */
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
        '7xl': ['4.5rem', { lineHeight: '1' }],
      },

      /* ─────────────────────────────────────────────────────────────
         SPACING (Base 4px)
         ───────────────────────────────────────────────────────────── */
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },

      /* ─────────────────────────────────────────────────────────────
         BORDER RADIUS
         ───────────────────────────────────────────────────────────── */
      borderRadius: {
        '4xl': '2rem',
      },

      /* ─────────────────────────────────────────────────────────────
         TRANSITION TIMING FUNCTIONS
         ───────────────────────────────────────────────────────────── */
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.2, 0.8, 0.2, 1)',
        'bounce-custom': 'cubic-bezier(0.25, 0.8, 0.25, 1)',
      },

      /* ─────────────────────────────────────────────────────────────
         ANIMATION KEYFRAMES
         ───────────────────────────────────────────────────────────── */
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'pulse-gold': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(197, 160, 89, 0.4)' },
          '50%': { boxShadow: '0 0 40px rgba(197, 160, 89, 0.8)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 15px rgba(197, 160, 89, 0.4)' },
          '50%': { boxShadow: '0 0 30px rgba(197, 160, 89, 0.7), 0 0 60px rgba(197, 160, 89, 0.3)' },
        },
        'liquid-gold': {
          'to': { backgroundPosition: '200% center' },
        },
      },

      animation: {
        'fade-in-up': 'fade-in-up 0.8s ease-out forwards',
        'pulse-gold': 'pulse-gold 2s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'shimmer': 'shimmer 3s ease infinite',
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'liquid-gold': 'liquid-gold 6s linear infinite',
      },

      /* ─────────────────────────────────────────────────────────────
         BACKDROP BLUR
         ───────────────────────────────────────────────────────────── */
      backdropBlur: {
        'xs': '2px',
      },

      /* ─────────────────────────────────────────────────────────────
         Z-INDEX SCALE
         ───────────────────────────────────────────────────────────── */
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
        'nav': '1000',
      },
    },
  },

  /* ─────────────────────────────────────────────────────────────────
     PLUGINS
     ───────────────────────────────────────────────────────────────── */
  plugins: [
    // Plugin personalizado para utilidades adicionales
    function({ addUtilities, theme }) {
      addUtilities({
        '.text-gradient-gold': {
          'background': 'linear-gradient(to right, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C)',
          '-webkit-background-clip': 'text',
          'background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
        },
        '.glass': {
          'background': 'rgba(255, 255, 255, 0.02)',
          'backdrop-filter': 'blur(24px)',
          '-webkit-backdrop-filter': 'blur(24px)',
          'border': '1px solid rgba(255, 255, 255, 0.04)',
        },
      });
    },
  ],

  /* ─────────────────────────────────────────────────────────────────
     CORE PLUGINS (desactivar los que no se usan)
     ───────────────────────────────────────────────────────────────── */
  corePlugins: {
    // Mantener todos activos por compatibilidad
  },
};
