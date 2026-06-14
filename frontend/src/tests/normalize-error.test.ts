import { describe, it, expect } from 'vitest';
import {
  normalizeApiError,
  ApiClientError,
  AppError,
} from '@/lib/api/client';

describe('normalizeApiError', () => {
  // ===================== ApiClientError =====================

  it('handles an ApiClientError instance', () => {
    const clientErr = new ApiClientError({
      code: 'SESSION_NOT_FOUND',
      message: 'Quest session not found',
      retryable: false,
    });
    const result = normalizeApiError(clientErr);
    expect(result.code).toBe('SESSION_NOT_FOUND');
    expect(result.message).toBe('Quest session not found');
  });

  it('marks 5xx errors as retryable from ApiClientError', () => {
    const clientErr = new ApiClientError({
      code: 'SERVER_ERROR',
      message: 'Internal server error',
      status: 500,
      retryable: false,
    });
    const result = normalizeApiError(clientErr);
    expect(result.retryable).toBe(true);
  });

  // ===================== Error instances =====================

  it('handles a plain TypeError (network failure)', () => {
    const typeErr = new TypeError('Failed to fetch');
    const result = normalizeApiError(typeErr);
    expect(result.code).toBe('NETWORK_ERROR');
    expect(result.message).toBe('Failed to fetch');
    expect(result.retryable).toBe(true);
  });

  it('handles a generic Error', () => {
    const err = new Error('Something broke');
    const result = normalizeApiError(err);
    expect(result.code).toBe('UNKNOWN_ERROR');
    expect(result.message).toBe('Something broke');
    expect(result.retryable).toBe(false);
  });

  // ===================== undefined / null =====================

  it('handles undefined input safely', () => {
    const result = normalizeApiError(undefined);
    expect(result.code).toBe('UNKNOWN');
    expect(result.message).toBe('An unexpected error occurred');
    expect(result.retryable).toBe(false);
  });

  it('handles null input safely', () => {
    const result = normalizeApiError(null);
    expect(result.code).toBe('UNKNOWN');
    expect(result.message).toBe('An unexpected error occurred');
  });

  // ===================== Backend detail string =====================

  it('handles {"detail": "Quest session not found"}', () => {
    const result = normalizeApiError({ detail: 'Quest session not found' });
    expect(result.code).toBe('HTTP_ERROR');
    expect(result.message).toBe('Quest session not found');
    expect(result.retryable).toBe(false);
  });

  // ===================== Backend detail object =====================

  it('handles {"detail": {"message": "...", "code": "..."}}', () => {
    const result = normalizeApiError({
      detail: { message: 'Quest session expired', code: 'QUEST_SESSION_EXPIRED' },
    });
    expect(result.code).toBe('QUEST_SESSION_EXPIRED');
    expect(result.message).toBe('Quest session expired');
  });

  // ===================== Canonical backend format =====================

  it('handles {"error": {"code": "...", "message": "..."}}', () => {
    const result = normalizeApiError({
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid input',
        details: { field: 'name' },
        request_id: 'req-123',
      },
    });
    expect(result.code).toBe('VALIDATION_ERROR');
    expect(result.message).toBe('Invalid input');
    expect(result.correlationId).toBe('req-123');
  });

  // ===================== errors array =====================

  it('handles {"errors": [{"message": "..."}]}', () => {
    const result = normalizeApiError({
      errors: [
        { message: 'Field is required', field: 'email' },
        { message: 'Must be valid email', field: 'email' },
      ],
    });
    expect(result.code).toBe('VALIDATION_ERROR');
    expect(result.message).toContain('Field is required');
    expect(result.fieldErrors?.email).toHaveLength(2);
  });

  // ===================== Non-JSON / network error =====================

  it('handles a string (status text / network error text)', () => {
    const result = normalizeApiError('Internal Server Error');
    expect(result.code).toBe('UNKNOWN_ERROR');
    expect(result.message).toBe('Internal Server Error');
  });

  it('handles empty string safely', () => {
    const result = normalizeApiError('');
    expect(result.code).toBe('UNKNOWN_ERROR');
    expect(result.message).toBe('');
  });

  // ===================== Malformed input =====================

  it('handles a number (unexpected primitive)', () => {
    const result = normalizeApiError(500);
    expect(result.code).toBe('UNKNOWN');
    expect(result.message).toBe('An unexpected error occurred');
  });

  it('handles an array instead of object', () => {
    const result = normalizeApiError(['error1', 'error2']);
    expect(result.code).toBe('UNKNOWN');
    expect(result.message).toBe('An unexpected error occurred');
  });

  // ===================== Known edge cases =====================

  it('handles {"detail": []} (empty array detail)', () => {
    const result = normalizeApiError({ detail: [] });
    expect(result.code).toBe('UNKNOWN');
    expect(result.message).toBe('An unexpected error occurred');
  });
});

describe('ApiClientError', () => {
  it('is an instance of Error', () => {
    const err = new ApiClientError('Test error');
    expect(err).toBeInstanceOf(Error);
    expect(err).toBeInstanceOf(ApiClientError);
  });

  it('never throws during construction with undefined', () => {
    expect(() => new ApiClientError(undefined)).not.toThrow();
    const err = new ApiClientError(undefined);
    expect(err.message).toBe('An unexpected error occurred');
  });

  it('never throws during construction with null', () => {
    expect(() => new ApiClientError(null)).not.toThrow();
    const err = new ApiClientError(null);
    expect(err.message).toBe('An unexpected error occurred');
  });

  it('extracts code and details from error object', () => {
    const err = new ApiClientError({
      code: 'NOT_FOUND',
      message: 'Not found',
      retryable: false,
    });
    expect(err.code).toBe('NOT_FOUND');
    expect(err.message).toBe('Not found');
  });

  it('extracts code from ApiError shape', () => {
    const err = new ApiClientError({
      error: { code: 'AUTH_FAILED', message: 'Bad token', details: {}, request_id: 'r1' },
    });
    expect(err.code).toBe('AUTH_FAILED');
    expect(err.message).toBe('Bad token');
    expect(err.requestId).toBe('r1');
  });

  it('extracts code from detail-string shape', () => {
    const err = new ApiClientError({ detail: 'Session not found' });
    expect(err.code).toBe('HTTP_ERROR');
    expect(err.message).toBe('Session not found');
  });

  it('preserves retryable flag', () => {
    const err = new ApiClientError({
      code: 'TIMEOUT',
      message: 'Request timed out',
      status: 504,
      retryable: true,
    });
    expect(err.status).toBe(504);
  });

  it('has name set to ApiClientError', () => {
    const err = new ApiClientError('test');
    expect(err.name).toBe('ApiClientError');
  });
});

describe('normalizeApiError regression — undefined.message contract', () => {
  it('NEVER produces "Cannot read properties of undefined" in message', () => {
    const cases: unknown[] = [
      undefined,
      null,
      { detail: 'Not found' },
      { error: undefined },
      { error: null },
      { message: null },
      { detail: null },
      { errors: null },
      new TypeError('Failed to fetch'),
      'Internal error',
      { detail: { message: 'expired' } },
      { errors: [{ message: 'Field required' }] },
    ];

    for (const input of cases) {
      const result = normalizeApiError(input);
      expect(result.message).not.toContain('Cannot read properties of undefined');
      expect(result.message).not.toContain('Cannot read properties');
    }
  });

  it('ApiClientError construction never throws TypeError for any input', () => {
    const inputs: unknown[] = [
      undefined,
      null,
      true,
      42,
      '',
      'error string',
      {},
      { error: undefined },
      { error: null },
      { detail: 'test' },
      { detail: { message: 'test' } },
      { message: 'test' },
      new Error('test'),
      new TypeError('network'),
      [],
      [1, 2, 3],
    ];

    for (const input of inputs) {
      expect(() => new ApiClientError(input)).not.toThrow();
    }
  });
});
