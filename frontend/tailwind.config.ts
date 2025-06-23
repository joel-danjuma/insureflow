import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'bg-primary': 'var(--bg-primary)',
        'bg-secondary': 'var(--bg-secondary)',
        'bg-tertiary': 'var(--bg-tertiary)',
        'text-primary': 'var(--text-primary)',
        'text-secondary': 'var(--text-secondary)',
        'text-muted': 'var(--text-muted)',
        'accent-orange': 'var(--accent-orange)',
        'accent-orange-hover': 'var(--accent-orange-hover)',
        'border-color': 'var(--border-color)',
      },
      fontFamily: {
        'public-sans': ['var(--font-public-sans)', 'Public Sans', 'sans-serif'],
        'noto-sans': ['var(--font-noto-sans)', 'Noto Sans', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/container-queries'),
  ],
}
export default config 