# Secret Handling Policy

> **Version:** 1.0  
> **Incident:** SECURITY-011S — JWT leaked in repo history  
> **Date:** 2026-06-16

---

## 1. Golden Rule

**Never store JWT, access tokens, API keys, passwords, or any credential inside the repository.**

This includes:

- test token files;
- browser localStorage dumps;
- session export files;
- `.env` files with real secrets (only commit `.env.example` with placeholder values);
- screenshots containing tokens or credentials;
- proof-of-work files that capture token values.

---

## 2. Temporary Auth Artifacts

Temporary authentication artifacts **must** live outside the repository tree:

| Artifact | Allowed Location |
|----------|------------------|
| Browser localStorage dump | OS temp folder (`/tmp/`, `%TEMP%`) |
| Session debug export | OS temp folder |
| Bearer token for curl tests | Environment variable or OS temp file (wiped after use) |
| Auth cookies exported from browser | OS temp folder |

**Important:** Never save temporary auth files inside the project tree —
even in `.gitignore`d locations a stray `git add .` can capture them.

---

## 3. Browser Acceptance Testing

When running browser-based acceptance (Playwright, manual, etc.):

- Use live login / session creation — do **not** persist a token to a file and re-use it.
- If a token must be captured for a curl test, save it **outside** the repo tree
  (e.g., `/tmp/acceptance_token.txt`) and delete it before the next `git status`.
- Keep the browser DevTools Network tab recording; copy the token from there
  directly into the terminal — never into a repo file.

---

## 4. Proof JSON / Documentation

- Proof JSON files **must never** contain actual token values.
- Screenshots of the browser **must not** show the token value in the URL,
  request headers, or response body.
- Security incident docs may reference the *fact* that a token was leaked
  but must not quote, encode, or reproduce the token value.

---

## 5. Before Every Commit

**Mandatory pre-commit steps:**

```bash
# 1. Check what is staged
git status --porcelain
git diff --cached --stat

# 2. Run the secret scan
npm run security:scan:staged
# or
bash scripts/security/scan-for-secrets.sh

# 3. Visually confirm no secrets in the diff
git diff --cached | head -100   # look for eyJ..., Bearer eyJ, token patterns
```

If any of these steps flags a secret, **do not commit**. Remove the file or
line from the staged changes before proceeding.

---

## 6. Pre-Commit Hook (Optional)

To install a local pre-commit hook that runs the secret scan automatically:

```bash
cat > .git/hooks/pre-commit << 'HOOK'
#!/usr/bin/env bash
exec bash scripts/security/scan-for-secrets.sh
HOOK
chmod +x .git/hooks/pre-commit
```

This is a local-only hook (not shared via the repo). Each developer must
install it themselves.

---

## 7. Never Use Broad `git add .`

Always review the staged diff before committing:

```bash
# BAD — stages everything blindly
git add .

# GOOD — stage specific files
git add path/to/file.py

# GOOD — stage interactively
git add -p
```

The `ba_quiz_token.txt` incident happened because `git add .` captured a
token file that was accidentally left in the working tree.

---

## 8. If a Secret Is Leaked (Incident Response)

Follow the SECURITY-011S incident response procedure:

1. **Rotate** the compromised secret immediately.
2. **Remove** the file from the working tree.
3. **Add** the file pattern to `.gitignore`.
4. **Rewrite** git history (`git filter-repo` or `git rebase`) to purge the file.
5. **Force-push** the rewritten history.
6. **Restart** any services using the old secret.
7. **Verify** invalidation by testing with the old secret.
8. **Document** the incident without exposing the secret value.

---

## 9. CI / Pull Request Checks

If CI is configured, add a secret scan job:

```yaml
# .github/workflows/secret-scan.yml (example)
name: Secret Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run secret scan
        run: bash scripts/security/scan-for-secrets.sh --all
```

The scan script requires only `bash`, `grep`, `git`, and `file` — no
external tools or paid services.

---

## 10. Enforcement

- The lead developer is responsible for reviewing diffs for leaked secrets
  before approving any PR.
- Any commit containing a credential will be rejected at review.
- A security incident will be opened for every verified credential leak.

---

*This policy was created in response to Security Incident SECURITY-011S and
applies to all contributors to this repository.*
