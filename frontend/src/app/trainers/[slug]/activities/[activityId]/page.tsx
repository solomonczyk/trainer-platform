'use client';

import React, { useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getTrainer, startActivity, submitActivity, getTrainerProgress } from '@/lib/api/client';
import { ActivityRenderer } from '@/features/activities/ActivityRenderer';
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import Badge from "@/components/ui/Badge";
import { t } from "@/lib/i18n";

type PageState = 'loading' | 'prompt' | 'submitting' | 'result' | 'error';

export default function ActivityRunnerPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;
  const activityId = params.activityId as string;

  const [pageState, setPageState] = useState<PageState>('loading');
  const [answer, setAnswer] = useState<unknown>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');

  // Fetch trainer (for slug validation)
  const { data: trainer } = useQuery({
    queryKey: ['trainer', slug],
    queryFn: () => getTrainer(slug),
  });

  // Fetch activity prompt
  const {
    data: activityData,
    isLoading: isActivityLoading,
    error: activityError,
  } = useQuery({
    queryKey: ['activity-start', slug, activityId],
    queryFn: () => startActivity(slug, activityId),
    enabled: !!trainer,
  });

  // Submit mutation
  const submitMutation = useMutation({
    mutationFn: () =>
      submitActivity(slug, {
        activity_id: activityId,
        answer: answer,
        idempotency_key: `${activityId}-${Date.now()}`,
      }),
    onSuccess: (data) => {
      setResult(data as unknown as Record<string, unknown>);
      setPageState('result');
    },
    onError: (error: Error) => {
      if (error.message?.toLowerCase().includes('not enrolled')) {
        setErrorMessage(t('common.notEnrolled.title'));
      } else {
        setErrorMessage(error.message || t('ba_trainer.error_submitting'));
      }
      setPageState('error');
    },
  });

  // Handle state transitions
  React.useEffect(() => {
    if (!isActivityLoading && activityData) {
      setPageState('prompt');
      // Initialize answer based on activity type
      if (activityData.activity_type === 'single_choice') {
        setAnswer(null);
      } else if (activityData.activity_type === 'multiple_choice') {
        setAnswer([]);
      } else if (activityData.activity_type === 'numeric') {
        setAnswer('');
      } else if (activityData.activity_type === 'fill_blanks') {
        setAnswer({});
      } else if (activityData.activity_type === 'matching') {
        setAnswer({});
      }
    }
    if (activityError) {
      const errMsg = activityError instanceof Error ? activityError.message : '';
      if (errMsg.toLowerCase().includes('not enrolled')) {
        setErrorMessage(t('common.notEnrolled.title'));
      } else {
        setErrorMessage(t('ba_trainer.error_loading'));
      }
      setPageState('error');
    }
  }, [isActivityLoading, activityData, activityError]);

  const handleSubmit = useCallback(() => {
    if (answer === null || answer === '' || (Array.isArray(answer) && answer.length === 0)) {
      setErrorMessage(t('ba_trainer.select_answer'));
      return;
    }
    setPageState('submitting');
    setErrorMessage('');
    submitMutation.mutate();
  }, [answer, submitMutation]);

  const handleNext = useCallback(() => {
    setAnswer(null);
    setResult(null);
    setPageState('loading');
    setErrorMessage('');
    router.refresh();
    // Navigate back to module
    if (activityData) {
      router.push(`/trainers/${slug}/modules/${activityData.module_id}`);
    } else {
      router.push(`/trainers/${slug}`);
    }
  }, [activityData, router, slug]);

  // Loading state
  if (pageState === 'loading' || isActivityLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner className="mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">{t('ba_trainer.loading')}</p>
        </div>
      </div>
    );
  }

  // Error state
  if (pageState === 'error') {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-red-500 text-4xl mb-4">!</div>
              <p className="text-red-600 dark:text-red-400 mb-4">{errorMessage}</p>
              <Button variant="outline" onClick={() => router.back()}>
                {t('common.back')}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Result state
  if (pageState === 'result' && result) {
    const status = result.status as string;
    const score = result.score as number;
    const passed = result.passed as boolean;
    const explanationKey = result.explanation_key as string;

    const statusColor = status === 'correct' ? 'green' : status === 'partial' ? 'yellow' : 'red';
    const statusText = status === 'correct' ? t('ba_trainer.result_correct') :
      status === 'partial' ? t('ba_trainer.result_partial') : t('ba_trainer.result_incorrect');

    return (
      <div className="min-h-[60vh] max-w-2xl mx-auto py-8 px-4">
        <Card>
          <CardHeader>
            <CardTitle>
              <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                status === 'correct' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                status === 'partial' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' :
                'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
              }`}>
                {statusText}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center">
              <div className="text-4xl font-bold mb-2">{score}%</div>
              <p className="text-gray-500 dark:text-gray-400">
                {passed ? t('ba_trainer.result_correct') : t('ba_trainer.result_incorrect')}
              </p>
            </div>

            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h3 className="font-medium text-blue-800 dark:text-blue-300 mb-2">
                {t('ba_trainer.explanation_label')}
              </h3>
              <p className="text-blue-700 dark:text-blue-400">
                {t(explanationKey)}
              </p>
            </div>

            <div className="flex justify-between">
              <Button variant="outline" onClick={handleNext}>
                {t('ba_trainer.next')}
              </Button>
              <Button onClick={handleNext}>
                {t('ba_trainer.next')}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Prompt state — show activity
  if (!activityData) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <p className="text-gray-500">{t('ba_trainer.error_loading')}</p>
      </div>
    );
  }

  const difficultyVariant = activityData.difficulty === 'junior' ? 'success' :
    activityData.difficulty === 'middle' ? 'warning' : 'danger';
  const difficultyLabel = activityData.difficulty === 'junior' ? t('ba_trainer.difficulty_junior') :
    activityData.difficulty === 'middle' ? t('ba_trainer.difficulty_middle') : t('ba_trainer.difficulty_senior');

  return (
    <div className="min-h-[60vh] max-w-2xl mx-auto py-8 px-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between mb-2">
            <Badge variant={difficultyVariant as any}>{difficultyLabel}</Badge>
            <Badge>{activityData.activity_type.replace('_', ' ')}</Badge>
          </div>
          <CardTitle>{t(activityData.title_key)}</CardTitle>
          {activityData.description_key && (
            <p className="text-gray-500 dark:text-gray-400 mt-2">
              {t(activityData.description_key)}
            </p>
          )}
        </CardHeader>
        <CardContent className="space-y-6">
          <ActivityRenderer
            activityType={activityData.activity_type as any}
            prompt={activityData.prompt}
            answer={answer}
            onAnswer={setAnswer}
            disabled={pageState === 'submitting'}
          />

          {errorMessage && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
              {errorMessage}
            </div>
          )}

          <div className="flex justify-between pt-4">
            <Button
              variant="outline"
              onClick={() => router.push(`/trainers/${slug}/modules/${activityData.module_id}`)}
            >
              {t('ba_trainer.back_to_modules')}
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={pageState === 'submitting'}
              isLoading={pageState === 'submitting'}
            >
              {t('ba_trainer.submit')}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
