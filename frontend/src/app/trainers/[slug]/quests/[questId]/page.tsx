'use client';

import { useState, useCallback, useEffect, useMemo } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  startQuest,
  getQuestStep,
  submitQuestAnswer,
  retryQuestEvaluation,
  completeQuest,
  getQuestProgress,
  sendAnalyticsEvent,
  listQuests,
} from '@/lib/api/client';
import type {
  QuestDefinition,
  QuestStepDefinition,
  QuestAnswerResponse,
  QuestOutcomeResponse,
  QuestProgressResponse,
} from '@/lib/api/client';
import { tl, t, ti } from '@/lib/i18n';

import {
  SingleChoiceRenderer,
  MultipleChoiceRenderer,
  FreeTextRenderer,
  OrderingRenderer,
  MatchingRenderer,
  EvidenceSelectRenderer,
  DecisionRenderer,
  DialogueRenderer,
  UnknownStepRenderer,
} from '@/features/quests/interaction-renderers';

import StatusMeter from '@/features/quests/status-meter';
import LearningFeedbackPanel from '@/features/quests/learning-feedback-panel';

import {
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  BookOpen,
  Target,
  Map,
  ChevronRight,
  RotateCcw,
  Star,
  TrendingUp,
  Lightbulb,
  Award,
  BarChart3,
  ArrowLeft,
  Play,
  ListChecks,
  Users,
  Layers,
  Eye,
  FileText,
  Zap,
} from 'lucide-react';
import Button from '@/components/ui/Button';
import Card, { CardTitle, CardContent, CardHeader, CardDescription } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import PageContainer from '@/components/ui/PageContainer';
import ProgressBar from '@/components/ui/ProgressBar';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

type QuestPageState =
  | 'loading'
  | 'intro'
  | 'ready'
  | 'submitting'
  | 'evaluating'
  | 'feedback'
  | 'timed_out'
  | 'failed'
  | 'outcome'
  | 'debrief'
  | 'mistakes_review'
  | 'next_action'
  | 'error';

// Professional sample content for educational debrief
const PROFESSIONAL_SAMPLES: Record<string, { title: string; content: string[] }> = {
  'qa.bug_report': {
    title: 'Professional Bug Report Example',
    content: [
      'Title: Place Order button unresponsive after upgrade to v2.5.1 on Chrome 120',
      'Environment: Windows 11, Chrome 120, App v2.5.1 (upgraded from v2.5.0)',
      'Preconditions: User is logged in, has items in cart, payment method saved',
      'Steps to Reproduce: 1. Navigate to /checkout 2. Click "Place Order" button 3. Observe no response from UI 4. Check browser console — no JS errors',
      'Actual Result: "Place Order" button does not respond to click events. No error in console. Other browsers (Firefox, Edge) work correctly.',
      'Expected Result: Clicking "Place Order" submits the order and redirects to confirmation page.',
      'Severity: Critical — blocks core purchase flow for Chrome 120 users',
      'Priority: Critical — affects all Chrome 120 users (estimated 40% of traffic)',
      'Attachments: Console screenshot, HAR export, screen recording of behavior',
    ],
  },
  'qa.payment_defect': {
    title: 'Professional Bug Report Example (Payment Defect)',
    content: [
      'Title: Intermittent payment callback failure due to race condition in payment handler v3.1',
      'Environment: Production — all browsers. Payment gateway: Stripe API v2023-10. App version: 4.2.1',
      'Steps to Reproduce: 1. Initiate payment with any card type 2. Complete 3DS authentication 3. Observe ~15% of callbacks fail to reach confirmation handler',
      'Actual Result: Race condition in PaymentCallbackHandler.process() — concurrent callbacks from Stripe webhook and client-side redirect collide, causing double-processing error and transaction rollback.',
      'Expected Result: Payment completes reliably for 100% of legitimate transactions. Callback handler must be idempotent and thread-safe.',
      'Severity: Critical — causes financial loss (15% transaction failure), data inconsistency, customer trust damage',
      'Priority: Critical — block release, fix before next deployment',
      'Impact: ~15% of all payments fail. Estimated monthly loss: $45,000 at current volume. Customer support tickets increased 3x.',
    ],
  },
  'ba.payment_conflict': {
    title: 'Professional Acceptance Criterion Example',
    content: [
      'Given the user has selected items for purchase and is on the checkout page',
      'When the user submits payment with a valid card',
      'Then the payment is processed through PCI-DSS compliant gateway',
      'And the user sees a clear confirmation with order number within 3 seconds',
      'And if the payment fails due to a transient error, the system retries automatically up to 2 times with 5-second intervals',
      'And the user is informed of the retry status with a progress indicator',
      'And if all retries fail, the user sees a clear error message with alternative payment options',
      'And a support ticket is automatically created for failed payments',
      'Acceptance Criteria Notes:',
      '- PCI-DSS compliance checks (encryption, tokenization) run before any transaction',
      '- Transaction log records every attempt with status, timestamp, and error code',
      '- Failed payment recovery path guides user to retry or use alternative method',
      '- All user-facing messages are non-technical and include next steps',
    ],
  },
};

// Skills per quest for mission intro and debrief
const QUEST_SKILLS: Record<string, { skills: string[]; minutes: number }> = {
  'qa.bug_report': {
    skills: ['Bug report structure', 'Severity vs Priority', 'Professional writing', 'Evidence analysis'],
    minutes: 15,
  },
  'qa.payment_defect': {
    skills: ['Incident triage', 'Evidence selection', 'Release decision', 'Stakeholder communication'],
    minutes: 20,
  },
  'ba.payment_conflict': {
    skills: ['Stakeholder analysis', 'Conflict resolution', 'Acceptance criteria', 'Requirements documentation'],
    minutes: 20,
  },
};

export default function QuestPlayPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;
  const questId = params?.questId as string;

  const [pageState, setPageState] = useState<QuestPageState>('loading');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [quest, setQuest] = useState<QuestDefinition | null>(null);
  const [currentStep, setCurrentStep] = useState<QuestStepDefinition | null>(null);
  const [narrativeState, setNarrativeState] = useState<Record<string, number>>({});
  const [completedStepIds, setCompletedStepIds] = useState<string[]>([]);
  const [stepAnswer, setStepAnswer] = useState<unknown>(null);
  const [stepUserText, setStepUserText] = useState('');
  const [evaluationResult, setEvaluationResult] = useState<QuestAnswerResponse | null>(null);
  const [outcomeResult, setOutcomeResult] = useState<QuestOutcomeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [consequenceMessage, setConsequenceMessage] = useState('');
  const [stepIndex, setStepIndex] = useState(1);
  const [isTerminalStep, setIsTerminalStep] = useState(false);
  const [stepResults, setStepResults] = useState<Record<string, QuestAnswerResponse>>({});
  const [reviewStepIndex, setReviewStepIndex] = useState(0);

  // All quests for cross-referencing
  const { data: allQuestsData } = useQuery({
    queryKey: ['quests'],
    queryFn: () => listQuests(),
    enabled: pageState === 'debrief' || pageState === 'outcome' || pageState === 'next_action',
  });

  // Try to resume session from localStorage
  const savedSessionId = typeof window !== 'undefined' ? localStorage.getItem(`quest_session_${questId}`) : null;

  // Determine recommended quest IDs
  const isQA = slug.includes('qa') || (slug || '').replace(/-/g, '_').includes('qa');
  const recommendedQuestId = isQA ? 'qa.bug_report' : 'ba.payment_conflict';
  const secondQuestId = isQA ? 'qa.payment_defect' : 'qa.bug_report';

  // Get quest skills
  const questSkills = QUEST_SKILLS[questId] || { skills: ['Professional skills'], minutes: 15 };
  const isRecommendedQuest = questId === recommendedQuestId;

  // Professional sample for current quest
  const professionalSample = PROFESSIONAL_SAMPLES[questId];

  // Load or resume quest
  useEffect(() => {
    async function init() {
      try {
        if (savedSessionId) {
          // Try to resume
          const progress = await getQuestProgress(savedSessionId);
          if (progress.session_found && progress.quest) {
            setSessionId(progress.session_id!);
            setQuest(progress.quest);
            setNarrativeState(progress.narrative_state || {});
            setCompletedStepIds(progress.completed_step_ids || []);
            setStepIndex((progress.completed_step_ids?.length || 0) + 1);
            setStepResults((progress as any).step_results || {});

            if (progress.status === 'completed') {
              setOutcomeResult({
                session_id: progress.session_id!,
                outcome_id: progress.outcome?.outcome_id || '',
                outcome_title_key: progress.outcome?.title_key || '',
                outcome_summary_key: progress.outcome?.summary_key || '',
                narrative_state: progress.narrative_state || {},
                debrief: progress.debrief || {},
                status: 'completed',
              });
              setPageState('outcome');
              return;
            }

            if (progress.current_step) {
              setCurrentStep(progress.current_step);
              setPageState('ready');
              return;
            }
          }
        }

        // Fresh start
        const data = await startQuest(questId, 'ru-RU');
        setSessionId(data.session_id);
        setQuest(data.quest);
        setCurrentStep(data.current_step);
        setNarrativeState(data.narrative_state);
        setPageState('intro');
        localStorage.setItem(`quest_session_${questId}`, data.session_id);
        sendAnalyticsEvent('quest_started', {
          trainer_slug: slug, scenario_id: questId,
        });
      } catch (err) {
        setErrorMessage(err instanceof Error ? err.message : 'Failed to load quest');
        setPageState('error');
      }
    }
    init();
  }, [questId, slug, savedSessionId]);

  const handleStart = () => {
    setPageState('ready');
  };

  const handleAnswerChange = useCallback((value: unknown) => {
    setStepAnswer(value);
  }, []);

  const handleUserTextChange = useCallback((value: string) => {
    setStepUserText(value);
  }, []);

  const submitMutation = useMutation({
    mutationFn: async () => {
      if (!sessionId || !currentStep) throw new Error('No active session');
      const idempotencyKey = `${sessionId}_${currentStep.step_id}_${Date.now()}`;

      let answer = stepAnswer;
      if (currentStep.step_type === 'free_text') {
        answer = { value: stepUserText };
      } else if (currentStep.step_type === 'dialogue') {
        const step = currentStep as QuestStepDefinition;
        const allowFreeText = step.interaction?.allow_free_text as boolean;
        if (allowFreeText && !answer) {
          answer = { value: stepUserText };
        } else if (typeof answer === 'string') {
          answer = { value: answer, choice_id: answer };
        }
      } else if (typeof answer === 'string') {
        answer = { value: answer };
      }

      return submitQuestAnswer(sessionId, {
        step_id: currentStep.step_id,
        answer,
        idempotency_key: idempotencyKey,
        locale: 'ru-RU',
      });
    },
    onSuccess: (data) => {
      setNarrativeState(data.narrative_state);
      setEvaluationResult(data);

      // Store step results for mistakes review
      setStepResults((prev) => ({ ...prev, [data.step_id]: data }));

      if (data.timed_out) {
        setPageState('timed_out');
        sendAnalyticsEvent('quest_evaluation_timed_out', {
          trainer_slug: slug, scenario_id: questId,
        });
        return;
      }

      if (data.status === 'completed') {
        setCompletedStepIds((prev) => [...prev, data.step_id]);
        setStepIndex((prev) => prev + 1);

        if (data.next_step_id === '__terminal__') {
          // All steps done — show feedback, user clicks Continue to complete
          setIsTerminalStep(true);
        } else if (data.next_step) {
          // Show feedback panel — user clicks Continue to advance
          setIsTerminalStep(false);
        }
        setPageState('feedback');
      } else if (data.status === 'timed_out') {
        setPageState('timed_out');
      } else {
        setPageState('feedback');
      }

      // Show consequence message
      if (data.consequence_updates) {
        const updates = data.consequence_updates;
        const parts: string[] = [];
        if (updates.risk) parts.push(`Risk ${updates.risk > 0 ? '+' : ''}${updates.risk}`);
        if (updates.team_trust) parts.push(`Team ${updates.team_trust > 0 ? '+' : ''}${updates.team_trust}`);
        if (updates.client_trust) parts.push(`Client ${updates.client_trust > 0 ? '+' : ''}${updates.client_trust}`);
        if (updates.decision_quality) parts.push(`Decision ${updates.decision_quality > 0 ? '+' : ''}${updates.decision_quality}`);
        if (updates.evidence_quality) parts.push(`Evidence ${updates.evidence_quality > 0 ? '+' : ''}${updates.evidence_quality}`);
        if (parts.length > 0) {
          setConsequenceMessage(parts.join(' | '));
        }
      }
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || 'Failed to submit answer');
      if (err.message?.includes('timed out') || err.message?.includes('timeout')) {
        setPageState('timed_out');
      } else {
        setPageState('failed');
      }
    },
  });

  const retryMutation = useMutation({
    mutationFn: async () => {
      if (!sessionId || !currentStep) throw new Error('No active session');
      const idempotencyKey = `${sessionId}_retry_${currentStep.step_id}_${Date.now()}`;
      return retryQuestEvaluation(sessionId, {
        step_id: currentStep.step_id,
        locale: 'ru-RU',
        idempotency_key: idempotencyKey,
      });
    },
    onSuccess: (data) => {
      setNarrativeState(data.narrative_state);
      setEvaluationResult(data);
      setStepResults((prev) => ({ ...prev, [data.step_id]: data }));
      if (data.timed_out) {
        setPageState('timed_out');
      } else {
        if (data.next_step_id === '__terminal__') {
          setIsTerminalStep(true);
        } else {
          setIsTerminalStep(false);
        }
        setPageState('feedback');
      }
    },
    onError: () => {
      setPageState('failed');
    },
  });

  const handleSubmit = () => {
    if (!currentStep) return;
    setErrorMessage('');
    setConsequenceMessage('');
    setPageState('submitting');
    submitMutation.mutate();
  };

  const handleRetry = () => {
    setErrorMessage('');
    setPageState('evaluating');
    retryMutation.mutate();
  };

  const handleReset = () => {
    localStorage.removeItem(`quest_session_${questId}`);
    router.refresh();
    window.location.reload();
  };

  const handleBackToTrainer = () => {
    localStorage.removeItem(`quest_session_${questId}`);
    router.push(`/trainers/${slug}`);
  };

  const handleBackToCatalog = () => {
    localStorage.removeItem(`quest_session_${questId}`);
    router.push(`/trainers/${slug}/quests`);
  };

  const handleViewDebrief = () => {
    setPageState('debrief');
  };

  const handleViewMistakesReview = () => {
    setPageState('mistakes_review');
  };

  const handleShowNextAction = () => {
    setPageState('next_action');
  };

  const handleContinue = useCallback(async () => {
    if (isTerminalStep) {
      // Complete quest
      try {
        if (!sessionId) return;
        const outcome = await completeQuest(sessionId);
        setOutcomeResult(outcome);
        setPageState('outcome');
        sendAnalyticsEvent('quest_completed', {
          trainer_slug: slug, scenario_id: questId,
          properties: { outcome_id: outcome.outcome_id },
        });
      } catch {
        setErrorMessage('Could not complete quest');
        setPageState('error');
      }
    } else if (evaluationResult?.next_step) {
      // Advance to next step
      setCurrentStep(evaluationResult.next_step);
      setStepAnswer(null);
      setStepUserText('');
      setEvaluationResult(null);
      setIsTerminalStep(false);
      setPageState('ready');
    }
  }, [isTerminalStep, sessionId, evaluationResult, slug, questId]);

  // ===================== RENDER =====================

  // LOADING
  if (pageState === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" label={tl('common.loading')} />
      </div>
    );
  }

  // ERROR
  if (pageState === 'error') {
    return (
      <PageContainer width="narrow">
        <Card padding="lg" variant="default" className="text-center border-danger-200">
          <div className="flex flex-col items-center gap-4 py-6">
            <AlertCircle className="h-12 w-12 text-text-danger" />
            <h2 className="text-h3 text-foreground">{tl('common.error')}</h2>
            <p className="text-body-sm text-text-secondary">{errorMessage || tl('quest.error_loading')}</p>
            <div className="flex gap-3">
              <Button onClick={handleReset}>{tl('quest.try_again')}</Button>
              <Button variant="outline" onClick={handleBackToTrainer}>{tl('quest.back_to_catalog')}</Button>
            </div>
          </div>
        </Card>
      </PageContainer>
    );
  }

  // INTRO — IMPROVED MISSION INTRO
  if (pageState === 'intro' && quest && currentStep) {
    const totalSteps = quest.steps.length;
    const interactionTypes = quest.steps.map(s => s.step_type);
    const uniqueTypes = [...new Set(interactionTypes)];

    return (
      <PageContainer>
        {/* Step indicator */}
        <div className="mb-8 flex items-center gap-2 text-label text-text-secondary">
          <Map className="h-5 w-5" />
          <span>{tl('quest.step_of').replace('{current}', '0').replace('{total}', String(totalSteps))}</span>
        </div>

        <Card padding="lg" variant="elevated" className="border-2 border-selected shadow-elevated">
          <div className="mb-10 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-primary-50 mb-6">
              <BookOpen className="h-10 w-10 text-primary-600" />
            </div>
            <h1 className="text-display text-foreground mb-3 leading-tight">
              {tl(quest.title_key)}
            </h1>
            <p className="text-body-lg text-text-secondary leading-relaxed max-w-2xl mx-auto">
              {tl(quest.summary_key)}
            </p>
          </div>

          {/* Quick info bar — estimated time, steps, interaction types */}
          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-50 border border-primary-200">
              <Clock className="h-4 w-4 text-primary-600" />
              <span className="text-body-sm font-medium text-primary-700">
                {ti('mission_intro.estimated_time_short', { minutes: String(questSkills.minutes) })}
              </span>
            </div>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-50 border border-purple-200">
              <Layers className="h-4 w-4 text-purple-600" />
              <span className="text-body-sm font-medium text-purple-700">
                {tl('quest.steps_count').replace('{count}', String(totalSteps))}
              </span>
            </div>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-muted border border-default">
              <ListChecks className="h-4 w-4 text-text-muted" />
              <span className="text-body-sm font-medium text-text-secondary">
                {uniqueTypes.length} {tl('mission_intro.interaction_types_label')}
              </span>
            </div>
          </div>

          {/* Role, Mission, Setting */}
          <div className="space-y-5 mb-10">
            <div className="p-5 rounded bg-primary-50 border border-primary-200">
              <div className="flex items-center gap-2 mb-2">
                <Target className="h-5 w-5 text-primary-600" />
                <span className="text-caption font-bold uppercase tracking-wider text-primary-700">{tl('quest.your_role')}</span>
              </div>
              <p className="text-body-lg text-primary-800 font-semibold">{tl(quest.learner_role_key)}</p>
            </div>

            <div className="p-5 rounded bg-purple-50 border border-purple-200">
              <div className="flex items-center gap-2 mb-2">
                <Award className="h-5 w-5 text-purple-600" />
                <span className="text-caption font-bold uppercase tracking-wider text-purple-700">{tl('quest.mission')}</span>
              </div>
              <p className="text-body-lg text-purple-800 leading-relaxed">{tl(quest.mission_key)}</p>
            </div>

            <div className="p-5 rounded bg-muted border border-default">
              <div className="flex items-center gap-2 mb-2">
                <Map className="h-5 w-5 text-text-muted" />
                <span className="text-caption font-bold uppercase tracking-wider text-text-secondary">{tl('quest.setting')}</span>
              </div>
              <p className="text-body-lg text-foreground leading-relaxed">{tl(quest.setting_key)}</p>
            </div>

            {/* Characters */}
            {quest.characters && quest.characters.length > 0 && (
              <div>
                <h3 className="text-caption font-bold uppercase tracking-wider text-text-secondary mb-3">{tl('quest.characters')}</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {quest.characters.map((ch) => (
                    <div key={ch.id} className="p-4 rounded bg-surface border border-default shadow-sm">
                      <p className="text-body font-semibold text-foreground">{tl(ch.name_key)}</p>
                      <p className="text-body-sm text-text-secondary mt-1">{tl(ch.role_key)}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Skills trained */}
          <div className="mb-6 p-5 rounded bg-muted border border-default">
            <h3 className="text-caption font-bold uppercase tracking-wider text-text-secondary mb-3">
              <Award className="h-4 w-4 inline mr-1" />
              {tl('mission_intro.skills_trained')}
            </h3>
            <p className="text-body-sm text-text-secondary mb-2">{tl('mission_intro.skills_list')}:</p>
            <div className="flex flex-wrap gap-2">
              {questSkills.skills.map((skill, idx) => (
                <Badge key={idx} variant="primary" size="sm">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  {skill}
                </Badge>
              ))}
            </div>
          </div>

          {/* How feedback works */}
          <div className="mb-6 p-5 rounded bg-success-50 border border-success-200">
            <h3 className="text-caption font-bold uppercase tracking-wider text-success-700 mb-2">
              <Lightbulb className="h-4 w-4 inline mr-1" />
              {tl('mission_intro.how_feedback_works')}
            </h3>
            <p className="text-body-sm text-success-700 leading-relaxed">
              {tl('mission_intro.how_feedback_desc')}
            </p>
          </div>

          {/* Narrative bars */}
          <div className="mb-8">
            <h3 className="text-label text-text-secondary mb-3">{tl('quest.narrative_state')}</h3>
            <StatusMeter state={narrativeState} />
          </div>

          <div className="flex justify-center">
            <Button size="lg" onClick={handleStart} className="w-full sm:w-auto px-8 py-3 text-body shadow-md">
              {tl('mission_intro.start_mission')}
              <ChevronRight className="h-5 w-5" />
            </Button>
          </div>
        </Card>
      </PageContainer>
    );
  }

  // READY — active step
  if ((pageState === 'ready' || pageState === 'submitting') && quest && currentStep) {
    const totalSteps = quest.steps.length;
    const isSubmitting = pageState === 'submitting';
    const progressPercent = totalSteps > 0 ? Math.round((completedStepIds.length / totalSteps) * 100) : 0;

    const renderStep = () => {
      const step = currentStep as QuestStepDefinition;
      switch (step.step_type) {
        case 'single_choice':
          return (
            <SingleChoiceRenderer
              step={step}
              value={stepAnswer as string | null}
              onChange={handleAnswerChange}
              disabled={isSubmitting}
            />
          );
        case 'multiple_choice':
          return (
            <MultipleChoiceRenderer
              step={step}
              value={(stepAnswer ?? []) as string[]}
              onChange={handleAnswerChange}
              disabled={isSubmitting}
            />
          );
        case 'free_text':
          return (
            <FreeTextRenderer
              step={step}
              value={stepUserText}
              onChange={handleUserTextChange}
              disabled={isSubmitting}
            />
          );
        case 'ordering':
          return (
            <OrderingRenderer
              step={step}
              value={(stepAnswer ?? []) as string[]}
              onChange={handleAnswerChange}
              disabled={isSubmitting}
            />
          );
        case 'matching':
          return (
            <MatchingRenderer
              step={step}
              value={(stepAnswer ?? {}) as Record<string, string>}
              onChange={handleAnswerChange}
              disabled={isSubmitting}
            />
          );
        case 'evidence_select':
          return (
            <EvidenceSelectRenderer
              step={step}
              value={(stepAnswer ?? []) as string[]}
              onChange={handleAnswerChange}
              disabled={isSubmitting}
            />
          );
        case 'decision':
          return (
            <DecisionRenderer
              step={step}
              value={stepAnswer as string | null}
              onChange={handleAnswerChange}
              disabled={isSubmitting}
            />
          );
        case 'dialogue':
          return (
            <DialogueRenderer
              step={step}
              value={stepAnswer as string | null}
              onChange={handleAnswerChange}
              disabled={isSubmitting}
              userValue={stepUserText}
              onUserValueChange={handleUserTextChange}
            />
          );
        default:
          return <UnknownStepRenderer step={step} />;
      }
    };

    // Check if answer is valid
    const hasAnswer = (() => {
      switch (currentStep.step_type) {
        case 'single_choice':
        case 'decision':
        case 'branching':
          return !!stepAnswer;
        case 'multiple_choice':
        case 'evidence_select':
          return Array.isArray(stepAnswer) && stepAnswer.length > 0;
        case 'ordering':
          return Array.isArray(stepAnswer) && stepAnswer.length > 0;
        case 'matching':
          return typeof stepAnswer === 'object' && stepAnswer !== null && Object.keys(stepAnswer as object).length > 0;
        case 'free_text':
          return stepUserText.trim().length >= ((currentStep.interaction?.min_length as number) || 0);
        case 'dialogue':
          if (currentStep.interaction?.allow_free_text) return stepUserText.trim().length > 0;
          return !!stepAnswer;
        default:
          return !!stepAnswer;
      }
    })();

    return (
      <PageContainer>
        {/* Progress Header — stepper style */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3 text-label font-semibold text-text-secondary">
              <Map className="h-5 w-5 text-primary-600" />
              <span>{tl('quest.step_of').replace('{current}', String(stepIndex)).replace('{total}', String(totalSteps))}</span>
            </div>
            {currentStep.evaluation_mode === 'ai_rubric' && (
              <Badge variant="primary" size="sm">
                <Award className="h-4 w-4" /> AI Evaluated
              </Badge>
            )}
          </div>
          {/* Progress bar */}
          <ProgressBar
            value={completedStepIds.length}
            max={totalSteps}
            size="lg"
            barClassName="bg-gradient-to-r from-primary-500 to-primary-600"
            className="relative"
          />
          <span className="block text-right mt-1 text-body-sm font-medium text-text-secondary">
            {completedStepIds.length}/{totalSteps}
          </span>
        </div>

        {/* Narrative Status */}
        <div className="mb-8 p-4 rounded bg-muted border border-default shadow-sm">
          <h3 className="text-label text-text-secondary mb-3">{tl('quest.narrative_state')}</h3>
          <StatusMeter state={narrativeState} />
        </div>

        <Card padding="lg" variant="default" className="border-2 shadow-md">
          {/* Story Context */}
          {currentStep.story_context_key && (
            <div className="mb-8 p-5 rounded bg-muted border border-default">
              <div className="flex items-center gap-2 mb-3">
                <BookOpen className="h-5 w-5 text-text-muted" />
                <span className="text-caption font-bold uppercase tracking-wider text-text-secondary">{tl('quest.story_context')}</span>
              </div>
              <p className="text-body-lg text-foreground leading-relaxed">
                {tl(currentStep.story_context_key)}
              </p>
            </div>
          )}

          {/* Prompt */}
          <div className="mb-8">
            <h2 className="text-h2 text-foreground mb-2 leading-tight">
              {tl(currentStep.prompt_key)}
            </h2>
            <p className="text-body-sm font-medium text-text-secondary">{tl(`quest.step_${currentStep.step_type}`)}</p>
          </div>

          {/* Interaction */}
          <div className="mb-8">
            {renderStep()}
          </div>

          {/* Error message */}
          {errorMessage && (
            <div className="mb-6 flex items-center gap-3 rounded bg-danger-50 p-4 text-body font-medium text-danger-700 border border-danger-200">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              {errorMessage}
            </div>
          )}

          {/* Submit / Next */}
          <div className="flex justify-end pt-6 border-t-2 border-default">
            <Button
              onClick={handleSubmit}
              isLoading={isSubmitting}
              disabled={!hasAnswer || isSubmitting}
              size="lg"
              className="px-8 py-3 text-body shadow-md"
            >
              {isSubmitting ? tl('quest.submitting') : tl('quest.next_step')}
            </Button>
          </div>
        </Card>
      </PageContainer>
    );
  }

  // EVALUATING
  if (pageState === 'evaluating') {
    return (
      <PageContainer width="narrow">
        <Card padding="lg" variant="outlined" className="text-center bg-primary-50 border-primary-200">
          <div className="flex flex-col items-center gap-4 py-8">
            <Loader2 className="h-12 w-12 animate-spin text-primary-600" />
            <h2 className="text-h3 text-primary-800">{tl('quest.evaluating')}</h2>
            <p className="text-body-sm text-primary-600">{tl('quest.evaluating_desc')}</p>
          </div>
        </Card>
      </PageContainer>
    );
  }

  // FEEDBACK — Learning feedback panel (user clicks Continue to advance)
  if (pageState === 'feedback' && evaluationResult && currentStep) {
    return (
      <PageContainer width="narrow">
        {/* Step progress indicator */}
        <div className="mb-6 flex items-center gap-2 text-label text-text-secondary">
          <Map className="h-5 w-5 text-primary-600" />
          <span>{t('quest.step_of').replace('{current}', String(stepIndex - 1)).replace('{total}', String(quest?.steps.length || 0))}</span>
        </div>

        {/* Consequence message */}
        {consequenceMessage && (
          <div className="mb-5 p-4 rounded-xl bg-warning-50 border border-warning-200">
            <p className="text-body-sm text-warning-700">{t('quest.consequence_applied')}</p>
            <p className="text-caption text-warning-600 mt-1">{consequenceMessage}</p>
          </div>
        )}

        {/* Learning Feedback */}
        <LearningFeedbackPanel
          evaluationResult={evaluationResult}
          step={currentStep}
          onContinue={handleContinue}
        />
      </PageContainer>
    );
  }

  // TIMED_OUT
  if (pageState === 'timed_out') {
    return (
      <PageContainer width="narrow">
        <Card padding="lg" variant="default" className="text-center border-warning-200 bg-warning-50">
          <div className="flex flex-col items-center gap-4 py-6">
            <Clock className="h-12 w-12 text-warning-500" />
            <h2 className="text-h3 text-warning-800">{tl('quest.evaluation_timed_out')}</h2>
            <p className="text-body-sm text-warning-600 max-w-md">{tl('quest.evaluation_timed_out_desc')}</p>
            <div className="flex gap-3 mt-2">
              <Button onClick={handleRetry} isLoading={retryMutation.isPending}>
                <RotateCcw className="h-4 w-4" />
                {tl('quest.retry_evaluation')}
              </Button>
            </div>
          </div>
        </Card>
      </PageContainer>
    );
  }

  // FAILED
  if (pageState === 'failed') {
    return (
      <PageContainer width="narrow">
        <Card padding="lg" variant="default" className="text-center border-danger-200 bg-danger-50">
          <div className="flex flex-col items-center gap-4 py-6">
            <AlertCircle className="h-12 w-12 text-danger-400" />
            <h2 className="text-h3 text-danger-800">{tl('quest.evaluation_failed')}</h2>
            <p className="text-body-sm text-danger-600">{tl('quest.answer_saved')}</p>
            <div className="flex gap-3 mt-2">
              <Button onClick={handleRetry} isLoading={retryMutation.isPending}>
                <RotateCcw className="h-4 w-4" />
                {tl('quest.retry_evaluation')}
              </Button>
            </div>
          </div>
        </Card>
      </PageContainer>
    );
  }

  // OUTCOME
  if (pageState === 'outcome' && outcomeResult) {
    return (
      <PageContainer>
        <Card padding="lg" variant="elevated" className="text-center border-2 border-selected shadow-elevated">
          <div className="flex flex-col items-center gap-5 py-6">
            <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-primary-50 shadow-inner">
              <Star className="h-12 w-12 text-primary-600" />
            </div>

            <h1 className="text-display text-foreground leading-tight">
              {tl('quest.quest_complete')}
            </h1>
            <h2 className="text-h2 text-primary-700 max-w-2xl">
              {tl(outcomeResult.outcome_title_key) || ''}
            </h2>
            <p className="text-body-lg text-text-secondary max-w-2xl leading-relaxed">
              {tl(outcomeResult.outcome_summary_key) || ''}
            </p>
          </div>

          {/* Final narrative state */}
          <div className="my-8 p-5 rounded bg-muted border-2 border-default shadow-sm">
            <h3 className="text-label font-bold text-text-secondary mb-3">{tl('quest.narrative_state')}</h3>
            <StatusMeter state={outcomeResult.narrative_state} />
          </div>

          <div className="flex flex-wrap justify-center gap-4">
            <Button onClick={handleViewDebrief} size="lg" className="px-8 py-3 text-body shadow-md">
              <Lightbulb className="h-5 w-5" />
              {tl('quest.view_debrief')}
            </Button>
          </div>
        </Card>
      </PageContainer>
    );
  }

  // DEBRIEF — IMPROVED
  if (pageState === 'debrief' && outcomeResult) {
    const debrief = outcomeResult.debrief as Record<string, unknown> || {};
    const narrativeStateData = outcomeResult.narrative_state;

    return (
      <PageContainer>
        <h1 className="text-display text-foreground mb-8 text-center leading-tight">
          {tl('quest.debrief_title')}
        </h1>

        {/* Outcome summary */}
        <Card padding="lg" variant="elevated" className="mb-8 border-2 border-selected shadow-md">
          <h2 className="text-h2 text-primary-700 mb-3 leading-tight">
            {tl(outcomeResult.outcome_title_key) || ''}
          </h2>
          <p className="text-body-lg text-text-secondary leading-relaxed">
            {tl(outcomeResult.outcome_summary_key) || ''}
          </p>
        </Card>

        {/* Final Score */}
        <Card padding="md" variant="default" className="mb-8 bg-surface border-2 border-default shadow-sm">
          <div className="flex items-center gap-3">
            <BarChart3 className="h-8 w-8 text-primary-600" />
            <div>
              <h3 className="text-label font-bold text-text-secondary">{t('debrief_enhanced.final_score')}</h3>
              <p className="text-h2 text-primary-700">
                {(() => {
                  const scores = Object.values(stepResults).filter(r => typeof r.score === 'number');
                  if (scores.length === 0) return '—';
                  const avg = Math.round(scores.reduce((a: number, r: any) => a + r.score, 0) / scores.length);
                  return `${avg}%`;
                })()}
              </p>
            </div>
          </div>
        </Card>

        {/* Strengths */}
        {Array.isArray(debrief.strengths) && debrief.strengths.length > 0 && (
          <div className="mb-8">
            <h2 className="mb-4 flex items-center gap-2 text-h3 text-success-700">
              <TrendingUp className="h-6 w-6" />
              {tl('quest.strengths')}
            </h2>
            <ul className="space-y-3">
              {(debrief.strengths as string[]).map((s, i) => (
                <li key={i} className="flex items-start gap-3 rounded bg-success-50 p-4 border border-success-200 shadow-sm">
                  <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-success-600" />
                  <span className="text-body font-medium text-success-800 leading-snug">{tl(s) || s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Mistakes / improvement areas */}
        {Array.isArray(debrief.mistakes) && debrief.mistakes.length > 0 && (
          <div className="mb-8">
            <h2 className="mb-4 flex items-center gap-2 text-h3 text-warning-700">
              <Lightbulb className="h-6 w-6" />
              {tl('quest.mistakes')}
            </h2>
            <ul className="space-y-3">
              {(debrief.mistakes as string[]).map((m, i) => (
                <li key={i} className="flex items-start gap-3 rounded bg-warning-50 p-4 border border-warning-200 shadow-sm">
                  <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-warning-600" />
                  <span className="text-body font-medium text-warning-800 leading-snug">{tl(m) || m}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Missed risks */}
        {Array.isArray(debrief.missed_risks) && debrief.missed_risks.length > 0 && (
          <div className="mb-8">
            <h2 className="mb-4 flex items-center gap-2 text-h3 text-danger-700">
              <XCircle className="h-6 w-6" />
              {tl('quest.missed_risks')}
            </h2>
            <ul className="space-y-3">
              {(debrief.missed_risks as string[]).map((r, i) => (
                <li key={i} className="flex items-start gap-3 rounded bg-danger-50 p-4 border border-danger-200 shadow-sm">
                  <AlertCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-danger-600" />
                  <span className="text-body font-medium text-danger-800 leading-snug">{tl(r) || r}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Professional Sample — NEW */}
        {professionalSample && (
          <div className="mb-8">
            <h2 className="mb-4 flex items-center gap-2 text-h3 text-primary-700">
              <FileText className="h-6 w-6" />
              {t('debrief_enhanced.professional_sample')}
            </h2>
            <Card padding="lg" variant="elevated" className="border-2 border-primary-200 bg-primary-50/30">
              <p className="text-body-sm text-text-secondary mb-3 leading-relaxed">
                {t('debrief_enhanced.professional_sample_desc')}
              </p>
              <div className="space-y-2">
                {professionalSample.content.map((line, idx) => (
                  <p key={idx} className="text-body-sm text-foreground leading-relaxed font-mono bg-white/60 p-2 rounded border border-primary-100">
                    {line}
                  </p>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Skills trained */}
        <div className="mb-8">
          <h2 className="mb-4 flex items-center gap-2 text-h3 text-foreground">
            <Award className="h-6 w-6" />
            {t('debrief_enhanced.quest_skills')}
          </h2>
          <div className="flex flex-wrap gap-2">
            {questSkills.skills.map((skill, idx) => (
              <Badge key={idx} variant="primary" size="md">
                <CheckCircle className="h-3 w-3 mr-1" />
                {skill}
              </Badge>
            ))}
          </div>
        </div>

        {/* Skill profile from backend */}
        {Array.isArray(debrief.skill_results) && debrief.skill_results.length > 0 && (
          <div className="mb-8">
            <h2 className="mb-4 flex items-center gap-2 text-h3 text-foreground">
              <BarChart3 className="h-6 w-6" />
              {tl('quest.skill_profile')}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {(debrief.skill_results as Array<{ skill_id: string; level: string }>).map((sk, i) => (
                <div key={i} className="p-4 rounded bg-surface border-2 border-default shadow-sm">
                  <p className="text-body font-semibold text-foreground mb-2">{sk.skill_id}</p>
                  <span className={`inline-block text-label font-semibold px-3 py-1 rounded-full border ${
                    sk.level === 'practiced'
                      ? 'bg-success-50 text-success-700 border-success-200'
                      : 'bg-muted text-text-secondary border-default'
                  }`}>
                    {sk.level === 'practiced' ? tl('quest.skill_level_practiced') : tl('quest.skill_level_observed')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Final narrative state */}
        <Card padding="lg" variant="default" className="mb-8 bg-muted border-2 border-default shadow-sm">
          <h3 className="text-label font-bold text-text-secondary mb-4">{tl('quest.narrative_state')}</h3>
          <StatusMeter state={narrativeStateData} />
        </Card>

        {/* Action buttons — improved */}
        <div className="flex flex-wrap items-center justify-center gap-4">
          {Object.keys(stepResults).length > 0 && (
            <Button variant="secondary" onClick={handleViewMistakesReview} size="lg" className="px-6 py-3 text-body shadow-sm">
              <Eye className="h-5 w-5" />
              {t('debrief_enhanced.view_mistakes_review')}
            </Button>
          )}
          <Button variant="outline" onClick={handleReset} size="lg" className="px-6 py-3 text-body">
            <RotateCcw className="h-5 w-5" />
            {tl('quest.try_again')}
          </Button>
          <Button onClick={handleShowNextAction} size="lg" className="px-6 py-3 text-body shadow-md">
            <ArrowLeft className="h-5 w-5" />
            {t('debrief_enhanced.complete_debrief')}
          </Button>
        </div>
      </PageContainer>
    );
  }

  // MISTAKES REVIEW — NEW
  if (pageState === 'mistakes_review') {
    const stepIds = Object.keys(stepResults);
    const totalMistakeSteps = stepIds.length;
    const currentReviewStepId = stepIds[reviewStepIndex] || '';
    const currentReviewResult = stepResults[currentReviewStepId];

    const questStep = quest?.steps.find(s => s.step_id === currentReviewStepId);
    const score = currentReviewResult?.score ?? 0;
    const isStepCorrect = score === 100;
    const isStepPartial = score > 0 && score < 100;

    return (
      <PageContainer>
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-display text-foreground">
            {t('mistakes_review.title')}
          </h1>
          <Button variant="outline" onClick={() => setPageState('debrief')} size="md">
            <ArrowLeft className="h-4 w-4" />
            {t('mistakes_review.back_to_debrief')}
          </Button>
        </div>

        <p className="text-body text-text-secondary mb-8 leading-relaxed">
          {t('mistakes_review.subtitle')}
        </p>

        {totalMistakeSteps === 0 && (
          <Card padding="lg" variant="elevated" className="text-center border-success-200 bg-success-50">
            <div className="flex flex-col items-center gap-4 py-6">
              <CheckCircle className="h-16 w-16 text-success-600" />
              <h2 className="text-h2 text-success-800">{t('mistakes_review.no_mistakes')}</h2>
            </div>
          </Card>
        )}

        {totalMistakeSteps > 0 && currentReviewResult && questStep && (
          <div className="space-y-6">
            {/* Step navigation */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-label text-text-secondary">
                <Map className="h-4 w-4" />
                <span>{t('mistakes_review.of_total')
                  .replace('{current}', String(reviewStepIndex + 1))
                  .replace('{total}', String(totalMistakeSteps))}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`inline-block px-3 py-1 rounded-full text-label font-semibold border ${
                  isStepCorrect
                    ? 'bg-success-50 text-success-700 border-success-200'
                    : isStepPartial
                      ? 'bg-warning-50 text-warning-700 border-warning-200'
                      : 'bg-danger-50 text-danger-700 border-danger-200'
                }`}>
                  {t('mistakes_review.score').replace('{score}', String(score))}
                </span>
                <span className={`inline-block px-3 py-1 rounded-full text-label font-semibold border ${
                  isStepCorrect
                    ? 'bg-success-50 text-success-700 border-success-200'
                    : isStepPartial
                      ? 'bg-warning-50 text-warning-700 border-warning-200'
                      : 'bg-danger-50 text-danger-700 border-danger-200'
                }`}>
                  {isStepCorrect
                    ? t('mistakes_review.result_correct')
                    : isStepPartial
                      ? t('mistakes_review.result_partial')
                      : t('mistakes_review.result_incorrect')}
                </span>
              </div>
            </div>

            {/* Step content */}
            <Card padding="lg" variant="default" className="border-2 shadow-md">
              {/* Prompt */}
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-caption font-bold uppercase tracking-wider text-text-secondary">
                    {t('mistakes_review.step_label').replace('{number}', String(reviewStepIndex + 1))}
                  </span>
                  <Badge variant="primary" size="sm">
                    {tl(`quest.step_${questStep.step_type}`)}
                  </Badge>
                </div>
                {questStep.story_context_key && (
                  <div className="mb-3 p-3 rounded bg-muted border border-default">
                    <p className="text-body-sm text-text-secondary leading-relaxed">
                      {tl(questStep.story_context_key)}
                    </p>
                  </div>
                )}
                <h3 className="text-h3 text-foreground leading-tight">
                  {tl(questStep.prompt_key)}
                </h3>
              </div>

              {/* Their answer display */}
              {currentReviewResult.feedback_data && (
                <div className="mb-4 p-4 rounded bg-surface border border-default">
                  <h4 className="text-caption font-bold uppercase tracking-wider text-text-secondary mb-2">
                    {t('mistakes_review.your_answer')}
                  </h4>
                  <p className="text-body text-foreground leading-relaxed">
                    {typeof currentReviewResult.feedback_data === 'object'
                      ? JSON.stringify(currentReviewResult.feedback_data)
                      : String(currentReviewResult.feedback_data)}
                  </p>
                </div>
              )}

              {/* What was missed / why */}
              {!isStepCorrect && questStep.feedback?.incorrect_explanation_key && (
                <div className="mb-4 p-4 rounded bg-warning-50 border border-warning-200">
                  <h4 className="text-caption font-bold uppercase tracking-wider text-warning-700 mb-2">
                    {t('mistakes_review.explanation')}
                  </h4>
                  <p className="text-body text-warning-800 leading-relaxed">
                    {tl(questStep.feedback.incorrect_explanation_key)}
                  </p>
                </div>
              )}

              {/* Correct approach */}
              {!isStepCorrect && questStep.feedback?.correct_approach_key && (
                <div className="mb-4 p-4 rounded bg-success-50 border border-success-200">
                  <h4 className="text-caption font-bold uppercase tracking-wider text-success-700 mb-2">
                    {t('mistakes_review.correct_answer')}
                  </h4>
                  <p className="text-body text-success-800 leading-relaxed">
                    {tl(questStep.feedback.correct_approach_key)}
                  </p>
                </div>
              )}

              {/* Takeaway */}
              {questStep.feedback?.takeaway_key && (
                <div className="p-4 rounded bg-primary-50 border border-primary-200">
                  <h4 className="text-caption font-bold uppercase tracking-wider text-primary-700 mb-2">
                    {t('mistakes_review.takeaway')}
                  </h4>
                  <p className="text-body text-primary-800 leading-relaxed">
                    {tl(questStep.feedback.takeaway_key)}
                  </p>
                </div>
              )}
            </Card>

            {/* Navigation arrows */}
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                disabled={reviewStepIndex === 0}
                onClick={() => setReviewStepIndex(Math.max(0, reviewStepIndex - 1))}
              >
                Previous Step
              </Button>
              <Button
                variant="outline"
                disabled={reviewStepIndex >= totalMistakeSteps - 1}
                onClick={() => setReviewStepIndex(Math.min(totalMistakeSteps - 1, reviewStepIndex + 1))}
              >
                Next Step
              </Button>
            </div>
          </div>
        )}

        {totalMistakeSteps > 0 && !questStep && (
          <Card padding="lg" variant="default" className="text-center">
            <p className="text-body text-text-secondary">{tl('quest.session_not_found')}</p>
          </Card>
        )}
      </PageContainer>
    );
  }

  // NEXT ACTION — NEW
  if (pageState === 'next_action') {
    const allQuests = allQuestsData?.quests ? Object.values(allQuestsData.quests) as any[] : [];
    const normalizedSlug = (slug || '').replace(/-/g, '_');
    const availableQuests = allQuests.filter((q: any) =>
      q.trainer_slug === slug || q.trainer_slug === normalizedSlug
    );

    // Determine next recommended quest
    let nextQuest = null;
    if (isRecommendedQuest) {
      // Completed recommended — suggest second quest or payment_defect
      const secondId = isQA ? 'qa.payment_defect' : 'qa.bug_report';
      nextQuest = availableQuests.find((q: any) => q.quest_id === secondId) || null;
    } else {
      // Otherwise suggest the recommended one
      nextQuest = availableQuests.find((q: any) => q.quest_id === recommendedQuestId) || null;
    }

    return (
      <PageContainer width="narrow">
        <Card padding="lg" variant="elevated" className="text-center border-selected shadow-elevated mb-8">
          <div className="flex flex-col items-center gap-4 py-4">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary-50 shadow-inner">
              <TrendingUp className="h-10 w-10 text-primary-600" />
            </div>
            <h1 className="text-h1 text-foreground leading-tight">
              {t('next_action.title')}
            </h1>
          </div>
        </Card>

        <div className="space-y-4">
          {/* Repeat this quest */}
          <Card
            padding="lg"
            hover
            variant="default"
            className="border-2 hover:border-interactive cursor-pointer"
            onClick={handleReset}
          >
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
                <RotateCcw className="h-5 w-5 text-primary-600" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-h3 text-foreground mb-1">{t('next_action.repeat_weak_topic')}</h3>
                <p className="text-body-sm text-text-secondary leading-relaxed">
                  {t('next_action.repeat_weak_topic_desc')}
                </p>
              </div>
              <ChevronRight className="h-5 w-5 text-text-muted flex-shrink-0" />
            </div>
          </Card>

          {/* Start next quest */}
          {nextQuest && (
            <Card
              padding="lg"
              hover
              variant="default"
              className="border-2 border-selected hover:border-interactive cursor-pointer bg-gradient-to-br from-primary-50 to-purple-50"
              onClick={() => {
                const nextQid = nextQuest.quest_id;
                localStorage.removeItem(`quest_session_${questId}`);
                router.push(`/trainers/${slug}/quests/${nextQid}`);
              }}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center">
                  <Play className="h-5 w-5 text-purple-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-h3 text-foreground mb-1">{t('next_action.start_next_quest')}</h3>
                  <p className="text-body-sm font-medium text-primary-700 mb-1">
                    {nextQuest.title_key ? tl(nextQuest.title_key) : nextQuest.quest_id}
                  </p>
                  <p className="text-body-sm text-text-secondary leading-relaxed">
                    {t('next_action.start_next_quest_desc')}
                  </p>
                </div>
                <ChevronRight className="h-5 w-5 text-text-muted flex-shrink-0" />
              </div>
            </Card>
          )}

          {/* Return to catalog */}
          <Card
            padding="lg"
            hover
            variant="default"
            className="border-2 hover:border-interactive cursor-pointer"
            onClick={handleBackToCatalog}
          >
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                <BookOpen className="h-5 w-5 text-text-muted" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-h3 text-foreground mb-1">{t('next_action.return_to_catalog')}</h3>
                <p className="text-body-sm text-text-secondary leading-relaxed">
                  {t('next_action.return_to_catalog_desc')}
                </p>
              </div>
              <ChevronRight className="h-5 w-5 text-text-muted flex-shrink-0" />
            </div>
          </Card>

          {/* Continue trainer path */}
          <Card
            padding="lg"
            hover
            variant="default"
            className="border-2 hover:border-interactive cursor-pointer"
            onClick={handleBackToTrainer}
          >
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                <Zap className="h-5 w-5 text-text-muted" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-h3 text-foreground mb-1">
                  {t('next_action.continue_path').replace('{trainer}', isQA ? 'QA' : 'BA')}
                </h3>
                <p className="text-body-sm text-text-secondary leading-relaxed">
                  {t('next_action.continue_path_desc')}
                </p>
              </div>
              <ChevronRight className="h-5 w-5 text-text-muted flex-shrink-0" />
            </div>
          </Card>
        </div>
      </PageContainer>
    );
  }

  // Fallback
  return null;
}