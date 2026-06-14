import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        // Semantic background tokens
        app: 'hsl(var(--color-bg-app))',
        page: 'hsl(var(--color-bg-page))',
        surface: 'hsl(var(--color-bg-surface))',
        elevated: 'hsl(var(--color-bg-elevated))',
        immersive: 'hsl(var(--color-bg-immersive))',
        'immersive-muted': 'hsl(var(--color-bg-immersive-muted))',
        // Text hierarchy tokens
        'text-primary': 'hsl(var(--color-text-primary))',
        'text-secondary': 'hsl(var(--color-text-secondary))',
        'text-muted': 'hsl(var(--color-text-muted))',
        'text-inverse': 'hsl(var(--color-text-inverse))',
        'text-danger': 'hsl(var(--color-text-danger))',
        'text-success': 'hsl(var(--color-text-success))',
        'text-warning': 'hsl(var(--color-text-warning))',
        // Border tokens
        'border-default': 'hsl(var(--color-border-default))',
        'border-strong': 'hsl(var(--color-border-strong))',
        'border-interactive': 'hsl(var(--color-border-interactive))',
        'border-selected': 'hsl(var(--color-border-selected))',
        'border-danger': 'hsl(var(--color-border-danger))',
        // Status tokens
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          400: '#facc15',
          500: '#eab308',
          600: '#ca8a04',
          700: '#a16207',
          800: '#854d0e',
        },
        danger: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
        },
        // Quest-specific tokens
        quest: {
          surface: 'hsl(var(--color-quest-surface))',
          'surface-hover': 'hsl(var(--color-quest-surface-hover))',
          selected: 'hsl(var(--color-quest-selected))',
          progress: 'hsl(var(--color-quest-progress))',
          story: 'hsl(var(--color-quest-story))',
          option: 'hsl(var(--color-quest-option))',
        },
      },
      borderRadius: {
        sm: '4px',
        DEFAULT: '8px',
        md: '6px',
        lg: '12px',
        xl: '16px',
      },
      maxWidth: {
        page: '64rem',
        'page-narrow': '48rem',
        'page-wide': '80rem',
      },
      fontSize: {
        display: ['2.5rem', { lineHeight: '2.75rem', fontWeight: '800' }],
        h1: ['2.25rem', { lineHeight: '2.5rem', fontWeight: '800' }],
        h2: ['1.875rem', { lineHeight: '2.25rem', fontWeight: '700' }],
        h3: ['1.5rem', { lineHeight: '2rem', fontWeight: '700' }],
        h4: ['1.25rem', { lineHeight: '1.75rem', fontWeight: '600' }],
        body: ['1rem', { lineHeight: '1.625rem' }],
        'body-lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'body-sm': ['0.875rem', { lineHeight: '1.375rem' }],
        caption: ['0.75rem', { lineHeight: '1rem' }],
        label: ['0.875rem', { lineHeight: '1.25rem', fontWeight: '500' }],
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.06)',
        elevated: '0 4px 12px -2px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.06)',
        immersive: '0 8px 24px -4px rgba(0, 0, 0, 0.12), 0 4px 8px -4px rgba(0, 0, 0, 0.08)',
      },
    },
  },
  plugins: [],
};

export default config;
