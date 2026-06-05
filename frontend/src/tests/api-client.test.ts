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
  it('returns NEXT_PUBLIC_API_URL when set in any environment', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_URL: 'https://backend.example.com',
      NEXT_PUBLIC_APP_ENV: 'production',
    });
    expect(url).toBe('https://backend.example.com');
  });

  it('falls back to localhost when APP_ENV is development', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: 'development',
    });
    expect(url).toBe('http://localhost:8000');
  });

  it('falls back to localhost when APP_ENV is local', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: 'local',
    });
    expect(url).toBe('http://localhost:8000');
  });

  it('falls back to localhost when APP_ENV is unset (defaults to development)', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: undefined,
    });
    expect(url).toBe('http://localhost:8000');
  });

  it('returns empty string in staging when URL is missing', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: 'staging',
    });
    expect(url).toBe('');
  });

  it('returns empty string in production when URL is missing', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_URL: undefined,
      NEXT_PUBLIC_APP_ENV: 'production',
    });
    expect(url).toBe('');
  });

  it('returns the set URL in staging (happy path)', async () => {
    const url = await resolveBaseUrl({
      NEXT_PUBLIC_API_URL: 'https://backend-staging.example.com',
      NEXT_PUBLIC_APP_ENV: 'staging',
    });
    expect(url).toBe('https://backend-staging.example.com');
  });
});
