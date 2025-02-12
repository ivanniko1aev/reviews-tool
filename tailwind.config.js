module.exports = {
  content: [
    './templates/**/*.html', // Adjust paths to your HTML files
    './static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#B80000',   // Red
        secondary: '#FF7F11', // Orange
        light: '#E2E8CE',     // Light Beige
        accent: '#ACBFA4',    // Muted Green
        dark: '#262626',      // Dark Grey/Black
      },
      fontFamily: {
        sans: ['Inter', 'Arial', 'sans-serif'],
        serif: ['Georgia', 'serif'],
      },
      spacing: {
        18: '4.5rem',
        84: '21rem',
      },
      borderRadius: {
        'xl': '1.25rem',
      },
      boxShadow: {
        'lg': '0 10px 15px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
}
