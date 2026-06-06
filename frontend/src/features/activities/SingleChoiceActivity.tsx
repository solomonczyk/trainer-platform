'use client';

import React from 'react';

interface SingleChoiceActivityProps {
  options: string[];
  selectedAnswer: string | null;
  onAnswer: (answer: string) => void;
  disabled: boolean;
}

export function SingleChoiceActivity({ options, selectedAnswer, onAnswer, disabled }: SingleChoiceActivityProps) {
  return (
    <div className="space-y-3">
      {options.map((option, index) => (
        <button
          key={index}
          onClick={() => !disabled && onAnswer(option)}
          disabled={disabled}
          className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
            selectedAnswer === option
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600'
          } ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          <div className="flex items-center gap-3">
            <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
              selectedAnswer === option
                ? 'border-blue-500'
                : 'border-gray-400 dark:border-gray-500'
            }`}>
              {selectedAnswer === option && (
                <div className="w-3 h-3 rounded-full bg-blue-500" />
              )}
            </div>
            <span className="text-gray-800 dark:text-gray-200">{option}</span>
          </div>
        </button>
      ))}
    </div>
  );
}
