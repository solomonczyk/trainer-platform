'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import type {
  ActivityResponse,
  ActivityStartResponse,
  ActivitySubmitResponse,
} from '@/lib/api/client';
import { startActivity, submitActivity } from '@/lib/api/client';
import { t } from '@/lib/i18n';
import { ActivityRenderer } from '@/features/activities/ActivityRenderer';
import { QuizProgressBar } from './QuizProgressBar';
import Button from '@/components/ui/Button';
import Card, { CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

/* ------------------------------------------------------------------ */
/*  Types                                                             */
/* ------------------------------------------------------------------ */

export type QuizPhase = 'loading' | 'answering' | 'submitting' | 'feedback';

export interface QuizResultItem {
  activity: ActivityResponse;
  startData: ActivityStartResponse;
  answer: unknown;
  result: ActivitySubmitResponse;
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                           */
/* ------------------------------------------------------------------ */

function initializeAnswer(type: string): unknown {
  switch (type) {
    case 'single_choice':
      return null;
    case 'multiple_choice':
      return [];
    case 'numeric':
      return '';
    case 'fill_blanks':
      return {};
    case 'matching':
      return {};
    default:
      return null;
  }
}

const difficultyVariant = (
  d: string,
): 'success' | 'warning' | 'danger' | 'default' => {
  switch (d) {
    case 'junior':
      return 'success';
    case 'middle':
      return 'warning';
    case 'senior':
      return 'danger';
    default:
      return 'default';
  }
};

const difficultyLabelText = (d: string) => {
  switch (d) {
    case 'junior':
      return t('ba_trainer.difficulty_junior');
    case 'middle':
      return t('ba_trainer.difficulty_middle');
    case 'senior':
      return t('ba_trainer.difficulty_senior');
    default:
      return d;
  }
};

/* ------------------------------------------------------------------ */
/*  Props                                                             */
/* ------------------------------------------------------------------ */

interface ModuleQuizEngineProps {
  slug: string;
  moduleId: string;
  activities: ActivityResponse[];
  onFinish: (results: QuizResultItem[]) => void;
  onExit: () => void;
}

/* ------------------------------------------------------------------ */
/*  Component                                                         */
/* ------------------------------------------------------------------ */

export default function ModuleQuizEngine({
  slug,
  moduleId,
  activities,
  onFinish,
  onExit,
}: ModuleQuizEngineProps) {
  const total = activities.length;

  // ── State ──────────────────────────────────────────────────────────
  const [currentIndex, setCurrentIndex] = useState(0);
  const [phase, setPhase] = useState<QuizPhase>('loading');
  const [currentStartData, setCurrentStartData] =
    useState<ActivityStartResponse | null>(null);
  const [answer, setAnswer] = useState<unknown>(null);
  const [currentResult, setCurrentResult] =
    useState<ActivitySubmitResponse | null>(null);
  const [results, setResults] = useState<QuizResultItem[]>([]);
  const [errorMessage, setErrorMessage] = useState('');

  // ── Load current question start data ──────────────────────────────
  const loadQuestion = useCallback(
    async (index: number) => {
      setPhase('loading');
      setCurrentResult(null);
      setErrorMessage('');
      try {
        const data = await startActivity(
          slug,
          activities[index].activity_id,
        );
        setCurrentStartData(data);
        setAnswer(initializeAnswer(data.activity_type));
        setPhase('answering');
      } catch {
        setErrorMessage(t('ba_trainer.error_loading'));
        setPhase('feedback'); // treat as terminal for this Q
      }
    },
    [slug, activities],
  );

  // Load first question on mount
  useEffect(() => {
    if (activities.length > 0) {
      loadQuestion(0);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Submit mutation ───────────────────────────────────────────────
  const submitMutation = useMutation({
    mutationFn: () =>
      submitActivity(slug, {
        activity_id: activities[currentIndex].activity_id,
        answer,
        idempotency_key: `${activities[currentIndex].activity_id}-${Date.now()}`,
      }),
    onSuccess: (data) => {
      setCurrentResult(data);
      setPhase('feedback');
    },
    onError: (err: Error) => {
      setErrorMessage(err.message || t('ba_trainer.error_submitting'));
      setPhase('feedback');
    },
  });

  // ── Handlers ──────────────────────────────────────────────────────
  const handleSubmit = useCallback(() => {
    if (answer === null || answer === '' ||
        (Array.isArray(answer) && answer.length === 0)) {
      setErrorMessage(t('ba_trainer.select_answer'));
      return;
    }
    setPhase('submitting');
    setErrorMessage('');
    submitMutation.mutate();
  }, [answer, submitMutation]);

  const handleNext = useCallback(() => {
    // Save current result
    if (currentStartData && currentResult) {
      const item: QuizResultItem = {
        activity: activities[currentIndex],
        startData: currentStartData,
        answer,
        result: currentResult,
      };
      const updated = [...results, item];
      setResults(updated);

      const nextIndex = currentIndex + 1;
      if (nextIndex >= total) {
        // Module complete — emit final results
        onFinish(updated);
        return;
      }
      setCurrentIndex(nextIndex);
      loadQuestion(nextIndex);
    }
  }, [
    currentStartData,
    currentResult,
    activities,
    currentIndex,
    answer,
    results,
    total,
    onFinish,
    loadQuestion,
  ]);

  // ── Loading phase ─────────────────────────────────────────────────
  if (phase === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <div className="text-center">
          <LoadingSpinner className="mx-auto mb-4" />
          <p className="text-gray-500">{t('ba_trainer.loading')}</p>
        </div>
      </div>
    );
  }

  // ── Error (terminal for this question) ────────────────────────────
  if (errorMessage && !currentStartData) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 text-4xl mb-4">!</div>
        <p className="text-red-600 mb-4">{errorMessage}</p>
        <Button variant="outline" onClick={onExit}>
          {t('ba_trainer.back_to_modules')}
        </Button>
      </div>
    );
  }

  if (!currentStartData) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">{t('ba_trainer.error_loading')}</p>
      </div>
    );
  }

  // ── Feedback phase (result shown after submit) ────────────────────
  if (phase === 'feedback' && currentResult) {
    const { status, score } = currentResult;
    const explanationKey = currentResult.explanation_key as string;
    const statusBg =
      status === 'correct'
        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
        : status === 'partial'
          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
          : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';

    const statusLabel =
      status === 'correct'
        ? t('ba_trainer.result_correct')
        : status === 'partial'
          ? t('ba_trainer.result_partial')
          : t('ba_trainer.result_incorrect');

    const isLast = currentIndex >= total - 1;

    return (
      <div className="space-y-6">
        {/* Progress */}
        <QuizProgressBar current={currentIndex + 1} total={total} />

        {/* Result card */}
        <Card>
          <CardContent className="pt-6 space-y-5">
            {/* Status badge + score */}
            <div className="flex items-center justify-between">
              <span
                className={`inline-block px-4 py-1.5 rounded-full text-sm font-semibold ${statusBg}`}
              >
                {statusLabel}
              </span>
              <span className="text-2xl font-bold">{score}%</span>
            </div>

            {/* Explanation */}
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h3 className="font-medium text-blue-800 dark:text-blue-300 mb-1">
                {t('ba_trainer.explanation_label')}
              </h3>
              <p className="text-blue-700 dark:text-blue-400 text-sm">
                {t(explanationKey)}
              </p>
            </div>

            {/* Next / Finish buttons */}
            <div className="flex justify-between pt-2">
              <Button variant="outline" onClick={onExit}>
                {t('ba_trainer.back_to_modules')}
              </Button>

              {isLast ? (
                <Button onClick={handleNext}>
                  {t('ba_trainer.finish_module')}
                </Button>
              ) : (
                <Button onClick={handleNext}>
                  {t('ba_trainer.next')}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // ── Answering phase ───────────────────────────────────────────────
  const questionNumber = currentIndex + 1;
  const aty = currentStartData.activity_type;

  return (
    <div className="space-y-6">
      {/* Progress */}
      <QuizProgressBar current={questionNumber} total={total} />

      {/* Question header */}
      <div className="flex items-center gap-2">
        <Badge variant={difficultyVariant(currentStartData.difficulty)}>
          {difficultyLabelText(currentStartData.difficulty)}
        </Badge>
        <Badge variant="default">
          {t(`ba_trainer.activity_type_${aty}`) !==
          `ba_trainer.activity_type_${aty}`
            ? t(`ba_trainer.activity_type_${aty}`)
            : aty.replace(/_/g, ' ')}
        </Badge>
      </div>

      {/* Question card */}
      <Card>
        <CardHeader>
          <CardTitle>
            {t(currentStartData.title_key)}
          </CardTitle>
          {currentStartData.description_key && (
            <p className="text-gray-500 dark:text-gray-400 mt-2">
              {t(currentStartData.description_key)}
            </p>
          )}
        </CardHeader>
        <CardContent className="space-y-6">
          <ActivityRenderer
            activityType={aty as any}
            prompt={currentStartData.prompt}
            answer={answer}
            onAnswer={setAnswer}
            disabled={phase === 'submitting'}
          />

          {errorMessage && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
              {errorMessage}
            </div>
          )}

          <div className="flex justify-between pt-4">
            <Button variant="outline" onClick={onExit}>
              {t('ba_trainer.back_to_modules')}
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={phase === 'submitting'}
              isLoading={phase === 'submitting'}
            >
              {t('ba_trainer.submit')}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
