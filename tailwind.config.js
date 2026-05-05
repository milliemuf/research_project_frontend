/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"IBM Plex Mono"', 'Menlo', 'monospace'],
        display: ['"Space Grotesk"', 'Inter', 'sans-serif'],
      },
      colors: {
        // Semantic "ink" scale — values come from CSS variables so the whole
        // palette flips when <html class="dark"> toggles. In dark mode the scale
        // runs page(950) → text(100); in light mode it's inverted.
        ink: {
          950: 'rgb(var(--ink-950) / <alpha-value>)',
          900: 'rgb(var(--ink-900) / <alpha-value>)',
          850: 'rgb(var(--ink-850) / <alpha-value>)',
          800: 'rgb(var(--ink-800) / <alpha-value>)',
          700: 'rgb(var(--ink-700) / <alpha-value>)',
          600: 'rgb(var(--ink-600) / <alpha-value>)',
          500: 'rgb(var(--ink-500) / <alpha-value>)',
          400: 'rgb(var(--ink-400) / <alpha-value>)',
          300: 'rgb(var(--ink-300) / <alpha-value>)',
          200: 'rgb(var(--ink-200) / <alpha-value>)',
          100: 'rgb(var(--ink-100) / <alpha-value>)',
        },
        // Neon accents — agent identity colors
        analyzer: { DEFAULT: '#A855F7', glow: 'rgba(168,85,247,0.45)' },  // violet
        healer:   { DEFAULT: '#22D3EE', glow: 'rgba(34,211,238,0.45)' },  // cyan
        validator:{ DEFAULT: '#34D399', glow: 'rgba(52,211,153,0.45)' }, // emerald
        // Status
        signal: {
          ok:   '#34D399',
          warn: '#F59E0B',
          err:  '#F43F5E',
          info: '#60A5FA',
        },
        brand: {
          50:  '#EEF2FF',
          100: '#E0E7FF',
          200: '#C7D2FE',
          300: '#A5B4FC',
          400: '#818CF8',
          500: '#7C8CFF',
          600: '#5B6CFF',
          700: '#4456E0',
          800: '#3543B0',
          900: '#272F7A',
        },
      },
      backgroundImage: {
        'grid-faint': 'linear-gradient(to right, rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.03) 1px, transparent 1px)',
        'glow-radial': 'radial-gradient(80% 60% at 50% 0%, rgba(124,140,255,0.18) 0%, rgba(7,10,18,0) 60%)',
        'agent-violet': 'linear-gradient(135deg, #A855F7 0%, #6366F1 100%)',
        'agent-cyan':   'linear-gradient(135deg, #22D3EE 0%, #2563EB 100%)',
        'agent-emerald':'linear-gradient(135deg, #34D399 0%, #059669 100%)',
      },
      boxShadow: {
        'glow-brand':    '0 0 0 1px rgba(124,140,255,0.35), 0 0 24px rgba(124,140,255,0.18)',
        'glow-analyzer': '0 0 0 1px rgba(168,85,247,0.40), 0 0 28px rgba(168,85,247,0.18)',
        'glow-healer':   '0 0 0 1px rgba(34,211,238,0.40), 0 0 28px rgba(34,211,238,0.18)',
        'glow-validator':'0 0 0 1px rgba(52,211,153,0.40), 0 0 28px rgba(52,211,153,0.18)',
        'panel':         '0 1px 0 rgba(255,255,255,0.04) inset, 0 30px 60px -30px rgba(0,0,0,0.6)',
      },
      animation: {
        'fade-in':    'fadeIn 0.45s ease-out both',
        'slide-up':   'slideUp 0.5s cubic-bezier(0.2,0.8,0.2,1) both',
        'pulse-soft': 'pulseSoft 2.4s ease-in-out infinite',
        'tick':       'tick 1.2s steps(60) infinite',
        'scan':       'scan 4s linear infinite',
        'flow':       'flow 1.6s ease-in-out infinite',
        'orbit':      'orbit 18s linear infinite',
      },
      keyframes: {
        fadeIn:    { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp:   { '0%': { opacity: '0', transform: 'translateY(14px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
        pulseSoft: { '0%,100%': { opacity: '1' }, '50%': { opacity: '.55' } },
        tick:      { '0%': { transform: 'rotate(0)' }, '100%': { transform: 'rotate(360deg)' } },
        scan:      { '0%': { transform: 'translateY(-100%)' }, '100%': { transform: 'translateY(100%)' } },
        flow:      { '0%': { strokeDashoffset: '40' }, '100%': { strokeDashoffset: '0' } },
        orbit:     { '0%': { transform: 'rotate(0)' }, '100%': { transform: 'rotate(360deg)' } },
      },
    },
  },
  plugins: [],
}
