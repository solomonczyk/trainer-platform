import { describe, it, expect, beforeEach, vi } from 'vitest';

// Store original env so we can restore between tests
const ORIGINAL_ENV = { ...process.env };

beforeEach(() => {
  // Reset process.env to clean state before each test
  vi.resetModules();
});

/**
 * Helper: call the module's getApiBaseUrl by importing the module fresh.
 * We use dynamic import after setting env vars because the module evaluates
 * API_BASE at import time.
 */
async function resolveBaseUrl(envVars: Record<string, string | undefined>) {
  // Set env vars before importing the module
  for (const [key, val] of Object.entries(envVars)) {
    if (val === undefined) {
      delete process.env[key];
    } else {
      process.env[key] = val;
    }
  }
  const mod = await import('@/lib/api/client');
  return mod.getApiBaseUrl();
}

describe('getApiBaseUrl', () => {
  // ---------- Canonical: NEXT_PUBLIC_API_BASE_URL ----------

  it('returns NEXT_PUBLIC_API_BASE_URL when set in any environment', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: 'https://backend.example.com',
      NEXT_PUBLIC_APP_ENV: 'production',
    });
    expect(url).toBe('https://backend.example.com');
  });

  it('returns NEXT_PUBLIC_API_BASE_URL in staging when set', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: 'https://backend-staging.example.com',
      NEXT_PUBLIC_APP_ENV: 'staging',
    });
    expect(url).toBe('https://backend-staging.example.com');
  });

  it('returns NEXT_PUBLIC_API_BASE_URL in development when set', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: 'https://backend.dev.example.com',
      NEXT_PUBLIC_APP_ENV: 'development',
    });
    expect(url).toBe('https://backend.dev.example.com');
  });

  // ---------- Fallback to deprecated NEXT_PUBLIC_API_URL ----------

  it('falls back to NEXT_PUBLIC_API_URL when BASE_URL is not set', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: undefined,
      NEXT_PUBLIC_API_URL: 'https://backend-fallback.example.com',
      NEXT_PUBLIC_APP_ENV: 'production',
    });
    expect(url).toBe('https://backend-fallback.example.com');
  });

  // ---------- Development localhost fallback ----------

  it('falls back to localhost when APP_ENV is development', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: undefined,
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: 'development',
    });
    expect(url).toBe('http://localhost:8000');
  });

  it('falls back to localhost when APP_ENV is local', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: undefined,
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: 'local',
    });
    expect(url).toBe('http://localhost:8000');
  });

  it('falls back to localhost when APP_ENV is unset (defaults to development)', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: undefined,
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: undefined,
    });
    expect(url).toBe('http://localhost:8000');
  });

  // ---------- Staging / Production: NEVER localhost ----------

  it('returns empty string in staging when URL is missing (never localhost)', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: undefined,
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: 'staging',
    });
    expect(url).toBe('');
  });

  it('returns empty string in production when URL is missing (never localhost)', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: undefined,
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: 'production',
    });
    expect(url).toBe('');
  });

  it('staging never resolves to localhost', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: undefined,
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: 'staging',
    });
    expect(url).not.toBe('http://localhost:8000');
  });

  it('production never resolves to localhost', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: undefined,
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: 'production',
    });
    expect(url).not.toBe('http://localhost:8000');
  });

  // ---------- Register / Login endpoint resolution ----------

  it('register endpoint uses external backend when NEXT_PUBLIC_API_BASE_URL is set', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: 'https://backend-staging-0487.up.railway.app',
      NEXT_PUBLIC_APP_ENV: 'staging',
    });
    expect(url).toBe('https://backend-staging-0487.up.railway.app');
    // Verify the register endpoint URL would be correct
    expect(`${url}/api/v1/auth/register`).toBe(
      'https://backend-staging-0487.up.railway.app/api/v1/auth/register',
    );
  });

  it('login endpoint uses external backend when NEXT_PUBLIC_API_BASE_URL is set', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_BASE_URL: 'https://backend-staging-0487.up.railway.app',
      NEXT_PUBLIC_APP_ENV: 'staging',
    });
    expect(`${url}/api/v1/auth/login`).toBe(
      'https://backend-staging-0487.up.railway.app/api/v1/auth/login',
    );
  });
});
