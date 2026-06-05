# Known Issues - MVP-007 Staging Real AI Acceptance Review

## Context

MVP-007 is a future acceptance review layer. This pack is prepared before MVP-006C is accepted and must wait for the MVP-006C result.

## 1. MVP-006C Acceptance Required

**Status**: OPEN

**Severity**: ENTRY BLOCKER

**Description**: MVP-007 cannot begin execution until MVP-006C accepts the DeepSeek evaluation schema contract with `validation_status=validated`, normalized criteria, and verified progress updates.

**Required action**: Wait for MVP-006C result.

## 2. Real AI Acceptance Tests Not Executed In This Layer

**Status**: OPEN

**Severity**: EXPECTED LIMITATION

**Description**: This layer creates the acceptance framework only. It does not execute real DeepSeek smoke, timeout tests, fallback tests, or rate-limit tests.

**Required action**: Execute after MVP-006C acceptance under the MVP-007 review task.

## 3. Production And Release Remain Disabled

**Status**: ACTIVE CONTROL

**Severity**: RELEASE GUARDRAIL

**Description**: `production_accepted` and `release_allowed` must remain false until a later production-specific review explicitly accepts them.

## Non-Issues

- Backend code was not changed.
- Frontend code was not changed.
- Railway variables were not changed.
- No provider secret was exposed.
- OpenAI was not enabled.
- No trainers, payments, production launch, or market launch work was started.

