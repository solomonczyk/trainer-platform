'use client';

import React from 'react';
import { ti } from '@/lib/i18n';

interface QuizProgressBarProps {
  current: number;
  total: number;
}

export function QuizProgressBar({ current, total }: QuizProgressBarProps) {
  const pct = Math.round((current / total) * 100);

  return (
    <div className="space-y-2">
      {/* Label */}
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-gray-700 dark:text-gray-300">
          {ti('ba_trainer.quiz_progress', {
            current: String(current),
            total: String(total),
          })}
        </span>
        <span className="text-gray-500">{pct}%</span>
      </div>

      {/* Bar */}
      <div className="w-full h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-600 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
