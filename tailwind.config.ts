import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Light Intelligence System tokens
        'bg-base': '#F7F8FA',
        'bg-card': '#FFFFFF',
        'border-base': '#E5E7EB',
        'primary': '#2F6BFF',
        'primary-light': '#EEF3FF',
        'success': '#16A34A',
        'success-light': '#DCFCE7',
        'danger': '#DC2626',
        'danger-light': '#FEE2E2',
        'gold': '#C9A86A',
        'gold-light': '#FEF3C7',
        'text-base': '#111827',
        'text-muted': '#6B7280',
        // Dark analytical zone tokens (for charts / deep analytics)
        'dark-bg': '#0F111A',
        'dark-card': '#161825',
        'dark-border': 'rgba(255,255,255,0.07)',
        // Legacy (Globe, etc.)
        'accent-blue': '#2F6BFF',
        'accent-green': '#16A34A',
        'accent-red': '#DC2626',
        'accent-gold': '#C9A86A',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgb(0 0 0 / 0.08), 0 1px 2px -1px rgb(0 0 0 / 0.04)',
        'card-hover': '0 4px 12px 0 rgb(0 0 0 / 0.1), 0 2px 4px -1px rgb(0 0 0 / 0.06)',
        'primary': '0 4px 14px 0 rgba(47,107,255,0.25)',
      },
      animation: {
        'ticker': 'ticker 40s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'pulse-dot': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.4s ease-out',
      },
      keyframes: {
        ticker: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
export default config
