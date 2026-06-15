'use client';

import { CheckCircle, XCircle, AlertCircle, Lightbulb, Target, ArrowRight } from 'lucide-react';
import { tl, t } from '@/lib/i18n';
import type { QuestAnswerResponse, QuestStepDefinition } from '@/lib/api/client';
import Button from '@/components/ui/Button';

interface LearningFeedbackPanelProps {
  evaluationResult: QuestAnswerResponse;
  step: QuestStepDefinition;
  onContinue: () => void;
}

type FeedbackResultType = 'correct' | 'partial' | 'incorrect';

export default function LearningFeedbackPanel({
  evaluationResult,
  step,
  onContinue,
}: LearningFeedbackPanelProps) {
  const { correct, score, max_score, feedback_data } = evaluationResult;
  const feedback = step.feedback;
  const isDeterministic = step.evaluation_mode === 'deterministic';

  // Score-based result classification (requirement: score===100 correct, >0 partial, 0 incorrect)
  const resultType: FeedbackResultType =
    score === 100
      ? 'correct'
      : score !== undefined && score > 0 && score < 100
        ? 'partial'
        : 'incorrect';

  const isCorrect = resultType === 'correct';
  const isPartial = resultType === 'partial';

  // Select feedback keys based on result type
  const whyKey = isCorrect
    ? feedback?.reinforcement_key
    : isPartial
      ? (feedback?.partial_missing_key || feedback?.incorrect_explanation_key)
      : feedback?.incorrect_explanation_key;

  const approachKey = isCorrect ? undefined : feedback?.correct_approach_key;
  const takeawayKey = feedback?.takeaway_key;

  // Title i18n key
  const titleKey = isCorrect
    ? 'quest.correct'
    : isPartial
      ? 'quest.result_partial'
      : 'quest.incorrect';

  // For AI-evaluated steps, use feedback_data if no step feedback exists
  const hasAiFeedback = !isDeterministic && feedback_data && !feedback;

  // AI feedback data for non-deterministic steps
  const aiStrengths: string[] = hasAiFeedback
    ? (feedback_data as Record<string, unknown>)?.strengths as string[] ?? []
    : [];
  const aiWeakPoints: string[] = hasAiFeedback
    ? (feedback_data as Record<string, unknown>)?.weak_points as string[] ?? []
    : [];

  // Icons and colors
  const IconComponent = isCorrect ? CheckCircle : isPartial ? AlertCircle : XCircle;
  const iconColor = isCorrect ? 'text-success-600' : isPartial ? 'text-warning-600' : 'text-danger-500';
  const bgColor = isCorrect
    ? 'bg-success-50 border-success-200'
    : isPartial
      ? 'bg-warning-50 border-warning-200'
      : 'bg-danger-50 border-danger-200';
  const scoreColor = isCorrect ? 'text-success-600' : isPartial ? 'text-warning-600' : 'text-danger-500';

  return (
    <div className="w-full max-w-2xl mx-auto space-y-5">
      {/* Result Header */}
      <div className={`rounded-xl border-2 p-6 ${bgColor}`}>
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 mt-0.5">
            <IconComponent className={`h-8 w-8 ${iconColor}`} />
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-xl font-bold text-foreground mb-1">
              {tl(titleKey)}
            </h2>
            {score !== undefined && score !== null && (
              <p className={`text-lg font-semibold ${scoreColor}`}>
                {score}/{max_score || 100}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Why section — explanation or reinforcement */}
      {whyKey && (
        <div className="rounded-xl border border-default bg-surface p-5 shadow-sm">
          <div className="flex items-start gap-3">
            <Lightbulb className="h-5 w-5 flex-shrink-0 mt-0.5 text-primary-600" />
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-text-secondary mb-2">
                {t('quest.feedback_why')}
              </h3>
              <p className="text-body text-foreground leading-relaxed">
                {tl(whyKey)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Correct approach — shown when answer is wrong or partial */}
      {approachKey && (
        <div className="rounded-xl border border-default bg-surface p-5 shadow-sm">
          <div className="flex items-start gap-3">
            <Target className="h-5 w-5 flex-shrink-0 mt-0.5 text-primary-600" />
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-text-secondary mb-2">
                {t('quest.feedback_correct_approach')}
              </h3>
              <p className="text-body text-foreground leading-relaxed">
                {tl(approachKey)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* AI feedback data (for free_text / dialogue steps) */}
      {aiStrengths.length > 0 && (
        <div className="rounded-xl border border-default bg-surface p-5 shadow-sm">
          <h3 className="text-sm font-bold uppercase tracking-wider text-success-700 mb-3">
            {t('result.strengths')}
          </h3>
          <ul className="space-y-2">
            {aiStrengths.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-body text-foreground">
                <CheckCircle className="h-4 w-4 flex-shrink-0 mt-0.5 text-success-600" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {aiWeakPoints.length > 0 && (
        <div className="rounded-xl border border-default bg-surface p-5 shadow-sm">
          <h3 className="text-sm font-bold uppercase tracking-wider text-warning-700 mb-3">
            {t('result.weakPoints')}
          </h3>
          <ul className="space-y-2">
            {aiWeakPoints.map((w, i) => (
              <li key={i} className="flex items-start gap-2 text-body text-foreground">
                <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5 text-warning-600" />
                <span>{w}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Takeaway — shown when available */}
      {takeawayKey && (
        <div className="rounded-xl border border-primary-200 bg-primary-50 p-5">
          <div className="flex items-start gap-3">
            <Target className="h-5 w-5 flex-shrink-0 mt-0.5 text-primary-700" />
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-primary-700 mb-2">
                {t('quest.feedback_takeaway')}
              </h3>
              <p className="text-body text-primary-800 leading-relaxed">
                {tl(takeawayKey)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Continue button */}
      <div className="flex justify-end pt-2">
        <Button
          onClick={onContinue}
          size="lg"
          className="px-8 py-3 text-body shadow-md"
        >
          {t('quest.feedback_continue')}
          <ArrowRight className="h-5 w-5 ml-2" />
        </Button>
      </div>
    </div>
  );
}
