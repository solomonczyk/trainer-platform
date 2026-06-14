# 010D Component System

## Component Inventory

### 1. Button (`components/ui/Button.tsx`)
- **Variants**: `primary` | `secondary` | `outline` | `ghost` | `danger`
- **Sizes**: `sm` | `md` | `lg`
- **States**: default, hover, focus, active, disabled, loading
- **Key change**: Added `gap-2` to base flex container for consistent icon spacing
- **Usage**: All action triggers

### 2. Card (`components/ui/Card.tsx`)
- **Variants**: `default` | `elevated` | `immersive` | `outlined`
- **Padding**: `none` | `sm` | `md` | `lg`
- **States**: default, hover (if `hover` prop set)
- **Sub-components**: `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`
- **Key change**: Semantic tokens for colors, `rounded` for default radius, new `variant` prop
- **Usage**: All container/card needs

### 3. Badge/Chip (`components/ui/Badge.tsx`)
- **Variants**: `default` | `success` | `warning` | `danger` | `info` | `primary` | `outline` | `secondary`
- **Sizes**: `sm` | `md`
- **Key change**: Added `primary` and `outline` variants
- **Usage**: Status indicators, interaction type badges, locale badges

### 4. ProgressBar (`components/ui/ProgressBar.tsx`)
- **Sizes**: `sm` | `md` | `lg`
- **Colors**: `auto` | `primary` | `success` | `warning` | `danger`
- **Props**: `barClassName` for custom bar styling
- **Key change**: Added `barClassName` prop, `color` prop with default `primary`
- **Usage**: Quest progress, loading progress

### 5. LoadingSpinner (`components/ui/LoadingSpinner.tsx`)
- **Sizes**: `sm` | `md` | `lg`
- **Props**: `label` for accessible loading text
- **Usage**: All loading states across pages

### 6. Input (`components/ui/Input.tsx`)
- **Variants**: `input` | `textarea`
- **States**: default, error (with error message), disabled
- **Props**: `label`, `helperText`, `error`
- **Usage**: Forms (login, register)

### 7. PageContainer (`components/ui/PageContainer.tsx`)
- **Props**:
  - `width`: `page` (default, 64rem) | `narrow` (48rem) | `wide` (80rem)
  - `padding`: `default` (py-12) | `compact` (py-8)
- **Sub-components**: `SectionHeader` (h1 + optional description)
- **Usage**: All page-level layouts

### 8. StatusMeter (`features/quests/status-meter.tsx`)
- **Props**: `state` (Record<string, number>), `showLabel` (boolean)
- **Bars**: risk, time_remaining, team_trust, client_trust, evidence_quality, decision_quality
- **Usage**: Narrative state visualization in quest play

### 9. MissionCard / QuestCard
- Implemented as `<Card hover variant="default" className="border-2 hover:border-interactive">`
- No separate component — Card with specific className pattern
- **Usage**: Quest catalog items

### 10. OptionCard
- No separate component — shared CSS class constants in `interaction-renderers.tsx`
- `OPTION_BASE`, `OPTION_UNSELECTED`, `OPTION_SELECTED`, `OPTION_DISABLED`, `OPTION_ENABLED`
- **States**: default, hover, selected, disabled, focus
- **Usage**: Single choice, multiple choice, decision, dialogue options

### 11. StoryPanel
- Implemented as `<div className="rounded bg-muted border border-default p-5">`
- No separate component — inline pattern
- **Usage**: Story context in quest play

### 12. OutcomeCard / DebriefSection
- Implemented as `<Card variant="elevated">` for outcome
- Debrief sections use `Card` for summary, colored lists for strengths/improvements
- **Usage**: Outcome and debrief screens

### 13. EmptyState / ErrorState / LoadingState
- Standard patterns:
  - **Empty**: Card + icon + message
  - **Error**: Icon + heading + message + retry button
  - **Loading**: LoadingSpinner centered
- **Usage**: All data-fetching pages

## State Consistency

All interactive components must support:
| State | Requirement |
|-------|------------|
| default | Clear, readable, properly colored |
| hover | Visual feedback (border color, lift, shadow) |
| focus | Focus ring (`focus:ring-2 focus:ring-ring`) |
| active | Subtle press (`active:scale-[0.99]`) |
| selected | Distinct border/background color |
| disabled | Reduced opacity (`opacity-50` / `opacity-60`) |
| error | Red border/background (form inputs) |
| loading | Spinner animation |

## Interaction Renderer Consistency

All option-based interaction renderers (single_choice, multiple_choice, decision, dialogue) use the same shared CSS classes defined at the top of `interaction-renderers.tsx`:

- `rounded border-2` for all option buttons (unified from mixed `rounded-xl`/`rounded-lg`)
- `border-default bg-surface` for unselected
- `hover:border-interactive hover:shadow-sm` for hover
- `border-selected bg-primary-50 shadow-sm` for selected
- `border-amber-500 bg-amber-50` for decision (amber accent)
- `border-purple-500 bg-purple-50` for dialogue (purple accent)
- `opacity-60 cursor-not-allowed` for disabled

## SVG Icons

All icons use `lucide-react`. Icon sizing guidelines:
- Button icons: `h-4 w-4` (sm) / `h-5 w-5` (md/lg)
- Section headers: `h-5 w-5`
- Empty states: `h-12 w-12`
- Status/result: `h-12 w-12`
- Navigation: `h-4 w-4`
