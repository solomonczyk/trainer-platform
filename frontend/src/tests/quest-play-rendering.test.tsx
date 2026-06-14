import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// --- Mock Next.js navigation ---
vi.mock('next/navigation', () => ({
  useParams: () => ({ slug: 'qa-trainer', questId: 'qa_bug_report_structure_v1' }),
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

// --- Mock i18n ---
vi.mock('@/lib/i18n', () => ({
  tl: (key: string) => key || '',
}));

// --- Mock the API client ---
const apiMocks = vi.hoisted(() => ({
  startQuest: vi.fn(),
  submitQuestAnswer: vi.fn(),
  completeQuest: vi.fn(),
  getQuestProgress: vi.fn(),
  retryQuestEvaluation: vi.fn(),
  sendAnalyticsEvent: vi.fn(),
}));

vi.mock('@/lib/api/client', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...(actual as object),
    startQuest: apiMocks.startQuest,
    submitQuestAnswer: apiMocks.submitQuestAnswer,
    completeQuest: apiMocks.completeQuest,
    getQuestProgress: apiMocks.getQuestProgress,
    retryQuestEvaluation: apiMocks.retryQuestEvaluation,
    sendAnalyticsEvent: apiMocks.sendAnalyticsEvent,
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
}));

// --- Mock Button ---
vi.mock('@/components/ui/Button', () => ({
  default: ({ children, onClick, isLoading, disabled, size, className }: any) => (
    <button onClick={onClick} disabled={disabled || isLoading} data-testid="button" data-size={size} className={className}>
      {isLoading ? 'Loading...' : children}
    </button>
  ),
}));

// --- Mock Card ---
vi.mock('@/components/ui/Card', () => ({
  default: ({ children, padding }: any) => <div data-testid="card" data-padding={padding}>{children}</div>,
  CardHeader: ({ children }: any) => <div data-testid="card-header">{children}</div>,
  CardTitle: ({ children }: any) => <div data-testid="card-title">{children}</div>,
  CardContent: ({ children }: any) => <div data-testid="card-content">{children}</div>,
}));

import QuestPlayPage from '@/app/trainers/[slug]/quests/[questId]/page';

// --- Helper to render with QueryClient ---
const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
});
function renderWithQuery(ui: React.ReactElement) {
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

// Shared test data
const sampleQuest = {
  quest_id: 'qa_bug_report_structure_v1',
  trainer_slug: 'qa-trainer',
  version: '1.0',
  locale: 'ru-RU',
  title_key: 'quest.qa_bug_report.title',
  summary_key: 'quest.qa_bug_report.summary',
  learner_role_key: 'quest.qa_bug_report.role',
  mission_key: 'quest.qa_bug_report.mission',
  setting_key: 'quest.qa_bug_report.setting',
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

describe('QuestPlayPage — error state safety', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders loading state initially', () => {
    apiMocks.startQuest.mockReturnValue(new Promise(() => {}));
    renderWithQuery(<QuestPlayPage />);
    expect(screen.getByText('common.loading')).toBeDefined();
  });

  it('renders intro when quest loads successfully', async () => {
    apiMocks.startQuest.mockResolvedValue({
      session_id: 'session-1',
      quest: sampleQuest,
      current_step: sampleQuest.steps[0],
      narrative_state: sampleQuest.initial_state,
      status: 'started',
    });

    renderWithQuery(<QuestPlayPage />);

    await waitFor(() => {
      expect(screen.getByText('quest.qa_bug_report.title')).toBeDefined();
    });
    expect(screen.getByText('quest.start_quest')).toBeDefined();
  });

  it('shows error state on {"detail": "..."} without crashing', async () => {
    const { ApiClientError } = await import('@/lib/api/client');
    apiMocks.startQuest.mockRejectedValue(new ApiClientError({ detail: 'Quest not found' }));

    renderWithQuery(<QuestPlayPage />);

    await waitFor(() => {
      expect(screen.getByText('common.error')).toBeDefined();
    });
    expect(screen.getByText('Quest not found')).toBeDefined();
    expect(screen.queryByText(/Cannot read properties of undefined/i)).toBeNull();
  });

  it('shows error state on canonical format without crashing', async () => {
    const { ApiClientError } = await import('@/lib/api/client');
    apiMocks.startQuest.mockRejectedValue(
      new ApiClientError({ error: { code: 'SESSION_ERROR', message: 'Session expired', details: {}, request_id: 'r1' } })
    );

    renderWithQuery(<QuestPlayPage />);

    await waitFor(() => {
      expect(screen.getByText('common.error')).toBeDefined();
    });
    expect(screen.getByText('Session expired')).toBeDefined();
    expect(screen.queryByText(/Cannot read properties of undefined/i)).toBeNull();
  });

  it('shows error state on TypeError (network) without crashing', async () => {
    apiMocks.startQuest.mockRejectedValue(new TypeError('Failed to fetch'));

    renderWithQuery(<QuestPlayPage />);

    await waitFor(() => {
      expect(screen.getByText('common.error')).toBeDefined();
    });
    expect(screen.queryByText(/Cannot read properties of undefined/i)).toBeNull();
  });

  it('handles string error without crashing', async () => {
    const { ApiClientError } = await import('@/lib/api/client');
    apiMocks.startQuest.mockRejectedValue(new ApiClientError('Internal Server Error'));

    renderWithQuery(<QuestPlayPage />);

    await waitFor(() => {
      expect(screen.getByText('common.error')).toBeDefined();
    });
    expect(screen.getByText('Internal Server Error')).toBeDefined();
    expect(screen.queryByText(/Cannot read properties of undefined/i)).toBeNull();
  });

  it('handles null/undefined error without crashing', async () => {
    const { ApiClientError } = await import('@/lib/api/client');
    apiMocks.startQuest.mockRejectedValue(new ApiClientError(undefined));

    renderWithQuery(<QuestPlayPage />);

    await waitFor(() => {
      expect(screen.getByText('common.error')).toBeDefined();
    });
    expect(screen.getByText('An unexpected error occurred')).toBeDefined();
    expect(screen.queryByText(/Cannot read properties of undefined/i)).toBeNull();
  });

  it('shows outcome for completed quests (resume path) without crashing', async () => {
    apiMocks.getQuestProgress.mockResolvedValue({
      session_found: true, session_id: 'session-5', quest: sampleQuest,
      narrative_state: sampleQuest.initial_state, completed_step_ids: ['s1'],
      status: 'completed',
      outcome: { outcome_id: 'o1', title_key: 'outcome.title', summary_key: 'outcome.summary' },
      debrief: { strengths: [], mistakes: [], missed_risks: [], skill_results: [] },
    });
    localStorage.setItem('quest_session_qa_bug_report_structure_v1', 'session-5');

    renderWithQuery(<QuestPlayPage />);

    await waitFor(() => {
      expect(screen.getByText('quest.quest_complete')).toBeDefined();
    });
    expect(screen.getByText('outcome.title')).toBeDefined();
  });
});

describe('Interaction renderers — direct rendering safety', () => {
  it('SingleChoiceRenderer renders safely with empty options', async () => {
    const { SingleChoiceRenderer } = await import('@/features/quests/interaction-renderers');
    const step = { step_id: 's1', step_type: 'single_choice', story_context_key: '', prompt_key: '', interaction: {}, evaluation_mode: 'deterministic', consequences: {}, next_step_rules: {}, learning_objectives: [], skill_bindings: [] };
    const { container } = render(<SingleChoiceRenderer step={step as any} value={null} onChange={vi.fn()} disabled={false} />);
    // Should render an empty space without options (no crash)
    expect(container).toBeDefined();
  });

  it('MultipleChoiceRenderer renders safely with empty choices', async () => {
    const { MultipleChoiceRenderer } = await import('@/features/quests/interaction-renderers');
    const step = { step_id: 's2', step_type: 'multiple_choice', story_context_key: '', prompt_key: '', interaction: {}, evaluation_mode: 'deterministic', consequences: {}, next_step_rules: {}, learning_objectives: [], skill_bindings: [] };
    const { container } = render(<MultipleChoiceRenderer step={step as any} value={[]} onChange={vi.fn()} disabled={false} />);
    expect(container).toBeDefined();
  });

  it('FreeTextRenderer renders with null guidance safely', async () => {
    const { FreeTextRenderer } = await import('@/features/quests/interaction-renderers');
    const step = { step_id: 's3', step_type: 'free_text', story_context_key: '', prompt_key: '', interaction: { min_length: 50, max_length: 3000 }, evaluation_mode: 'ai_rubric', consequences: {}, next_step_rules: {}, learning_objectives: [], skill_bindings: [] };
    const { container } = render(<FreeTextRenderer step={step as any} value="" onChange={vi.fn()} disabled={false} />);
    expect(container).toBeDefined();
  });

  it('OrderingRenderer renders safely with empty items', async () => {
    const { OrderingRenderer } = await import('@/features/quests/interaction-renderers');
    const step = { step_id: 's4', step_type: 'ordering', story_context_key: '', prompt_key: '', interaction: {}, evaluation_mode: 'deterministic', consequences: {}, next_step_rules: {}, learning_objectives: [], skill_bindings: [] };
    const { container } = render(<OrderingRenderer step={step as any} value={[]} onChange={vi.fn()} disabled={false} />);
    expect(container).toBeDefined();
  });

  it('MatchingRenderer renders safely with empty items', async () => {
    const { MatchingRenderer } = await import('@/features/quests/interaction-renderers');
    const step = { step_id: 's5', step_type: 'matching', story_context_key: '', prompt_key: '', interaction: {}, evaluation_mode: 'deterministic', consequences: {}, next_step_rules: {}, learning_objectives: [], skill_bindings: [] };
    const { container } = render(<MatchingRenderer step={step as any} value={{}} onChange={vi.fn()} disabled={false} />);
    expect(container).toBeDefined();
  });

  it('EvidenceSelectRenderer renders safely with null items', async () => {
    const { EvidenceSelectRenderer } = await import('@/features/quests/interaction-renderers');
    const step = { step_id: 's6', step_type: 'evidence_select', story_context_key: '', prompt_key: '', interaction: {}, evaluation_mode: 'deterministic', consequences: {}, next_step_rules: {}, learning_objectives: [], skill_bindings: [] };
    const { container } = render(<EvidenceSelectRenderer step={step as any} value={[]} onChange={vi.fn()} disabled={false} />);
    expect(container).toBeDefined();
  });

  it('UnknownStepRenderer does not crash', async () => {
    const { UnknownStepRenderer } = await import('@/features/quests/interaction-renderers');
    const step = { step_id: 's7', step_type: 'unknown_type' as any, story_context_key: '', prompt_key: '', interaction: {}, evaluation_mode: 'deterministic', consequences: {}, next_step_rules: {}, learning_objectives: [], skill_bindings: [] };
    const { container } = render(<UnknownStepRenderer step={step as any} />);
    expect(container).toBeDefined();
  });
});

describe('Regression — undefined.message never shown', () => {
  it('normalizeApiError never produces "Cannot read properties of undefined"', async () => {
    const { normalizeApiError } = await import('@/lib/api/client');
    const cases = [
      undefined,
      null,
      { detail: 'Not found' },
      { error: undefined },
      { detail: null },
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
});
