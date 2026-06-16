import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// --- Mock next/navigation ---
vi.mock('next/navigation', () => ({
  useParams: () => ({ slug: 'ba-trainer' }),
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

// --- Mock i18n: return English translations so test assertions are stable ---
const mockT = vi.fn((key: string) => {
  const en: Record<string, string> = {
    'trainer.locale': 'Language',
    'trainer.targetAudience': 'Target Audience',
    'trainer.duration': 'Duration',
    'trainer.scenarios': 'Scenarios',
    'common.loading': 'Loading…',
    'common.error': 'Error',
    'common.retry': 'Retry',
    'trainer.notEnrolled': 'Not enrolled',
    'trainer.enrolled': 'Enrolled',
    'trainer.enroll': 'Enroll',
    'trainer.startQuest': 'Start Quest',
    'trainer.questsAvailable': 'Quests available',
    'trainer.enrolledMessage': 'Successfully enrolled!',
    'ba_trainer.modules': 'Modules',
    'ba_trainer.module_activities': 'Module Activities',
    'ba_trainer.phase_1_badge': 'Phase 1',
    'ba_trainer.activity_label': 'activities',
    'trainer.questCatalog': 'Quest Catalog',
    'trainer.questCatalogDesc': 'Browse all quests',
    'trainer.immersiveExperience': 'Immersive Experience',
    'trainer.immersiveExperienceDesc': 'Role-play real scenarios',
    'ba_phase2.title': 'Phase 2',
    'ba_phase2.description': 'Advanced scenarios',
    'ba_phase2.how_it_works_title': 'How it works',
    'ba_phase2.how_it_works_desc': 'Complete complex cases',
    'ba_phase2.start': 'Start',
    'recommended_quest.title': 'Recommended Quest',
    'recommended_quest.start_recommended': 'Start Recommended',
    'recommended_quest.browse_all': 'Browse All',
    'recommended_quest.for_ba': 'BA Payment Requirements Conflict',
    'recommended_quest.for_ba_reason': 'Practice requirements analysis',
    'recommended_quest.for_ba_skills': 'Core BA skills',
    'recommended_quest.for_ba_why': 'This quest covers key BA concepts',
    'recommended_quest.estimated_time_label': '{minutes} min',
    'recommended_quest.steps_label': '{count} steps',
    'recommended_quest.why_this_title': 'Why this quest',
  };
  return en[key] ?? key;
});

vi.mock('@/lib/i18n', () => ({
  t: (key: string) => mockT(key),
  tl: (key: string) => key || '',
  ti: (key: string) => key || '',
}));

// --- Mock API client ---
vi.mock('@/lib/api/client', () => ({
  getTrainer: vi.fn(),
  enrollTrainer: vi.fn(),
  isAuthenticated: () => false,
}));

// --- Mock lucide icons ---
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
}));

// --- Mock query hooks ---
const mockUseQuery = vi.fn();
vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual<typeof import('@tanstack/react-query')>('@tanstack/react-query');
  return {
    ...actual,
    useQuery: (opts: any) => mockUseQuery(opts),
  };
});

// Helper to render with QueryClient provider
function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe('Trainer Detail Page — Language Control', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('does NOT render a "Language" / "Язык" supported-locales card', async () => {
    // Arrange: mock API returning a trainer with supported_locales
    mockUseQuery.mockReturnValue({
      data: {
        slug: 'ba-trainer',
        trainer_product_id: 'business_analyst_interview_trainer',
        name: 'BA Trainer',
        description: 'Test description',
        is_enrolled: false,
        target_audience: ['analysts', 'developers'],
        supported_locales: ['ru-RU', 'en-US'],
        default_locale: 'ru-RU',
        scenario_count: 10,
      },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    // Lazy-import the page so mocks are in place first
    const { default: TrainerDetailPage } = await import('@/app/trainers/[slug]/page');

    const { container } = renderWithClient(<TrainerDetailPage />);

    // Wait for rendering to settle
    await vi.dynamicImportSettled?.();

    // The trainer.locale translation key maps to "Language" — verify no element
    // labeled "Language" exists as a card title (the supported-locales card)
    const languageElements = screen.queryAllByText('Language');
    expect(languageElements.length).toBe(0);

    // Also verify there's no Globe icon (was unique to the removed card)
    const globeIcons = container.querySelectorAll('[data-testid="icon-globe"]');
    expect(globeIcons.length).toBe(0);

    // The target-audience and duration cards should still be present
    expect(screen.getByText('Target Audience')).toBeTruthy();
    expect(screen.getByText('Duration')).toBeTruthy();
  });

  it('shows zero "Language" locale badge sections on the page', async () => {
    mockUseQuery.mockReturnValue({
      data: {
        slug: 'ba-trainer',
        trainer_product_id: 'business_analyst_interview_trainer',
        name: 'BA Trainer',
        description: 'Test description',
        is_enrolled: false,
        target_audience: ['analysts'],
        supported_locales: ['ru-RU', 'en-US', 'de-DE'],
        default_locale: 'en-US',
        scenario_count: 5,
      },
      isLoading: false,
      isError: false,
      error: null,
      refetch: vi.fn(),
    });

    const { default: TrainerDetailPage } = await import('@/app/trainers/[slug]/page');
    const { container } = renderWithClient(<TrainerDetailPage />);

    await vi.dynamicImportSettled?.();

    // The trainer should not render locale badges anywhere on the page
    const localeBadges = container.querySelectorAll('[class*="flex-wrap gap-2"]');
    // No card should contain locale badges (the only flex-wrap gap-2 was in the removed card)
    expect(localeBadges.length).toBe(0);
  });
});
