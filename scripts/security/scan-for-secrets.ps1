<#
.SYNOPSIS
    Secret scan for Trainer Platform — Windows PowerShell equivalent.
.DESCRIPTION
    Scans staged files (or all tracked files) for JWT/token patterns.
    Exits with non-zero if any matches are found.
.PARAMETER All
    Scan all tracked files instead of only staged files.
.PARAMETER Help
    Show this help.
.EXAMPLE
    .\scripts\security\scan-for-secrets.ps1
    .\scripts\security\scan-for-secrets.ps1 -All
#>

param(
    [switch]$All,
    [switch]$Help
)

if ($Help) {
    Get-Help $PSCommandPath -Full
    exit 0
}

$ErrorActionPreference = 'Stop'
$hasError = $false

# Patterns
$jwtPattern = 'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'
$bearerPattern = 'Authorization:\s*Bearer\s+eyJ'
$localStoragePattern = '"access_token":\s*"eyJ'
$tokenFilePatterns = @('_token.txt', 'token*.txt', '*.jwt', '*.jwt.*', 'auth-dump*', 'localStorage*.json', 'session*.json', 'credentials*', '*.pem', '*.key')

# Determine files to scan
if ($All) {
    Write-Host "[scan-for-secrets] Scanning ALL tracked files…"
    $files = git ls-files
} else {
    Write-Host "[scan-for-secrets] Scanning staged files…"
    $files = git diff --cached --name-only --diff-filter=ACM
}

if (-not $files) {
    Write-Host "[scan-for-secrets] No files to scan."
    exit 0
}

# Scan file names
Write-Host "[scan-for-secrets] Checking file names for secret patterns…"
foreach ($file in $files) {
    foreach ($pattern in $tokenFilePatterns) {
        $patternRegex = '^' + [regex]::Escape($pattern).Replace('\*', '.*') + '$'
        if ($file -match $patternRegex) {
            Write-Host -ForegroundColor Red "[SECURITY] File name matches secret pattern: $file"
            $hasError = $true
        }
    }
}

# Scan contents
Write-Host "[scan-for-secrets] Checking file contents for JWT/token patterns…"
foreach ($file in $files) {
    if (-not (Test-Path $file)) { continue }
    $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
    if (-not $content) { continue }

    # Skip binary
    if ($content -match '[^\x20-\x7E\x0A\x0D\t]' -and ($content.Length -gt 0 -and $content.Length -lt 100)) {
        continue
    }
    if ($content -match $jwtPattern) {
        Write-Host -ForegroundColor Red "[SECURITY] JWT-like string found in: $file"
        $hasError = $true
    }
    if ($content -match $bearerPattern) {
        Write-Host -ForegroundColor Red "[SECURITY] Bearer token pattern found in: $file"
        $hasError = $true
    }
    if ($content -match $localStoragePattern) {
        Write-Host -ForegroundColor Red "[SECURITY] Access token dump found in: $file"
        $hasError = $true
    }
}

if ($hasError) {
    Write-Host ""
    Write-Host -ForegroundColor Red "[SECURITY] ⚠️  SECRET SCAN FAILED — one or more secrets detected."
    Write-Host -ForegroundColor Red "[SECURITY] Remove the flagged files/lines before committing."
    exit 1
}

Write-Host -ForegroundColor Yellow "[SECURITY] ✅ Secret scan passed — no secrets detected."
exit 0
