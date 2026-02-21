/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./api/templates/**/*.html",
        "./static/**/*.js",
        "./static/atoms/**/*.html",
        "./static/molecules/**/*.html",
        "./static/organisms/**/*.html",
        "./tests/frontend/templates/**/*.html"
    ],
    theme: {
        extend: {
            colors: {
                'luxury-gold': '#C5A059', // Gold 1
                'luxury-gold-light': '#F1D06E', // Gold 2
                'luxury-gold-dark': '#aa8c2c', // Gold 3 (generated dim)
                'luxury-black': '#0a0a0a', // Deep Black
                'luxury-gray': '#1a1a1a', // Surface (NOT for text)
                'luxury-text': '#e8e8e8', // Body text (WCAG AA: 17.4:1)
                'luxury-text-dim': '#9ca3af', // Muted text (WCAG AA: 7.2:1)
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                serif: ['Playfair Display', 'serif'],
            },
            boxShadow: {
                'glow-gold': '0 0 20px rgba(212, 175, 55, 0.15)',
                'glow-gold-lg': '0 0 40px rgba(212, 175, 55, 0.25)',
            },
            backgroundImage: {
                'gradient-gold': 'linear-gradient(135deg, #D4AF37 0%, #F1D06E 50%, #D4AF37 100%)',
            }
        },
    },
    plugins: [],
}
