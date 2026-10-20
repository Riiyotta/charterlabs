/** @type {import('tailwindcss').Config} */

// Source uses Tailwind v4 with `--spacing: 1px`, so every numeric utility is px
// (`pt-128` = 128px, `h-514` = 514px, `-ml-16` = -16px). Reproduce that here.
const spacing = { px: '1px' }
for (let i = 0; i <= 2600; i++) spacing[i] = `${i}px`

// Tone-driven semantic colours (swap via [data-tone=light|inverse] in index.css).
const tone = {
  primary: 'var(--tone-text-primary)',
  secondary: 'var(--tone-text-secondary)',
  tertiary: 'var(--tone-text-tertiary)',
  disabled: 'var(--tone-text-disabled)',
}

// Type scale. Sizes are CSS vars that change at tablet/desktop (index.css).
// Prefer the `.type-*` classes from index.css; these `text-*` sizes mirror them.
const type = (name, lh, ls, fw) => [
  `var(--type-${name}-size)`,
  { lineHeight: lh, letterSpacing: ls, fontWeight: fw },
]

export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    screens: {
      tablet: '810px',
      desktop: '1200px',
      wide: '1920px',
    },
    spacing,
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      inherit: 'inherit',
      black: '#000',
      white: '#fff',
      gray: {
        0: '#fff',
        50: '#fafafa',
        100: '#f5f5f5',
        200: '#ebebeb',
        300: '#d6d6d6',
        400: '#b3b3b3',
        500: '#8f8f8f',
        600: '#6b6b6b',
        700: '#4d4d4d',
        800: '#2e2e2e',
        900: '#1a1a1a',
        950: '#0d0d0d',
        1000: '#000',
      },
      'alpha-black': {
        4: '#0000000a',
        8: '#00000014',
        12: '#0000001f',
        20: '#0003',
        40: '#0006',
        60: '#0009',
        80: '#000c',
      },
      'alpha-white': {
        4: '#ffffff0a',
        8: '#ffffff14',
        12: '#ffffff1f',
        20: '#fff3',
        40: '#fff6',
        60: '#fff9',
        80: '#fffc',
      },
      'status-error': '#ff2244',
    },
    extend: {
      // text-primary / text-secondary / text-tertiary / text-disabled / text-on-solid
      textColor: { ...tone, 'on-solid': 'var(--tone-surface)' },
      // bg-surface / bg-raised / bg-solid / bg-solid-disabled
      backgroundColor: {
        surface: 'var(--tone-surface)',
        raised: 'var(--tone-surface-raised)',
        solid: 'var(--tone-text-primary)',
        'solid-disabled': 'var(--tone-text-tertiary)',
      },
      // border-subtle / border-strong
      borderColor: {
        subtle: 'var(--tone-border-subtle)',
        strong: 'var(--tone-border-strong)',
      },
      placeholderColor: tone,
      ringColor: { primary: 'var(--tone-text-primary)' },
      ringOffsetColor: { surface: 'var(--tone-surface)' },
      fontFamily: {
        sans: ['inter', '"inter Fallback"', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        display: type('display', '1', '-0.03em', '440'),
        h1: type('h1', '1.04', '-0.02em', '450'),
        h2: type('h2', '1.06', '-0.02em', '450'),
        h3: type('h3', '1.08', '-0.015em', '450'),
        h4: type('h4', '1.1', '-0.01em', '450'),
        h5: type('h5', '1.15', '-0.005em', '450'),
        h6: type('h6', '1.2', '-0.01em', '485'),
        tag: type('tag', '1.4', '-0.005em', '420'),
        body1: type('body1', '1.38', '0', '450'),
        'body1-strong': type('body1-strong', '1.38', '-0.01em', '550'),
        body2: type('body2', '1.5', '0.005em', '400'),
        body3: type('body3', '1.35', '0.01em', '450'),
        caption: type('caption', '1.35', '0.01em', '450'),
        button: type('button', '1', '0', '500'),
      },
      fontWeight: {
        400: '400',
        420: '420',
        440: '440',
        450: '450',
        485: '485',
        500: '500',
        550: '550',
      },
      borderRadius: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        card: '28px',
        lg: '32px',
        xl: '64px',
        pill: '999px',
      },
      blur: {
        reveal: '5px',
        glass: '10px',
        mirror: '24px',
        ambient: '48px',
      },
      backdropBlur: {
        reveal: '5px',
        glass: '10px',
        mirror: '24px',
        ambient: '48px',
      },
      borderWidth: { 3: '3px' },
      zIndex: { 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10' },
      maxWidth: {
        page: '1700px',
        'measure-sm': '420px',
        'measure-md': '560px',
        'measure-lg': '720px',
      },
      rotate: { 19: '19deg', 22.5: '22.5deg' },
      transitionTimingFunction: {
        // revealMask / nav-drop
        'expo-out': 'cubic-bezier(.16,1,.3,1)',
        // nav panel / sheet / links
        drawer: 'cubic-bezier(.32,.72,0,1)',
        standard: 'cubic-bezier(.4,0,.2,1)',
      },
    },
  },
  plugins: [],
}
