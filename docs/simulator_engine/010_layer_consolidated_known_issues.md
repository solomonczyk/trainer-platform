# Layer 010 — Consolidated Known Issues

## Classification

```json
{
  "blocking_runtime_issues": [],
  "blocking_release_issues": [],
  "iterative_product_fixes": [
    "visual consistency still needs expansion across more quests/pages",
    "design system foundation accepted but may require future polish",
    "operator acceptance limited to current reviewed flow",
    "production gate remains closed"
  ]
}
```

## Iterative Product Fixes (Non-Blocking)

### Visual Consistency Expansion
The unified design system (010D) is accepted for the current QA and BA quest flows. However, visual consistency has not been verified across all trainer pages, scenario pages, activity pages, and future quest content. Expansion across the full page surface is deferred as iterative work.

### Design System Polish
The design system foundation (semantic tokens, typography scale, component system) is accepted. Future polish items may include:
- Refined color usage across more states
- Additional component variants
- Motion/animation refinement
- Accessibility enhancements beyond current scope

### Operator Visual Review Scope
The operator visual review was conducted and accepted specifically for the **current reviewed quest flow** (QA bug report quest, BA payment requirements quest). This acceptance does **not** extend to:
- Full product-market visual quality
- All trainer pages and enrollment flows
- All legacy scenario pages
- Unreviewed edge cases or error states

### Production Gate
`production_accepted` remains `false`. `release_allowed` remains `false`. No production deployment has been performed. A future Layer (or release decision) is required to open the production gate.

## Deployment / Git Issues

### Local docker-compose.staging.yml Changes
The file `docker-compose.staging.yml` has local unstaged changes:
- `NEXT_PUBLIC_API_URL` replaced with `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_APP_ENV: staging` added

**Operator action required**: These changes should be committed or reverted before the next deployment.

### HEAD Not Deployed
Current HEAD (`dd2323c`) differs from the last deployed commit (`c04df92`). The diff includes frontend runtime code (feedback panel, interaction renderers), backend code (quest data, evaluator), and a new frontend Dockerfile. **Redeployment is required** to deploy the accepted HEAD to VPS staging.

### Sub-layer 010A — Known Client Issue
010A (Primary Flow Integration) remains at `IMPLEMENTED_WITH_KNOWN_CLIENT_ISSUE`. The legacy scenario recovery is partial (6 scenarios hidden, 4 redirected, 1 converted). This is preserved as accepted history and is not a release blocker.

## Previously Recorded Issues (Superseded by Acceptance)

The following known issues from earlier 010 sub-layers are **superseded** by acceptance of later layers:

| Issue | Source | Status |
|---|---|---|
| Undefined `.message` error in quest play | 010B known issues | FIXED (010B) |
| Quest catalog/play unreadable | 010B operator review | FIXED (010C + 010D) |
| Inconsistent visual design | 010C → 010D | FIXED (010D) |
| Auto-advance instead of manual Continue | 010D iterative | FIXED (LearningFeedbackPanel) |
