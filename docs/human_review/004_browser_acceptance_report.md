# Browser Acceptance Report — Human Review Layer 004

## Status: PENDING (requires browser automation environment)

The browser acceptance workflow requires:
1. Real browser (Playwright)
2. Running backend with PostgreSQL (staging)
3. Test identities with appropriate roles

## Planned Test Flow

```text
1. Create test identities:
   - platform_admin (for case creation and assignment)
   - expert_reviewer (for review)

2. Operator creates review case from valid handoff
3. Operator assigns eligible reviewer
4. Reviewer signs in
5. Reviewer opens review queue (/review)
6. Reviewer claims review
7. Reviewer inspects evidence
8. Reviewer submits decision
9. Page refresh confirms persistence
10. Decision and audit history visible
```

## Negative Tests

```text
1. Unauthorized user blocked (redirect to login)
2. Self-review blocked (API returns 403)
3. Second decision blocked (API returns 409)
4. No React runtime errors in console
5. No unexpected 401/403/404/500
6. No pilot or exam-eligible side effects
```

## Environment Requirements

- Node.js 18+
- Backend running on http://localhost:8000 with PostgreSQL
- Test users with roles: platform_admin, expert_reviewer
- Valid generation request with review_handoff_ready candidate
