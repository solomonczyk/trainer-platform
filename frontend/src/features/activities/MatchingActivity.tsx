'use client';

import React from 'react';

interface MatchingActivityProps {
  leftItems: string[];
  rightItems: string[];
  mappings: Record<string, string>;
  onMapping: (left: string, right: string) => void;
  disabled: boolean;
}

export function MatchingActivity({ leftItems, rightItems, mappings, onMapping, disabled }: MatchingActivityProps) {
  return (
    <div className="space-y-4">
      {leftItems.map((left, index) => (
        <div key={index} className="flex items-center gap-4">
          <div className="flex-1 p-3 bg-gray-100 dark:bg-gray-800 rounded-lg text-gray-800 dark:text-gray-200 font-medium">
            {left}
          </div>
          <div className="text-gray-400">→</div>
          <div className="flex-1">
            <select
              value={mappings[left] || ''}
              onChange={(e) => onMapping(left, e.target.value)}
              disabled={disabled}
              className="w-full p-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 focus:border-blue-500 focus:outline-none disabled:opacity-60"
            >
              <option value="">...</option>
              {rightItems.map((right, ri) => (
                <option key={ri} value={right}>{right}</option>
              ))}
            </select>
          </div>
        </div>
      ))}
    </div>
  );
}
