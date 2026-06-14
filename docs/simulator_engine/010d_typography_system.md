# 010D Typography System

## Primary Font: Inter

Inter is a highly readable, neutral typeface designed for computer screens. It supports both Latin (en-US) and Cyrillic (ru-RU) scripts with excellent legibility at all sizes.

- Font family: `Inter, system-ui, -apple-system, sans-serif`
- Weights used: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold), 800 (Extra Bold)
- Source: Google Fonts (`@import` in `globals.css`)

## Typography Scale

| Token | Size | Line Height | Weight | Usage |
|-------|------|-------------|--------|-------|
| `text-display` | 2.5rem (40px) | 2.75rem (44px) | 800 | Hero/major page titles |
| `text-h1` | 2.25rem (36px) | 2.5rem (40px) | 800 | Page titles |
| `text-h2` | 1.875rem (30px) | 2.25rem (36px) | 700 | Section titles |
| `text-h3` | 1.5rem (24px) | 2rem (32px) | 700 | Card titles / quest titles |
| `text-h4` | 1.25rem (20px) | 1.75rem (28px) | 600 | Subsection titles |
| `text-body-lg` | 1.125rem (18px) | 1.75rem (28px) | 400 | Large body text / story text |
| `text-body` | 1rem (16px) | 1.625rem (26px) | 400 | Main body text |
| `text-body-sm` | 0.875rem (14px) | 1.375rem (22px) | 400 | Secondary text / metadata |
| `text-caption` | 0.75rem (12px) | 1rem (16px) | 500 | Labels, badges, helpers |
| `text-label` | 0.875rem (14px) | 1.25rem (20px) | 500 | Form labels, option labels |

## Readability Requirements

| Context | Minimum Size | Line Height |
|---------|-------------|-------------|
| Body text | 16px (text-body) | 1.5+ |
| Quest options | 16px (text-body) | — |
| Story context | 17px (text-body-lg) | 1.6+ |
| Catalog titles | 24px (text-h3) | — |
| Catalog descriptions | 16px (text-body) | 1.5+ |
| Metadata | 14px (text-body-sm) | — |
| Badges/chips | 12px (text-caption) | — |

## Text Color Semantics

| Context | Color Token | Light | Dark |
|---------|------------|-------|------|
| Page/section heading | `text-foreground` | gray-900 | white |
| Card title | `text-foreground` | gray-900 | white |
| Body text | `text-secondary-foreground` | gray-700 | light gray |
| Description/metadata | `text-muted-foreground` | gray-500 | medium gray |
| Placeholder | `text-muted-foreground` | gray-400 | medium gray |
| Error | `text-danger-700` | red-700 | red-200 |
| Success | `text-success-700` | green-700 | green-200 |

## Implementation Notes

- Typography tokens are defined in `tailwind.config.ts` under `theme.extend.fontSize`
- The Inter font is loaded via Google Fonts `@import` in `globals.css`
- Font family is applied globally via `body { @apply font-sans }`
- ru-RU text is safe because Inter provides full Cyrillic support
- Long Russian words wrap naturally with the generous line-height values
