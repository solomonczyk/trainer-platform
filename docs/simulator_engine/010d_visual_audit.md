# 010D Visual Audit

## Purpose
Pre-implementation audit of current UI screens to document inconsistencies before the design system overhaul.

## Screens Audited

### Home Page
- **Typography Issues**: Hero `text-4xl font-extrabold`, features `text-3xl font-bold` — two different heading styles without hierarchy rule
- **Color Issues**: Hardcoded `text-gray-900`, `text-primary-600`, `text-primary-100`
- **Spacing Issues**: Hero `py-24 sm:py-32`, features `py-20 sm:py-28` — different spacing
- **Component Inconsistencies**: Feature cards use Card component but with `text-gray-900` override
- **Visual Identity Issues**: Generic SaaS landing page, no simulator feel

### IT Domain Page
- **Typography Issues**: `text-3xl font-bold text-gray-900 sm:text-4xl` — hardcoded styles
- **Color Issues**: `text-gray-500` for description, `text-gray-300` for empty state
- **Component Inconsistencies**: Domain cards use `rounded-lg` for icons vs `rounded-xl` for cards
- **Visual Identity Issues**: Clean but generic

### QA Trainer Page
- **Typography Issues**: `text-3xl font-bold text-gray-900` — hardcoded heading
- **Color Issues**: `bg-green-100 text-green-700` for enrolled badge — inline badge, not using Badge component
- **Component Inconsistencies**: Enroll status uses hand-rolled badge instead of Badge component
- **Interaction State Issues**: Card hover effects inconsistent

### BA Trainer Page
- Same issues as QA trainer page plus BA-specific module cards
- **Typography Issues**: Module items use hardcoded `text-gray-900`/`text-gray-500`
- **Component Inconsistencies**: Module list items hand-rolled, not using Card sub-components

### QA Quest Catalog
- **Typography Issues**: `text-3xl sm:text-4xl font-extrabold text-gray-900` — hardcoded
- **Color Issues**: `bg-primary-100 text-primary-800 border-primary-200` for interaction type badges — hand-rolled badges
- **Component Inconsistencies**: Cards use `border-2 border-gray-200 hover:border-primary-400` — hardcoded colors
- **Readability Issues**: Metadata text size inconsistent

### BA Quest Catalog
- Same issues as QA quest catalog

### QA Quest Step 1
- **Typography Issues**: `text-xl sm:text-2xl font-bold text-gray-900` — hardcoded
- **Color Issues**: `border-gray-200 bg-gray-50` for story panel — hardcoded
- **Component Inconsistencies**: Option buttons use `rounded-xl` (12px), narrative bars inline
- **Interaction State Issues**: Selected state uses `border-primary-500 bg-primary-50` — correct but hardcoded
- **Visual Identity Issues**: No immersive feeling, no product identity

### QA Evidence Selection
- **Typography Issues**: Category label `text-xs font-semibold uppercase tracking-wider text-gray-500`
- **Component Inconsistencies**: Evidence options don't match standard option card pattern
- **Readability Issues**: Evidence items at `text-sm` could be more readable

### QA Selected Option State
- **Color Issues**: `border-primary-500 bg-primary-50` — correct but hardcoded
- **Interaction State Issues**: Hover on unselected uses `hover:border-primary-300` — subtle, acceptable

### QA Outcome/Debrief
- **Typography Issues**: Mixed `text-3xl` and `text-xl` headings
- **Color Issues**: `bg-green-50 text-green-700` for strengths — hardcoded
- **Component Inconsistencies**: Debrief sections are hand-rolled, no consistent card pattern

### Header/Footer/Localization
- **Component Inconsistencies**: Locale switcher logic duplicated in Header, Footer, and LocaleSwitcher component
- **Color Issues**: Header uses `bg-white/95 backdrop-blur` — hardcoded

## Summary of Main Inconsistencies
1. No semantic color tokens — all colors hardcoded
2. No typography scale — font sizes/weights chosen per-page
3. Button icon spacing inconsistent (mr-2, mr-1.5, ml-2, ml-1)
4. Badge component exists but unused in most places
5. LoadingSpinner component exists but unused in most pages
6. ProgressBar component exists but unused in quest play
7. Input component exists but unused in login/register
8. Card border-radius inconsistent (rounded-xl vs rounded-lg)
9. Page widths inconsistent (max-w-7xl, max-w-4xl, max-w-3xl)
10. Dark mode CSS variables defined but completely unused
11. NarrativeBar defined inline in quest play page
12. No LocaleSwitcher component adoption in Header/Footer
