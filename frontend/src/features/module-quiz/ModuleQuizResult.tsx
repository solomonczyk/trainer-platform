'use client';

import React, { useMemo, useState } from 'react';
import { t, ti } from '@/lib/i18n';
import type { QuizResultItem } from './ModuleQuizEngine';
import Button from '@/components/ui/Button';
import Card, { CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';

/* ------------------------------------------------------------------ */
/*  Props                                                             */
/* ------------------------------------------------------------------ */

interface ModuleQuizResultProps {
  results: QuizResultItem[];
  moduleTitle: string;
  onRepeat: () => void;
  onBack: () => void;
  onBank: () => void;
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                           */
/* ------------------------------------------------------------------ */

function difficultyLabelText(d: string) {
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
}

function formatAnswer(answer: unknown, type: string): string {
  if (answer === null || answer === undefined) return '—';
  if (typeof answer === 'string') return answer || '—';
  if (Array.isArray(answer)) {
    return answer.length > 0 ? answer.join(', ') : '—';
  }
  if (typeof answer === 'object') {
    try {
      return JSON.stringify(answer);
    } catch {
      return '—';
    }
  }
  return String(answer);
}

/* ------------------------------------------------------------------ */
/*  Component                                                         */
/* ------------------------------------------------------------------ */

export default function ModuleQuizResult({
  results,
  moduleTitle,
  onRepeat,
  onBack,
  onBank,
}: ModuleQuizResultProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  // ── Aggregate stats ───────────────────────────────────────────────
  const stats = useMemo(() => {
    const correct = results.filter((r) => r.result.status === 'correct').length;
    const partial = results.filter((r) => r.result.status === 'partial').length;
    const incorrect = results.filter((r) => r.result.status === 'incorrect').length;
    const totalScore =
      results.length > 0
        ? Math.round(
            results.reduce((sum, r) => sum + r.result.score, 0) / results.length,
          )
        : 0;

    // Per-difficulty breakdown
    const byDifficulty: Record<string, { correct: number; total: number }> = {};
    for (const item of results) {
      const d = item.activity.difficulty || 'unknown';
      if (!byDifficulty[d]) byDifficulty[d] = { correct: 0, total: 0 };
      byDifficulty[d].total++;
      if (item.result.status === 'correct') byDifficulty[d].correct++;
    }

    // Weak topics (difficulty levels with < 60% accuracy)
    const weakTopics: string[] = [];
    for (const [diff, st] of Object.entries(byDifficulty)) {
      const acc = st.total > 0 ? Math.round((st.correct / st.total) * 100) : 0;
      if (acc < 60) weakTopics.push(difficultyLabelText(diff));
    }

    return {
      correct,
      partial,
      incorrect,
      total: results.length,
      totalScore,
      byDifficulty,
      weakTopics,
    };
  }, [results]);

  // ── Empty state ───────────────────────────────────────────────────
  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">{t('ba_trainer.no_activities')}</p>
        <div className="flex gap-3 justify-center mt-6">
          <Button onClick={onRepeat}>{t('ba_trainer.repeat_module')}</Button>
          <Button variant="outline" onClick={onBack}>
            {t('ba_trainer.back_to_modules')}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* ── Header ────────────────────────────────────────────────── */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          {t('ba_trainer.module_completed')}
        </h2>
        <p className="text-gray-500 dark:text-gray-400">{moduleTitle}</p>
      </div>

      {/* ── Score card ────────────────────────────────────────────── */}
      <Card>
        <CardContent className="pt-6 space-y-6">
          {/* Big score */}
          <div className="text-center">
            <div
              className={`text-5xl font-bold mb-1 ${
                stats.totalScore >= 80
                  ? 'text-green-600'
                  : stats.totalScore >= 50
                    ? 'text-yellow-600'
                    : 'text-red-600'
              }`}
            >
              {stats.totalScore}%
            </div>
            <p className="text-sm text-gray-500">
              {t('ba_trainer.total_score')}
            </p>
          </div>

          {/* Counts row */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
              <div className="text-2xl font-bold text-green-700 dark:text-green-400">
                {stats.correct}
              </div>
              <div className="text-xs text-green-600 dark:text-green-500 mt-1">
                {t('ba_trainer.questions_correct')}
              </div>
            </div>
            <div className="p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
              <div className="text-2xl font-bold text-yellow-700 dark:text-yellow-400">
                {stats.partial}
              </div>
              <div className="text-xs text-yellow-600 dark:text-yellow-500 mt-1">
                {t('ba_trainer.questions_partial')}
              </div>
            </div>
            <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20">
              <div className="text-2xl font-bold text-red-700 dark:text-red-400">
                {stats.incorrect}
              </div>
              <div className="text-xs text-red-600 dark:text-red-500 mt-1">
                {t('ba_trainer.questions_incorrect')}
              </div>
            </div>
          </div>

          {/* Difficulty breakdown */}
          {Object.keys(stats.byDifficulty).length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                {t('ba_trainer.difficulty_breakdown')}
              </h3>
              <div className="space-y-2">
                {Object.entries(stats.byDifficulty).map(([diff, st]) => {
                  const acc =
                    st.total > 0
                      ? Math.round((st.correct / st.total) * 100)
                      : 0;
                  return (
                    <div
                      key={diff}
                      className="flex items-center gap-3 text-sm"
                    >
                      <span className="w-20 text-gray-600 dark:text-gray-400">
                        {difficultyLabelText(diff)}
                      </span>
                      <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            acc >= 80
                              ? 'bg-green-500'
                              : acc >= 50
                                ? 'bg-yellow-500'
                                : 'bg-red-500'
                          }`}
                          style={{ width: `${acc}%` }}
                        />
                      </div>
                      <span className="w-12 text-right text-gray-600 dark:text-gray-400 font-mono text-xs">
                        {acc}%
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Weak topics */}
          {stats.weakTopics.length > 0 && (
            <div className="p-4 rounded-lg bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800">
              <h3 className="font-semibold text-orange-800 dark:text-orange-300 mb-2">
                {t('ba_trainer.weak_topics')}
              </h3>
              <ul className="list-disc list-inside text-sm text-orange-700 dark:text-orange-400 space-y-1">
                {stats.weakTopics.map((topic) => (
                  <li key={topic}>
                    {ti('ba_trainer.weak_topic_item', { topic })}
                  </li>
                ))}
              </ul>
              <p className="text-sm text-orange-700 dark:text-orange-400 mt-2">
                {t('ba_trainer.recommendation')}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ── Per-question review ───────────────────────────────────── */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('ba_trainer.review_title')}
        </h3>
        <div className="space-y-3">
          {results.map((item, idx) => {
            const { status, score, explanation_key: explanationKey } =
              item.result;
            const isExpanded = expandedIndex === idx;
            const statusColor =
              status === 'correct'
                ? 'green'
                : status === 'partial'
                  ? 'yellow'
                  : 'red';
            const statusLabel =
              status === 'correct'
                ? t('ba_trainer.result_correct')
                : status === 'partial'
                  ? t('ba_trainer.result_partial')
                  : t('ba_trainer.result_incorrect');

            return (
              <Card key={idx} padding="md" variant="default">
                <button
                  type="button"
                  onClick={() =>
                    setExpandedIndex(isExpanded ? null : idx)
                  }
                  className="w-full text-left focus:outline-none"
                >
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-sm font-semibold text-gray-600 dark:text-gray-400">
                        {idx + 1}
                      </span>
                      <span
                        className={`inline-block w-2 h-2 rounded-full flex-shrink-0 ${
                          status === 'correct'
                            ? 'bg-green-500'
                            : status === 'partial'
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                        }`}
                      />
                      <span className="font-medium text-gray-900 dark:text-gray-100 truncate">
                        {t(item.startData.title_key)}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <Badge
                        variant={
                          statusColor as 'success' | 'warning' | 'danger'
                        }
                        size="sm"
                      >
                        {statusLabel}
                      </Badge>
                      <span className="text-sm font-mono text-gray-500">
                        {score}%
                      </span>
                      <svg
                        className={`w-4 h-4 text-gray-400 transition-transform ${
                          isExpanded ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </div>
                  </div>
                </button>

                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
                    {/* User's answer */}
                    <div>
                      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        {t('ba_trainer.your_answer')}
                      </span>
                      <p className="text-sm text-gray-800 dark:text-gray-200 mt-1">
                        {formatAnswer(
                          item.answer,
                          item.startData.activity_type,
                        )}
                      </p>
                    </div>

                    {/* Explanation */}
                    <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <span className="text-xs font-semibold text-blue-600 uppercase tracking-wider">
                        {t('ba_trainer.explanation_label')}
                      </span>
                      <p className="text-sm text-blue-700 dark:text-blue-400 mt-1">
                        {t(explanationKey as string)}
                      </p>
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </div>

      {/* ── Actions ───────────────────────────────────────────────── */}
      <div className="flex flex-wrap gap-3 justify-center pt-4 pb-8">
        <Button onClick={onRepeat}>{t('ba_trainer.repeat_module')}</Button>
        <Button variant="outline" onClick={onBank}>
          {t('ba_trainer.bank_mode')}
        </Button>
        <Button variant="ghost" onClick={onBack}>
          {t('ba_trainer.back_to_modules')}
        </Button>
      </div>
    </div>
  );
}
