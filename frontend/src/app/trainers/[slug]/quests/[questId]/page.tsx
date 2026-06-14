'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
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
} from '@/lib/api/client';
import type {
  QuestDefinition,
  QuestStepDefinition,
  QuestAnswerResponse,
  QuestOutcomeResponse,
} from '@/lib/api/client';
import { tl } from '@/lib/i18n';

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
} from 'lucide-react';
import Button from '@/components/ui/Button';
import Card, { CardTitle, CardContent } from '@/components/ui/Card';
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
  | 'error';

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
  const evaluationTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Try to resume session from localStorage
  const savedSessionId = typeof window !== 'undefined' ? localStorage.getItem(`quest_session_${questId}`) : null;

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

  // Clear evaluation timer on unmount
  useEffect(() => {
    return () => {
      if (evaluationTimerRef.current) clearTimeout(evaluationTimerRef.current);
    };
  }, []);

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
          // All steps done, go to outcome
          setPageState('feedback');
          evaluationTimerRef.current = setTimeout(async () => {
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
          }, 2000);
        } else if (data.next_step) {
          // Show evaluation briefly then advance
          setPageState('feedback');
          evaluationTimerRef.current = setTimeout(() => {
            setCurrentStep(data.next_step!);
            setStepAnswer(null);
            setStepUserText('');
            setEvaluationResult(null);
            setPageState('ready');
          }, 2000);
        }
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
      if (data.timed_out) {
        setPageState('timed_out');
      } else {
        setPageState('feedback');
        evaluationTimerRef.current = setTimeout(() => {
          if (data.next_step) {
            setCurrentStep(data.next_step);
            setStepAnswer(null);
            setStepUserText('');
            setEvaluationResult(null);
            setPageState('ready');
          } else {
            setPageState('outcome');
          }
        }, 2000);
      }
    },
    onError: () => {
      setPageState('failed');
    },
  });

  const handleSubmit = () => {
    // Validate answer
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

  const handleViewDebrief = () => {
    setPageState('debrief');
  };

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

  // INTRO
  if (pageState === 'intro' && quest && currentStep) {
    const totalSteps = quest.steps.length;
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

          {/* Narrative bars */}
          <div className="mb-8">
            <h3 className="text-label text-text-secondary mb-3">{tl('quest.narrative_state')}</h3>
            <StatusMeter state={narrativeState} />
          </div>

          <div className="flex justify-center">
            <Button size="lg" onClick={handleStart} className="w-full sm:w-auto px-8 py-3 text-body shadow-md">
              {tl('quest.start_quest')}
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

  // FEEDBACK (briefly shown before advancing)
  if (pageState === 'feedback' && evaluationResult) {
    return (
      <PageContainer width="narrow">
        <Card padding="lg" variant="default" className="text-center">
          <div className="flex flex-col items-center gap-4 py-6">
            {evaluationResult.correct ? (
              <CheckCircle className="h-12 w-12 text-success-600" />
            ) : evaluationResult.timed_out ? (
              <Clock className="h-12 w-12 text-warning-600" />
            ) : (
              <XCircle className="h-12 w-12 text-danger-400" />
            )}

            <h2 className="text-h3 text-foreground">
              {evaluationResult.feedback_key ? tl(evaluationResult.feedback_key) : ''}
            </h2>

            {evaluationResult.score !== undefined && (
              <div className="flex items-center gap-2 text-body-lg font-bold">
                <span className={evaluationResult.correct ? 'text-success-600' : 'text-danger-500'}>
                  {evaluationResult.score}/{evaluationResult.max_score || 100}
                </span>
              </div>
            )}

            {consequenceMessage && (
              <div className="p-3 rounded bg-warning-50 border border-warning-200">
                <p className="text-body-sm text-warning-700">{tl('quest.consequence_applied')}</p>
                <p className="text-caption text-warning-600 mt-1">{consequenceMessage}</p>
              </div>
            )}

            <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
            <p className="text-caption text-text-muted">Advancing...</p>
          </div>
        </Card>
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

          <div className="flex justify-center gap-4">
            <Button onClick={handleViewDebrief} size="lg" className="px-8 py-3 text-body shadow-md">
              <Lightbulb className="h-5 w-5" />
              {tl('quest.view_debrief')}
            </Button>
          </div>
        </Card>
      </PageContainer>
    );
  }

  // DEBRIEF
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

        {/* Skill profile */}
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

        {/* Action buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4">
          <Button variant="outline" onClick={handleReset} size="lg" className="px-6 py-3 text-body">
            <RotateCcw className="h-5 w-5" />
            {tl('quest.try_again')}
          </Button>
          <Button onClick={handleBackToTrainer} size="lg" className="px-6 py-3 text-body shadow-md">
            <ArrowLeft className="h-5 w-5" />
            {tl('quest.back_to_catalog')}
          </Button>
        </div>
      </PageContainer>
    );
  }

  // Fallback
  return null;
}
