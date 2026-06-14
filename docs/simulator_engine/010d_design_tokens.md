# 010D Design Tokens

## Token Architecture

All design tokens are defined as CSS custom properties in `globals.css` and exposed through Tailwind's `theme.extend` in `tailwind.config.ts`. Components use Tailwind utility classes that reference these tokens.

## Background Tokens

| Token | Tailwind Class | Light Value | Dark Value | Usage |
|-------|---------------|-------------|------------|-------|
| `--color-bg-app` | `bg-app` | gray-50 | dark gray | Page background |
| `--color-bg-page` | `bg-page` | white | dark | Content area |
| `--color-bg-surface` | `bg-surface` | white | dark | Card/surface background |
| `--color-bg-elevated` | `bg-elevated` | white | lighter dark | Elevated cards |
| `--color-bg-immersive` | `bg-immersive` | dark blue-gray | black | Quest play immersive background |
| `--color-bg-immersive-muted` | `bg-immersive-muted` | muted dark | dark | Quest story panel |

## Text Tokens

| Token | Tailwind Class | Light Value | Dark Value | Usage |
|-------|---------------|-------------|------------|-------|
| `--color-text-primary` | `text-primary` | gray-900 | white | Primary headings |
| `--color-text-secondary` | `text-secondary` | gray-500 | light gray | Body/metadata text |
| `--color-text-muted` | `text-muted` | gray-400 | medium gray | Helper/placeholder text |
| `--color-text-inverse` | `text-inverse` | white | dark | Text on dark backgrounds |
| `--color-text-danger` | `text-danger` | red-500 | red-400 | Error text |
| `--color-text-success` | `text-success` | green-600 | green-400 | Success text |
| `--color-text-warning` | `text-warning` | amber-500 | amber-400 | Warning text |

## Border Tokens

| Token | Tailwind Class | Light Value | Dark Value | Usage |
|-------|---------------|-------------|------------|-------|
| `--color-border-default` | `border-default` | gray-200 | dark border | Standard borders |
| `--color-border-strong` | `border-strong` | dark border | light border | Strong borders |
| `--color-border-interactive` | `border-interactive` | primary-500 | primary-400 | Hover/focus borders |
| `--color-border-selected` | `border-selected` | primary-500 | primary-400 | Selected state borders |
| `--color-border-danger` | `border-danger` | red-500 | red-400 | Error borders |

## Status Colors

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `success` | green 50-800 | green 900/30 + green | Success states |
| `warning` | amber 50-800 | amber 900/30 + amber | Warning states |
| `danger` | red 50-800 | red 900/30 + red | Danger states |

## Quest-Specific Tokens

| Token | Tailwind Class | Light Value | Dark Value |
|-------|---------------|-------------|------------|
| `--color-quest-surface` | `bg-quest-surface` | dark blue-gray | very dark |
| `--color-quest-selected` | `bg-quest-selected` | primary-500 | primary-400 |
| `--color-quest-progress` | `bg-quest-progress` | primary-500 | primary-400 |
| `--color-quest-story` | `bg-quest-story` | very dark | black |

## Radius Scale

| Token | Value | Usage |
|-------|-------|-------|
| `rounded-sm` | 4px | Small elements (badges, inline tags) |
| `rounded` | 8px | Cards, buttons, inputs, option buttons |
| `rounded-md` | 6px | Smaller buttons, compact elements |
| `rounded-lg` | 12px | Featured cards, modals, large containers |
| `rounded-full` | 9999px | Pills, avatars, progress bars |

## Shadow Scale

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-card` | 0 1px 3px 0 rgba(0,0,0,0.06) | Default card shadow |
| `shadow-elevated` | 0 4px 12px -2px rgba(0,0,0,0.08) | Elevated/hover cards |
| `shadow-immersive` | 0 8px 24px -4px rgba(0,0,0,0.12) | Immersive surfaces |

## Page Width Semantics

| Token | Value | Usage |
|-------|-------|-------|
| `max-w-page` | 64rem (1024px) | Standard content pages |
| `max-w-page-narrow` | 48rem (768px) | Narrow content (feedback screens) |
| `max-w-page-wide` | 80rem (1280px) | Dashboard/wide layouts |
