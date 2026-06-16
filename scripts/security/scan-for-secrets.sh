#!/usr/bin/env bash
# =============================================================================
# Secret Scan for Trainer Platform
#
# Scans staged files (and optionally all tracked files) for likely secret/JWT
# patterns. Exits with non-zero if any matches are found.
#
# Usage:
#   ./scripts/security/scan-for-secrets.sh          # staged files only (pre-commit)
#   ./scripts/security/scan-for-secrets.sh --all     # all tracked files
#   ./scripts/security/scan-for-secrets.sh --help    # this help
# =============================================================================

set -o errexit -o nounset -o pipefail

SCRIPT_NAME="$(basename "$0")"
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
HAS_ERROR=0

usage() {
    sed -n '2,/^$/s/^# \?//p' "$0"
    exit 0
}

# --- Patterns ---------------------------------------------------------------
# JWT-like tokens (JSON Web Token — base64url-encoded three-part string)
JWT_PATTERN='eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}'

# Bearer auth header value
BEARER_PATTERN='Authorization:\s*Bearer\s+eyJ'

# LocalStorage / session export pattern
LOCALSTORAGE_DUMP_PATTERN='"access_token":\s*"eyJ'

# --- File naming patterns ---------------------------------------------------
TOKEN_FILE_PATTERNS='_token\.txt|token.*\.txt|\.jwt$|\.jwt\.|auth-dump|localStorage.*\.json|session.*\.json|credentials|\.pem$|\.key$'

# --- Determine files to scan ------------------------------------------------
if [[ "${1:-}" == "--help" ]]; then
    usage
fi

if [[ "${1:-}" == "--all" ]]; then
    echo "[$SCRIPT_NAME] Scanning ALL tracked files…"
    FILES=$(git ls-files)
else
    echo "[$SCRIPT_NAME] Scanning staged files (use --all for full scan)…"
    FILES=$(git diff --cached --name-only --diff-filter=ACM)
fi

if [[ -z "$FILES" ]]; then
    echo "[$SCRIPT_NAME] No files to scan."
    exit 0
fi

# --- Scan file names --------------------------------------------------------
echo "[$SCRIPT_NAME] Checking file names for secret patterns…"
while IFS= read -r file; do
    if echo "$file" | grep -Eq "$TOKEN_FILE_PATTERNS"; then
        echo -e "${RED}[SECURITY]${NC} File name matches secret pattern: $file"
        HAS_ERROR=1
    fi
done <<< "$FILES"

# --- Scan file contents -----------------------------------------------------
echo "[$SCRIPT_NAME] Checking file contents for JWT/token patterns…"
while IFS= read -r file; do
    # Skip binary files
    if [[ -f "$file" ]] && file --mime "$file" 2>/dev/null | grep -q binary; then
        continue
    fi
    if [[ -f "$file" ]]; then
        # JWT inline
        if grep -Eq "$JWT_PATTERN" "$file" 2>/dev/null; then
            echo -e "${RED}[SECURITY]${NC} JWT-like string found in: $file"
            HAS_ERROR=1
        fi
        # Bearer header
        if grep -Eiq "$BEARER_PATTERN" "$file" 2>/dev/null; then
            echo -e "${RED}[SECURITY]${NC} Bearer token pattern found in: $file"
            HAS_ERROR=1
        fi
        # LocalStorage dump
        if grep -Eq "$LOCALSTORAGE_DUMP_PATTERN" "$file" 2>/dev/null; then
            echo -e "${RED}[SECURITY]${NC} Access token dump pattern found in: $file"
            HAS_ERROR=1
        fi
    fi
done <<< "$FILES"

# --- Result ----------------------------------------------------------------
if [[ $HAS_ERROR -eq 1 ]]; then
    echo ""
    echo -e "${RED}[SECURITY]${NC} ⚠️  SECRET SCAN FAILED — one or more secrets detected."
    echo -e "${RED}[SECURITY]${NC} Remove the flagged files/lines before committing."
    exit 1
fi

echo -e "${YELLOW}[SECURITY]${NC} ✅ Secret scan passed — no secrets detected."
exit 0
