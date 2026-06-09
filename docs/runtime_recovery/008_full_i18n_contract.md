# 008 — Full i18n Contract

## Locales

| Code | Status |
|------|--------|
| `ru-RU` | ✅ Complete for user flow |
| `en-US` | ✅ Complete for user flow |

## Content Categories

| Category | ru-RU | en-US | Coverage |
|----------|-------|-------|----------|
| navigation | ✅ | ✅ | 8 entries each |
| homepage hero | ✅ | ✅ | 2 entries each |
| homepage CTA | ✅ | ✅ | 2 entries each |
| feature cards | ✅ | ✅ | 6 entries each |
| auth forms | ✅ | ✅ | 10 entries each |
| domain names | ✅ | ✅ | 2 entries each |
| domain descriptions | ✅ | ✅ | 2 entries each |
| trainer names | ✅ | ✅ | 2 product names |
| trainer descriptions | ✅ | ✅ | 2 product descriptions |
| target audiences | ✅ | ✅ | 9 audience labels |
| duration labels | ✅ | ✅ | 2 entries each |
| QA scenario titles | ✅ | ✅ | 5 titles each |
| QA scenario goals | ✅ | ✅ | 5 goals each |
| BA scenario titles | ✅ | ✅ | 6 titles each |
| difficulty/level labels | ✅ | ✅ | 5 level labels |
| question content | ✅ | ✅ | Via scenario API |
| answer placeholders | ✅ | ✅ | 2 entries each |
| submit buttons | ✅ | ✅ | 2 entries each |
| loading states | ✅ | ✅ | 2 entries each |
| empty states | ✅ | ✅ | 2 entries each |
| error states | ✅ | ✅ | 5 entries each |
| evaluation labels | ✅ | ✅ | 14 entries each |
| evaluation criteria | ✅ | ✅ | 5 entries each |
| strengths/improvements | ✅ | ✅ | 3 entries each |
| score labels | ✅ | ✅ | 4 entries each |
| progress labels | ✅ | ✅ | 10 entries each |
| completion messages | ✅ | ✅ | 2 entries each |
| API error messages | ✅ | ✅ | 3 entries each |
| 404 messages | ✅ | ✅ | 2 entries each |

## Fallback Policy

```
requested locale → configured default locale (ru-RU) → explicit key
```

Raw translation keys are NEVER shown to users. The `t()` function returns
the key unchanged when not found, and callers use `tl()` to strip the
translation-framework prefix for user-safe display.

## Forbidden Patterns

- Raw `scenario.*.title` / `scenario.*.goal` keys in UI: ❌ → Fixed ✅
- English-only content in ru-RU locale: ❌ → Fixed ✅
- Hardcoded Russian/English in components: ❌ → Verified absent ✅
- Locale switch without content update: ❌ → Fixed ✅

## Verification

```bash
npx tsc --noEmit    # PASSED
npm run build       # PASSED
npx vitest run      # 63/63 PASSED
```
