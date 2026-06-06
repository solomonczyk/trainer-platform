'use client';

import React from 'react';

interface BlankDef {
  id: string;
  options?: string[];
}

interface FillBlanksActivityProps {
  template: string;
  blanks: BlankDef[];
  filledAnswers: Record<string, string>;
  onAnswer: (blankId: string, value: string) => void;
  disabled: boolean;
}

export function FillBlanksActivity({ template, blanks, filledAnswers, onAnswer, disabled }: FillBlanksActivityProps) {
  // Split template on ___ markers and render inline inputs
  const parts = template.split('___');

  const rendered: React.ReactNode[] = [];
  let blankIndex = 0;

  parts.forEach((part, i) => {
    rendered.push(<span key={`text-${i}`}>{part}</span>);
    if (blankIndex < blanks.length) {
      const blank = blanks[blankIndex];
      const value = filledAnswers[blank.id] || '';

      if (blank.options && blank.options.length > 0) {
        rendered.push(
          <select
            key={`blank-${blank.id}`}
            value={value}
            onChange={(e) => onAnswer(blank.id, e.target.value)}
            disabled={disabled}
            className="mx-1 px-3 py-1 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 focus:border-blue-500 focus:outline-none disabled:opacity-60"
          >
            <option value="">...</option>
            {blank.options.map((opt, oi) => (
              <option key={oi} value={opt}>{opt}</option>
            ))}
          </select>
        );
      } else {
        rendered.push(
          <input
            key={`blank-${blank.id}`}
            type="text"
            value={value}
            onChange={(e) => onAnswer(blank.id, e.target.value)}
            disabled={disabled}
            className="mx-1 px-3 py-1 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 focus:border-blue-500 focus:outline-none disabled:opacity-60 inline-block w-40"
            placeholder="..."
          />
        );
      }
      blankIndex++;
    }
  });

  return (
    <div className="text-lg leading-relaxed text-gray-800 dark:text-gray-200">
      {rendered}
    </div>
  );
}
