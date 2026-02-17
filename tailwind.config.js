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
                'luxury-black': '#050505',
                'luxury-black-deep': '#0a0a0a',
                'luxury-dark': '#0f0f0f',
                'luxury-charcoal': '#1a1a1a',
                'luxury-text': '#f5f5f7',
                'luxury-gold': '#c5a059',
                'luxury-gold-light': '#e5c585',
                'luxury-gold-dark': '#b08d45',
                'luxury-gold-darker': '#8e6e34',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                serif: ['Playfair Display', 'serif'],
            },
            blur: {
                'luxury-sm': '8px',
                'luxury-md': '12px',
                'luxury-lg': '20px',
                'luxury-xl': '120px', /* Much higher for giant glows */
            }
        },
    },
    plugins: [],
}
