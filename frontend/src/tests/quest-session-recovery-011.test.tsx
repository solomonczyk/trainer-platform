import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// --- Mock Next.js navigation ---
vi.mock('next/navigation', () => ({
  useParams: () => ({ slug: 'qa-engineer-interview-trainer', questId: 'qa_bug_report_structure_v1' }),
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

// --- Mock i18n ---
vi.mock('@/lib/i18n', () => ({
  tl: (key: string) => key || '',
  t: (key: string) => key || '',
  ti: (key: string, params?: Record<string, string | number>) => {
    let text = key || '';
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        text = text.replace(`{${k}}`, String(v));
      }
    }
    return text;
  },
}));

// --- Mock API client ---
const apiMocks = vi.hoisted(() => ({
  startQuest: vi.fn(),
  getQuestProgress: vi.fn(),
  sendAnalyticsEvent: vi.fn(),
  ApiClientError: class extends Error {
    code: string;
    status: number | undefined;
    constructor(msg: string, status?: number) {
      super(msg);
      this.name = 'ApiClientError';
      this.code = 'HTTP_ERROR';
      this.status = status;
    }
  },
}));

vi.mock('@/lib/api/client', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...(actual as object),
    startQuest: apiMocks.startQuest,
    getQuestProgress: apiMocks.getQuestProgress,
    sendAnalyticsEvent: apiMocks.sendAnalyticsEvent,
    ApiClientError: apiMocks.ApiClientError,
  };
});

// --- Mock lucide-react ---
vi.mock('lucide-react', () => ({
  AlertCircle: () => <div data-testid="icon-alert" />,
  CheckCircle: () => <div data-testid="icon-check" />,
  XCircle: () => <div data-testid="icon-x" />,
  Clock: () => <div data-testid="icon-clock" />,
  Loader2: () => <div data-testid="icon-loader" />,
  BookOpen: () => <div data-testid="icon-book" />,
  Target: () => <div data-testid="icon-target" />,
  Map: () => <div data-testid="icon-map" />,
  ChevronRight: () => <div data-testid="icon-chevron" />,
  RotateCcw: () => <div data-testid="icon-rotate" />,
  Star: () => <div data-testid="icon-star" />,
  TrendingUp: () => <div data-testid="icon-trend" />,
  Lightbulb: () => <div data-testid="icon-bulb" />,
  Award: () => <div data-testid="icon-award" />,
  BarChart3: () => <div data-testid="icon-chart" />,
  ArrowLeft: () => <div data-testid="icon-back" />,
  ArrowRight: () => <div data-testid="icon-arrow-right" />,
  Play: () => <div data-testid="icon-play" />,
  Layers: () => <div data-testid="icon-layers" />,
  ListChecks: () => <div data-testid="icon-list-checks" />,
  Eye: () => <div data-testid="icon-eye" />,
  FileText: () => <div data-testid="icon-file-text" />,
  Zap: () => <div data-testid="icon-zap" />,
  Users: () => <div data-testid="icon-users" />,
  GraduationCap: () => <div data-testid="icon-grad" />,
}));

// --- Mock Button ---
vi.mock('@/components/ui/Button', () => ({
  default: ({ children, onClick, isLoading, disabled }: any) => (
    <button onClick={onClick} disabled={disabled || isLoading} data-testid="button">
      {isLoading ? 'Loading...' : children}
    </button>
  ),
}));

// --- Mock Card ---
vi.mock('@/components/ui/Card', () => ({
  default: ({ children }: any) => <div data-testid="card">{children}</div>,
  CardHeader: ({ children }: any) => <div data-testid="card-header">{children}</div>,
  CardTitle: ({ children }: any) => <div data-testid="card-title">{children}</div>,
  CardContent: ({ children }: any) => <div data-testid="card-content">{children}</div>,
}));

// --- Mock remaining UI components ---
vi.mock('@/components/ui/Badge', () => ({
  default: ({ children, variant, size }: any) => <span data-testid="badge" data-variant={variant}>{children}</span>,
}));

vi.mock('@/components/ui/ProgressBar', () => ({
  default: () => <div data-testid="progress-bar" />,
}));

vi.mock('@/components/ui/PageContainer', () => ({
  default: ({ children, width }: any) => <div data-testid="page-container" data-width={width}>{children}</div>,
  SectionHeader: ({ title }: any) => <div data-testid="section-header">{title}</div>,
}));

vi.mock('@/components/ui/LoadingSpinner', () => ({
  default: ({ size, label }: any) => <div data-testid="loading" data-size={size}>{label}</div>,
}));

vi.mock('@/features/quests/status-meter', () => ({
  default: () => <div data-testid="status-meter" />,
}));

vi.mock('@/features/quests/learning-feedback-panel', () => ({
  default: () => <div data-testid="feedback-panel" />,
}));

vi.mock('@/features/quests/interaction-renderers', () => ({
  SingleChoiceRenderer: () => <div data-testid="renderer-single" />,
  MultipleChoiceRenderer: () => <div data-testid="renderer-multiple" />,
  FreeTextRenderer: () => <div data-testid="renderer-free" />,
  OrderingRenderer: () => <div data-testid="renderer-order" />,
  MatchingRenderer: () => <div data-testid="renderer-match" />,
  EvidenceSelectRenderer: () => <div data-testid="renderer-evidence" />,
  DecisionRenderer: () => <div data-testid="renderer-decision" />,
  DialogueRenderer: () => <div data-testid="renderer-dialogue" />,
  UnknownStepRenderer: () => <div data-testid="renderer-unknown" />,
}));

import QuestPlayPage from '@/app/trainers/[slug]/quests/[questId]/page';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
});

function renderWithQuery(ui: React.ReactElement) {
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

const sampleQuest = {
  quest_id: 'qa_bug_report_structure_v1',
  trainer_slug: 'qa-engineer-interview-trainer',
  version: '1.0',
  locale: 'ru-RU',
  title_key: 'quest.qa.bug_report.title',
  summary_key: 'quest.qa.bug_report.summary',
  learner_role_key: 'quest.qa.bug_report.role',
  mission_key: 'quest.qa.bug_report.mission',
  setting_key: 'quest.qa.bug_report.setting',
  estimated_minutes: 15,
  initial_state: { risk: 50, time_remaining: 80, team_trust: 70, client_trust: 60, evidence_quality: 40, decision_quality: 50 },
  steps: [
    { step_id: 's1', step_type: 'single_choice', story_context_key: 'ctx1', prompt_key: 'prompt1', interaction: { options: [{ id: 'a', text_key: 'opt_a' }, { id: 'b', text_key: 'opt_b' }] }, evaluation_mode: 'deterministic', consequences: {}, next_step_rules: { default: 's2' }, learning_objectives: [], skill_bindings: [] },
  ],
  outcomes: [{ outcome_id: 'o1', title_key: 'outcome.title', summary_key: 'outcome.summary', is_default: true }],
  debrief_contract: { sections: ['strengths', 'mistakes'], skill_dimensions: [] },
  characters: [{ id: 'c1', name_key: 'char.name', role_key: 'char.role' }],
  tags: ['qa'],
};

describe('Quest 011 — Stale session 404 recovery', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('handles 404 from getQuestProgress by falling through to startQuest', async () => {
    // Arrange: Set a stale session ID in localStorage
    localStorage.setItem('quest_session_qa_bug_report_structure_v1', 'stale-session-123');

    // getQuestProgress throws 404 (ApiClientError)
    const apiError404 = new apiMocks.ApiClientError('Session not found', 404);
    apiMocks.getQuestProgress.mockRejectedValue(apiError404);

    // startQuest succeeds
    apiMocks.startQuest.mockResolvedValue({
      session_id: 'fresh-session-456',
      quest: sampleQuest,
      current_step: sampleQuest.steps[0],
      narrative_state: sampleQuest.initial_state,
      status: 'started',
    });

    // Act: render the component
    renderWithQuery(<QuestPlayPage />);

    // Assert: wait for async init to complete
    await waitFor(() => {
      // getQuestProgress should have been called with the stale session
      expect(apiMocks.getQuestProgress).toHaveBeenCalledWith('stale-session-123');
    });

    await waitFor(() => {
      // After 404, startQuest should be called to create a fresh session
      // (instead of showing error screen)
      expect(apiMocks.startQuest).toHaveBeenCalledWith('qa_bug_report_structure_v1', 'ru-RU');
    });

    await waitFor(() => {
      // Stale session ID should be removed from localStorage
      expect(localStorage.getItem('quest_session_qa_bug_report_structure_v1')).toBe('fresh-session-456');
    });

    await waitFor(() => {
      // Intro screen should render (no error screen)
      expect(screen.getByTestId('icon-book')).toBeDefined();
    });
  });

  it('falls through to startQuest for any resume error (500, timeout, etc.)', async () => {
    // Arrange: Set a stale session ID in localStorage
    localStorage.setItem('quest_session_qa_bug_report_structure_v1', 'stale-session-789');

    // getQuestProgress throws ANY error (not just 404)
    const apiError500 = new apiMocks.ApiClientError('Server error', 500);
    apiMocks.getQuestProgress.mockRejectedValue(apiError500);

    // startQuest succeeds (recovery should clear stale state and create fresh session)
    apiMocks.startQuest.mockResolvedValue({
      session_id: 'recovered-session-789',
      quest: sampleQuest,
      current_step: sampleQuest.steps[0],
      narrative_state: sampleQuest.initial_state,
      status: 'started',
    });

    // Act
    renderWithQuery(<QuestPlayPage />);

    // Assert: getQuestProgress was attempted on stale session
    await waitFor(() => {
      expect(apiMocks.getQuestProgress).toHaveBeenCalledWith('stale-session-789');
    });

    await waitFor(() => {
      // startQuest IS called as recovery path
      expect(apiMocks.startQuest).toHaveBeenCalledWith('qa_bug_report_structure_v1', 'ru-RU');
    });

    await waitFor(() => {
      // Intro screen (not error) renders after recovery
      expect(screen.getByTestId('icon-book')).toBeDefined();
    });
  });
});

describe('Quest 011 — Start recommended quest contract', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('calls startQuest with correct quest_id and locale for fresh start', async () => {
    // Arrange: no saved session
    apiMocks.startQuest.mockResolvedValue({
      session_id: 'session-001',
      quest: sampleQuest,
      current_step: sampleQuest.steps[0],
      narrative_state: sampleQuest.initial_state,
      status: 'started',
    });

    // Act
    renderWithQuery(<QuestPlayPage />);

    // Assert: startQuest called with the correct quest_id
    await waitFor(() => {
      expect(apiMocks.startQuest).toHaveBeenCalledWith('qa_bug_report_structure_v1', 'ru-RU');
    });

    await waitFor(() => {
      // Session ID should be saved to localStorage
      expect(localStorage.getItem('quest_session_qa_bug_report_structure_v1')).toBe('session-001');
    });
  });

  it('resumes valid existing session via getQuestProgress', async () => {
    // Arrange: set a valid session ID
    localStorage.setItem('quest_session_qa_bug_report_structure_v1', 'valid-session-555');

    // getQuestProgress returns valid progress
    apiMocks.getQuestProgress.mockResolvedValue({
      session_found: true,
      session_id: 'valid-session-555',
      quest: sampleQuest,
      current_step: sampleQuest.steps[0],
      narrative_state: sampleQuest.initial_state,
      completed_step_ids: [],
      answers: {},
      status: 'in_progress',
    });

    // Act
    renderWithQuery(<QuestPlayPage />);

    // Assert: getQuestProgress called, startQuest NOT called (resume path)
    await waitFor(() => {
      expect(apiMocks.getQuestProgress).toHaveBeenCalledWith('valid-session-555');
    });

    await waitFor(() => {
      expect(apiMocks.startQuest).not.toHaveBeenCalled();
    });

    await waitFor(() => {
      // Ready state (not intro, not error) since we resumed
      // In mock world, tl returns key names, so check that we see the step prompt
      // The READY section renders after intro is bypassed on resume
      // We should not see the error screen
      expect(screen.queryByTestId('icon-alert')).toBeNull();
    });
  });
});
