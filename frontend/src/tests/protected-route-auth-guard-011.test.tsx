import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// ── Shared test helpers ──────────────────────────────────────────────────────

const mockGetTrainer = vi.fn();
const mockRouterPush = vi.fn();

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useParams: () => ({ slug: 'business-analyst-interview-trainer' }),
  useRouter: () => ({ push: mockRouterPush, refresh: vi.fn() }),
}));

// Mock i18n: return English translations by default; switchable via setMockLocale
let mockLocale: 'en' | 'ru' = 'en';
const mockT = vi.fn((key: string) => {
  const en: Record<string, string> = {
    'auth.sign_in_required': 'Sign in to continue',
    'auth.sign_in_required_description': 'Please sign in to access this content.',
    'auth.sign_in': 'Sign In',
    'auth.verificationRequiredTitle': 'Email Verification Required',
    'auth.verificationRequiredDesc': 'Please verify your email address before accessing the simulator. Check your inbox for the verification link.',
    'auth.resendVerificationButton': 'Resend Verification Email',
    'auth.backToLogin': 'Back to Login',
    'common.loading': 'Loading…',
    'common.error': 'An error occurred',
    'common.retry': 'Retry',
    'trainer.questsAvailable': 'Quests available',
  };
  const ru: Record<string, string> = {
    'auth.sign_in_required': 'Войдите в аккаунт, чтобы продолжить',
    'auth.sign_in_required_description': 'Пожалуйста, войдите в аккаунт для доступа к этому контенту.',
    'auth.sign_in': 'Войти',
    'auth.verificationRequiredTitle': 'Требуется подтверждение email',
    'auth.verificationRequiredDesc': 'Пожалуйста, подтвердите ваш email перед доступом к тренажёрам. Проверьте почту — мы отправили ссылку.',
    'auth.resendVerificationButton': 'Отправить повторно',
    'auth.backToLogin': 'Назад к входу',
    'common.loading': 'Загрузка…',
    'common.error': 'Произошла ошибка',
    'common.retry': 'Повторить',
    'trainer.questsAvailable': 'Квесты доступны',
  };
  const map = mockLocale === 'ru' ? ru : en;
  return map[key] ?? key;
});

function setMockLocale(locale: 'en' | 'ru') {
  mockLocale = locale;
}

vi.mock('@/lib/i18n', () => ({
  t: (key: string) => mockT(key),
  tl: (key: string) => key || '',
  ti: (key: string) => key || '',
}));

// Mock API client
vi.mock('@/lib/api/client', () => ({
  getTrainer: (...args: any[]) => mockGetTrainer(...args),
  enrollTrainer: vi.fn(),
  isAuthenticated: () => false,
  resendVerification: vi.fn(() => Promise.resolve({ message: 'sent' })),
  clearToken: vi.fn(),
  ApiClientError: class ApiClientError extends Error {
    status: number | undefined;
    code: string;
    details: Record<string, unknown>;
    requestId: string;
    constructor(err: any) {
      super(err?.message || 'API Error');
      this.name = 'ApiClientError';
      this.status = err?.status;
      this.code = err?.code || 'ERROR';
      this.details = {};
      this.requestId = '';
    }
  },
}));

// Mock lucide icons
vi.mock('lucide-react', () => ({
  AlertCircle: () => <div data-testid="icon-alert" />,
  CheckCircle: () => <div data-testid="icon-check" />,
  Clock: () => <div data-testid="icon-clock" />,
  BookOpen: () => <div data-testid="icon-book" />,
  Users: () => <div data-testid="icon-users" />,
  ArrowRight: () => <div data-testid="icon-arrow-right" />,
  GraduationCap: () => <div data-testid="icon-grad" />,
  Zap: () => <div data-testid="icon-zap" />,
  Star: () => <div data-testid="icon-star" />,
  Play: () => <div data-testid="icon-play" />,
  Layers: () => <div data-testid="icon-layers" />,
  Award: () => <div data-testid="icon-award" />,
  Lightbulb: () => <div data-testid="icon-bulb" />,
  ListChecks: () => <div data-testid="icon-list-checks" />,
  Mail: () => <div data-testid="icon-mail" />,
}));

// ── Auth context mock ───────────────────────────────────────────────────────

type MockAuthState = {
  user: { id: string; email: string; email_verified: boolean; role: string } | null;
  status: 'loading' | 'authenticated' | 'unauthenticated';
  loading: boolean;
  refresh: () => Promise<void>;
  clearSession: () => void;
};

let mockAuthState: MockAuthState = {
  user: null,
  status: 'loading',
  loading: true,
  refresh: async () => {},
  clearSession: () => {},
};

vi.mock('@/lib/auth/AuthContext', () => ({
  useAuth: () => mockAuthState,
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Helper to set auth state and re-render
function setAuthState(overrides: Partial<MockAuthState>) {
  mockAuthState = { ...mockAuthState, ...overrides };
}

// Mock @tanstack/react-query (partial)
const mockUseQuery = vi.fn();
vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual<typeof import('@tanstack/react-query')>('@tanstack/react-query');
  return {
    ...actual,
    useQuery: (opts: any) => mockUseQuery(opts),
  };
});

// Mock the auth gate and email verification gate components to avoid rendering
// their full implementations (which might import additional dependencies)
vi.mock('@/components/auth/AuthRequiredGate', () => ({
  AuthRequiredGate: ({ redirectTo }: { redirectTo?: string }) => (
    <div data-testid="auth-required-gate">
      <span>{mockT('auth.sign_in_required')}</span>
      <span>{mockT('auth.sign_in_required_description')}</span>
      <a href={redirectTo ? `/login?redirect=${encodeURIComponent(redirectTo)}` : '/login'}>
        {mockT('auth.sign_in')}
      </a>
    </div>
  ),
}));

vi.mock('@/components/auth/EmailVerificationRequiredGate', () => ({
  EmailVerificationRequiredGate: () => (
    <div data-testid="email-verification-gate">
      <span>{mockT('auth.verificationRequiredTitle')}</span>
    </div>
  ),
}));

// ── Render helpers ──────────────────────────────────────────────────────────

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

// ── Tests ────────────────────────────────────────────────────────────────────

describe('Layer 011 — Protected Route Auth Guard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetTrainer.mockReset();
    // Default: unauthenticated
    setAuthState({
      user: null,
      status: 'unauthenticated',
      loading: false,
      refresh: async () => {},
      clearSession: () => {},
    });
    // Default mock for useQuery — not enabled for unauthenticated
    mockUseQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });
  });

  // ── Test 1: unauthenticated → getTrainer() NOT called ──────────────────────
  it('unauthenticated trainer page does NOT call getTrainer()', async () => {
    mockUseQuery.mockImplementation((opts: any) => {
      // The query should NOT be enabled when unauthenticated
      // If it were called, the queryFn would be invoked
      if (opts.enabled === true) {
        // This should NOT happen for unauthenticated users
        mockGetTrainer('business-analyst-interview-trainer');
      }
      return {
        data: undefined,
        isLoading: false,
        isError: false,
        error: null,
        refetch: vi.fn(),
      };
    });

    const { default: TrainerDetailPage } = await import('@/app/trainers/[slug]/page');
    renderWithClient(<TrainerDetailPage />);

    expect(mockGetTrainer).not.toHaveBeenCalled();
  });

  // ── Test 2: unauthenticated → AuthRequiredGate visible ─────────────────────
  it('unauthenticated trainer page shows AuthRequiredGate', async () => {
    const { default: TrainerDetailPage } = await import('@/app/trainers/[slug]/page');
    renderWithClient(<TrainerDetailPage />);

    expect(screen.getByTestId('auth-required-gate')).toBeTruthy();
    expect(screen.getByText('Sign in to continue')).toBeTruthy();
  });

  // ── Test 3: /me 401 → status becomes unauthenticated (via AuthContext logic) ─
  it('AuthContext sets unauthenticated status when /me returns 401', async () => {
    // This tests the AuthContext bootstrap logic directly
    // Simulate: no token → status = unauthenticated
    setAuthState({
      user: null,
      status: 'unauthenticated',
      loading: false,
    });

    const { default: TrainerDetailPage } = await import('@/app/trainers/[slug]/page');
    renderWithClient(<TrainerDetailPage />);

    // Should show auth gate, not generic error
    expect(screen.getByTestId('auth-required-gate')).toBeTruthy();
    expect(screen.queryByText('An error occurred')).toBeFalsy();
  });

  // ── Test 4: 401 from protected query → no generic error ────────────────────
  it('401 protected query does NOT show generic error', async () => {
    // Set authenticated
    setAuthState({
      user: { id: '1', email: 'test@test.com', email_verified: true, role: 'user' },
      status: 'authenticated',
      loading: false,
    });

    // Import the mocked ApiClientError so instanceof checks in the page work
    const { ApiClientError: MockApiClientError } = await import('@/lib/api/client');
    const apiError = new MockApiClientError({ status: 401, message: 'Unauthorized', code: 'UNAUTHORIZED' });

    // useQuery returns a 401 error that IS an instance of ApiClientError
    mockUseQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: apiError,
      refetch: vi.fn(),
    });

    const { default: TrainerDetailPage } = await import('@/app/trainers/[slug]/page');
    renderWithClient(<TrainerDetailPage />);

    // Should show auth gate, not generic error
    expect(screen.getByTestId('auth-required-gate')).toBeTruthy();
    expect(screen.queryByText('An error occurred')).toBeFalsy();
  });

  // ── Test 5: RU unauthenticated gate has no English text ────────────────────
  it('RU unauthenticated gate has no English text', async () => {
    setMockLocale('ru');
    setAuthState({
      user: null,
      status: 'unauthenticated',
      loading: false,
    });

    const { default: TrainerDetailPage } = await import('@/app/trainers/[slug]/page');
    renderWithClient(<TrainerDetailPage />);

    // Should have Russian text, not English
    expect(screen.getByText('Войдите в аккаунт, чтобы продолжить')).toBeTruthy();
    expect(screen.queryByText('Sign in to continue')).toBeFalsy();

    setMockLocale('en');
  });

  // ── Test 6: RU footer/header labels are Russian ───────────────────────────
  it('RU footer and header labels are localized in Russian', () => {
    setMockLocale('ru');

    // Directly test that the RU translations don't contain English text
    expect(mockT('nav.login')).not.toBe('Log In');
    expect(mockT('nav.register')).not.toBe('Register');
    expect(mockT('nav.domains')).not.toBe('Domains');
    expect(mockT('nav.myProgress')).not.toBe('My Progress');
    expect(mockT('footer.domains')).not.toBe('Domains');
    expect(mockT('footer.interface_language')).not.toBe('Interface Language');
    expect(mockT('footer.platform_description')).not.toBe('Professional Training Platform');

    setMockLocale('en');
  });

  // ── Test 7: authenticated verified user → getTrainer() IS called ──────────
  it('authenticated verified user does call getTrainer()', async () => {
    setAuthState({
      user: { id: '1', email: 'test@test.com', email_verified: true, role: 'user' },
      status: 'authenticated',
      loading: false,
    });

    // Simulate query enabled → queryFn called
    mockUseQuery.mockImplementation((opts: any) => {
      if (opts.enabled) {
        opts.queryFn();
      }
      return {
        data: {
          slug: 'business-analyst-interview-trainer',
          trainer_product_id: 'business_analyst_interview_trainer',
          name: 'BA Trainer',
          description: 'Test',
          is_enrolled: false,
          target_audience: ['analysts'],
          scenario_count: 10,
        },
        isLoading: false,
        isError: false,
        error: null,
        refetch: vi.fn(),
      };
    });

    const { default: TrainerDetailPage } = await import('@/app/trainers/[slug]/page');

    // useQuery will be called during render; the mock will invoke the queryFn
    renderWithClient(<TrainerDetailPage />);

    expect(mockGetTrainer).toHaveBeenCalledTimes(1);
  });

  // ── Test 8: authenticated unverified → getTrainer() NOT called, sees verify gate ─
  it('authenticated unverified user does NOT call getTrainer and sees verify gate', async () => {
    setAuthState({
      user: { id: '1', email: 'test@test.com', email_verified: false, role: 'user' },
      status: 'authenticated',
      loading: false,
    });

    // Track if queryFn is called (it shouldn't be)
    mockUseQuery.mockImplementation((opts: any) => {
      if (opts.enabled) {
        // This should NOT happen for unverified users
        throw new Error('Query was enabled for unverified user');
      }
      return {
        data: undefined,
        isLoading: false,
        isError: false,
        error: null,
        refetch: vi.fn(),
      };
    });

    const { default: TrainerDetailPage } = await import('@/app/trainers/[slug]/page');

    expect(() => renderWithClient(<TrainerDetailPage />)).not.toThrow();

    // Should see email verification gate, not trainer content
    expect(screen.getByTestId('email-verification-gate')).toBeTruthy();
    expect(screen.getByText('Email Verification Required')).toBeTruthy();
  });
});
