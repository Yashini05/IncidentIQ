/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#07111f',
        panel: 'rgba(9, 18, 32, 0.72)',
        line: 'rgba(255, 255, 255, 0.10)',
        accent: '#4fd1c5',
        accent2: '#f59e0b',
        danger: '#ef4444',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(79, 209, 197, 0.25), 0 24px 80px rgba(0, 0, 0, 0.45)',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        body: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        aurora:
          'radial-gradient(circle at top left, rgba(79, 209, 197, 0.24), transparent 35%), radial-gradient(circle at top right, rgba(245, 158, 11, 0.16), transparent 28%), linear-gradient(180deg, #050b16 0%, #07111f 48%, #050b16 100%)',
      },
    },
  },
  plugins: [],
};
