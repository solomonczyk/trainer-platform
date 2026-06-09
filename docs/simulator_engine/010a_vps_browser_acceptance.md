# 010a — VPS Browser Acceptance

## Status: PENDING

This document will be updated after deployment and real browser testing.

## Staging URL

```
https://trainer.152.53.227.37.nip.io
```

## Test Checklist

### QA Primary Flow
- [ ] Normal navigation from home → IT domain → QA trainer → quest catalog
- [ ] Legacy scenario catalog absent from primary flow
- [ ] Quest catalog shows available quests
- [ ] Bug report quest has 5+ interaction types
- [ ] No textarea-only page encountered

### BA Primary Flow
- [ ] Normal navigation from home → IT domain → BA trainer → quest catalog
- [ ] Legacy scenario catalog absent from primary flow
- [ ] Quest catalog shows BA quest
- [ ] BA quest completes with outcome and debrief

### Legacy URL
- [ ] `/scenarios/qa_bug_report_structure_v1` redirects to quest
- [ ] No React error #31
- [ ] No white screen

### Runtime
- [ ] No React error #31
- [ ] No white screen
- [ ] No infinite loader
- [ ] No raw i18n keys visible
- [ ] No unexpected console errors
