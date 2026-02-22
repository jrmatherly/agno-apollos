import type { Config } from 'tailwindcss'
import tailwindcssAnimate from 'tailwindcss-animate'

export default {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}'
  ],
  theme: {
    extend: {
      colors: {
        primary: '#FAFAFA',
        primaryAccent: '#0F141E',
        brand: '#38bdf8',
        background: {
          DEFAULT: '#0a0e14',
          secondary: '#151b28'
        },
        secondary: '#f5f5f5',
        border: 'rgba(var(--color-border-default))',
        accent: '#151b28',
        muted: '#A1A1AA',
        destructive: '#E53935',
        positive: '#34D399'
      },
      fontFamily: {
        sans: 'var(--font-inter)',
        heading: 'var(--font-source-sans)',
        dmmono: 'var(--font-dm-mono)'
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '2rem',
        '3xl': '2.5rem'
      }
    }
  },
  plugins: [tailwindcssAnimate]
} satisfies Config
