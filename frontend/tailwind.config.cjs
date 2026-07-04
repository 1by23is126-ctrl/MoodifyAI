module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        void: '#050608',
        abyss: '#0a0b10',
        surface: '#0e1018',
        elevated: '#1a1d29',
        'nebula-purple': '#9b8cff',
        'neon-purple': '#9b8cff',
        'electric-blue': '#6ab7ff',
        'cyber-pink': '#ff9a8a',
        stellar: 'var(--text-primary)',
        muted: 'var(--text-muted)',
        ghost: '#4a505d',
        primary: 'var(--text-primary)',
        secondary: 'var(--text-secondary)',
        'soft-ivory': 'var(--text-primary)',
        'warm-gray': 'var(--text-secondary)',
        'glass-dark': 'var(--glass-dark)',
        'surface-overlay': 'var(--surface-overlay)',
        'mood-primary': 'var(--mood-primary)',
        'mood-secondary': 'var(--mood-secondary)',
        'mood-glow': 'var(--mood-glow)'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Clash Display', 'Inter', 'sans-serif'],
        serif: ['Instrument Serif', 'Cormorant Garamond', 'Georgia', 'serif']
      },
      animation: {
        'pulse-glow': 'pulse-glow 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 14s ease-in-out infinite',
        'float-delayed': 'float 18s ease-in-out infinite 2s',
        'breathe': 'breathe 5s ease-in-out infinite',
        'drift': 'drift 26s linear infinite'
      },
      backgroundImage: {
        'glass-gradient': 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%)',
      }
    }
  },
  plugins: [],
}
