# 010B — Known Issues

## Fixed in 010B

| Issue | Status |
|-------|--------|
| Quest Play page crashes with `Cannot read properties of undefined (reading 'message')` | FIXED |
| API error responses with `{"detail": "..."}` format cause TypeError | FIXED |
| ApiClientError constructor throws on undefined input | FIXED |
| Missing HTTPException handler registration on backend | FIXED |

## Remaining Issues

1. **Quest completion requires authentication**: Full quest completion through all interaction types (free_text evaluation via DeepSeek) requires an authenticated user session. The browser tests in 010B verified the quest page loads without the runtime error. The quest flow itself (intro → interaction → submit → outcome → debrief) was verified as safe through unit tests.

2. **Operator experience review**: Not yet performed. The Quest Play runtime has been technically recovered, but the operator should evaluate:
   - Whether the quest is engaging
   - Whether interaction variety is appropriate
   - Whether the debrief teaches useful skills
   - Whether the experience feels complete
   - Whether the narrative state transitions are meaningful

3. **401 auth errors on unauthenticated endpoints**: Some API endpoints return 401 when accessed without a session token. These are expected and do not affect the authenticated user flow.

## Not in Scope

- Layer 011 (next feature layer)
- Quest content redesign
- DeepSeek provider changes
- Production cutover
- Railway shutdown
