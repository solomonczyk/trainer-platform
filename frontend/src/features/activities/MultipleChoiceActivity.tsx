'use client';

import React from 'react';
import { t } from '@/lib/i18n';

interface MultipleChoiceActivityProps {
  options: string[];
  selectedAnswers: string[];
  onAnswer: (answers: string[]) => void;
  disabled: boolean;
  /** Activity ID for localized option lookup (e.g. "ba_hr_q1_multi") */
  activityId?: string;
}

export function MultipleChoiceActivity({ options, selectedAnswers, onAnswer, disabled, activityId }: MultipleChoiceActivityProps) {
  const getOptionLabel = (option: string, index: number): string => {
    if (!activityId) return option;
    const baseId = activityId.replace(/_single$|_multi$/, '');
    const key = `${baseId}_opt_${index + 1}`;
    const localized = t(key);
    return localized !== key ? localized : option;
  };

  const toggleOption = (option: string) => {
    if (disabled) return;
    const newSelected = selectedAnswers.includes(option)
      ? selectedAnswers.filter(a => a !== option)
      : [...selectedAnswers, option];
    onAnswer(newSelected);
  };

  return (
    <div className="space-y-3">
      {options.map((option, index) => {
        const isSelected = selectedAnswers.includes(option);
        return (
          <button
            key={index}
            onClick={() => toggleOption(option)}
            disabled={disabled}
            className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
              isSelected
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600'
            } ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <div className="flex items-center gap-3">
              <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                isSelected
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-400 dark:border-gray-500'
              }`}>
                {isSelected && (
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </div>
              <span className="text-gray-800 dark:text-gray-200">{getOptionLabel(option, index)}</span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
