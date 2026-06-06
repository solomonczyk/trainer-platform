'use client';

import React from 'react';
import { SingleChoiceActivity } from './SingleChoiceActivity';
import { MultipleChoiceActivity } from './MultipleChoiceActivity';
import { NumericActivity } from './NumericActivity';
import { FillBlanksActivity } from './FillBlanksActivity';
import { MatchingActivity } from './MatchingActivity';

export type ActivityType = 'single_choice' | 'multiple_choice' | 'numeric' | 'fill_blanks' | 'matching';

interface ActivityRendererProps {
  activityType: ActivityType;
  prompt: Record<string, unknown>;
  answer: unknown;
  onAnswer: (answer: unknown) => void;
  disabled: boolean;
}

export function ActivityRenderer({ activityType, prompt, answer, onAnswer, disabled }: ActivityRendererProps) {
  switch (activityType) {
    case 'single_choice':
      return (
        <SingleChoiceActivity
          options={prompt.options as string[] || []}
          selectedAnswer={answer as string | null}
          onAnswer={(val) => onAnswer(val)}
          disabled={disabled}
        />
      );

    case 'multiple_choice':
      return (
        <MultipleChoiceActivity
          options={prompt.options as string[] || []}
          selectedAnswers={answer as string[] || []}
          onAnswer={(val) => onAnswer(val)}
          disabled={disabled}
        />
      );

    case 'numeric':
      return (
        <NumericActivity
          value={answer as string || ''}
          onAnswer={(val) => onAnswer(val)}
          disabled={disabled}
        />
      );

    case 'fill_blanks':
      return (
        <FillBlanksActivity
          template={prompt.template as string || ''}
          blanks={(prompt.blanks as Array<{id: string; options?: string[]}> || [])}
          filledAnswers={answer as Record<string, string> || {}}
          onAnswer={(blankId, value) => {
            const current = (answer as Record<string, string>) || {};
            onAnswer({ ...current, [blankId]: value });
          }}
          disabled={disabled}
        />
      );

    case 'matching':
      return (
        <MatchingActivity
          leftItems={prompt.left_items as string[] || []}
          rightItems={prompt.right_items as string[] || []}
          mappings={answer as Record<string, string> || {}}
          onMapping={(left, right) => {
            const current = (answer as Record<string, string>) || {};
            onAnswer({ ...current, [left]: right });
          }}
          disabled={disabled}
        />
      );

    default:
      return (
        <div className="p-4 text-yellow-700 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
          Unknown activity type: {activityType}
        </div>
      );
  }
}
