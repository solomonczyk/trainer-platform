'use client';

import React from 'react';
import type { QuestStepDefinition } from '@/lib/api/client';
import { tl } from '@/lib/i18n';

// ---------------------------------------------------------------------------
// Shared option button classes — unified across all interaction types
// ---------------------------------------------------------------------------

const OPTION_BASE = "w-full text-left p-4 sm:p-5 rounded border-2 transition-all duration-150";
const OPTION_UNSELECTED = "border-default bg-surface hover:border-interactive hover:shadow-sm";
const OPTION_SELECTED = "border-selected bg-primary-50 shadow-sm";
const OPTION_SELECTED_AMBER = "border-amber-500 bg-amber-50 shadow-sm";
const OPTION_SELECTED_PURPLE = "border-purple-500 bg-purple-50 shadow-sm";
const OPTION_DISABLED = "opacity-60 cursor-not-allowed";
const OPTION_ENABLED = "cursor-pointer focus:outline-none focus:ring-2 focus:ring-ring active:scale-[0.99]";

// ---------------------------------------------------------------------------
// Single Choice
// ---------------------------------------------------------------------------

interface SingleChoiceProps {
  step: QuestStepDefinition;
  value: string | null;
  onChange: (value: string) => void;
  disabled: boolean;
}

export function SingleChoiceRenderer({ step, value, onChange, disabled }: SingleChoiceProps) {
  const options = (step.interaction?.options as Array<{ id: string; text_key: string }>) || [];

  return (
    <div className="space-y-3" role="radiogroup" aria-label="Single choice options">
      {options.map((option) => {
        const isSelected = value === option.id;
        return (
          <button
            key={option.id}
            onClick={() => !disabled && onChange(option.id)}
            disabled={disabled}
            role="radio"
            aria-checked={isSelected}
            tabIndex={0}
            className={`${OPTION_BASE} ${
              isSelected ? OPTION_SELECTED : OPTION_UNSELECTED
            } ${disabled ? OPTION_DISABLED : OPTION_ENABLED}`}
          >
            <div className="flex items-center gap-4">
              <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
                isSelected ? 'border-primary-500 bg-primary-500' : 'border-gray-400 bg-surface'
              }`}>
                {isSelected && <div className="w-2.5 h-2.5 rounded-full bg-white" />}
              </div>
              <span className="text-body font-semibold text-foreground leading-snug">
                {tl(option.text_key)}
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Multiple Choice
// ---------------------------------------------------------------------------

interface MultipleChoiceProps {
  step: QuestStepDefinition;
  value: string[];
  onChange: (value: string[]) => void;
  disabled: boolean;
}

export function MultipleChoiceRenderer({ step, value = [], onChange, disabled }: MultipleChoiceProps) {
  const choices = (step.interaction?.choices || step.interaction?.options || []) as Array<{ id: string; text_key: string }>;
  const minSelect = (step.interaction?.min_selections as number) || 1;
  const maxSelect = (step.interaction?.max_selections as number) || 0;

  const toggleOption = (id: string) => {
    if (disabled) return;
    const newValue = value.includes(id)
      ? value.filter((v) => v !== id)
      : [...value, id];
    onChange(newValue);
  };

  return (
    <div className="space-y-3" role="group" aria-label="Multiple choice options">
      {choices.map((choice) => {
        const isSelected = value.includes(choice.id);
        return (
          <button
            key={choice.id}
            onClick={() => toggleOption(choice.id)}
            disabled={disabled}
            role="checkbox"
            aria-checked={isSelected}
            className={`${OPTION_BASE} ${
              isSelected ? OPTION_SELECTED : OPTION_UNSELECTED
            } ${disabled ? OPTION_DISABLED : OPTION_ENABLED}`}
          >
            <div className="flex items-center gap-4">
              <div className={`w-6 h-6 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
                isSelected ? 'border-primary-500 bg-primary-500' : 'border-gray-400 bg-surface'
              }`}>
                {isSelected && (
                  <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </div>
              <span className="text-body font-semibold text-foreground leading-snug">{tl(choice.text_key)}</span>
            </div>
          </button>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Free Text
// ---------------------------------------------------------------------------

interface FreeTextProps {
  step: QuestStepDefinition;
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
}

export function FreeTextRenderer({ step, value = '', onChange, disabled }: FreeTextProps) {
  const maxLength = (step.interaction?.max_length as number) || 3000;
  const minLength = (step.interaction?.min_length as number) || 50;
  const placeholder = ((step.interaction?.placeholder_key as string) || 'quest.write_answer');
  const guidance = (step.interaction?.guidance_key as string) || '';

  return (
    <div className="space-y-4">
      {guidance && (
        <div className="rounded bg-blue-50 p-5 border border-blue-200">
          <p className="text-body text-blue-800 leading-relaxed font-medium">{guidance}</p>
        </div>
      )}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder}
        rows={8}
        maxLength={maxLength}
        className="block w-full rounded border-2 border-default px-5 py-4 text-body shadow-sm placeholder:text-text-muted focus:border-interactive focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 disabled:bg-muted bg-surface text-foreground leading-relaxed"
        aria-label="Free text answer"
      />
      <div className="flex justify-between text-body-sm font-medium text-text-secondary">
        <span>{minLength > 0 ? `Minimum ${minLength} characters` : ''}</span>
        <span>{value.length > 0 ? `${maxLength - value.length} characters remaining` : ''}</span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Ordering
// ---------------------------------------------------------------------------

interface OrderingProps {
  step: QuestStepDefinition;
  value: string[];
  onChange: (value: string[]) => void;
  disabled: boolean;
}

export function OrderingRenderer({ step, value = [], onChange, disabled }: OrderingProps) {
  const items = (step.interaction?.items as Array<{ id: string; text_key: string }>) || [];
  const orderedItems = value.length === items.length ? value : items.map((i) => i.id);

  const moveItem = (index: number, direction: -1 | 1) => {
    if (disabled) return;
    const newOrder = [...orderedItems];
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= newOrder.length) return;
    [newOrder[index], newOrder[targetIndex]] = [newOrder[targetIndex], newOrder[index]];
    onChange(newOrder);
  };

  return (
    <div className="space-y-2" role="list" aria-label="Ordering items">
      {orderedItems.map((itemId, index) => {
        const item = items.find((i) => i.id === itemId);
        return (
          <div
            key={itemId}
            role="listitem"
            className="flex items-center gap-3 p-3 rounded border border-default bg-surface"
          >
            <span className="flex items-center justify-center w-8 h-8 rounded-full bg-muted text-body-sm font-bold text-text-secondary">
              {index + 1}
            </span>
            <span className="flex-1 text-body text-foreground">
              {item ? tl(item.text_key) : itemId}
            </span>
            <div className="flex gap-1">
              <button
                onClick={() => moveItem(index, -1)}
                disabled={disabled || index === 0}
                className="p-1.5 rounded hover:bg-muted disabled:opacity-30 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-ring"
                aria-label="Move up"
                tabIndex={0}
              >
                <svg className="w-4 h-4 text-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" /></svg>
              </button>
              <button
                onClick={() => moveItem(index, 1)}
                disabled={disabled || index === orderedItems.length - 1}
                className="p-1.5 rounded hover:bg-muted disabled:opacity-30 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-ring"
                aria-label="Move down"
                tabIndex={0}
              >
                <svg className="w-4 h-4 text-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Matching
// ---------------------------------------------------------------------------

interface MatchingProps {
  step: QuestStepDefinition;
  value: Record<string, string>;
  onChange: (value: Record<string, string>) => void;
  disabled: boolean;
}

export function MatchingRenderer({ step, value = {}, onChange, disabled }: MatchingProps) {
  const leftItems = (step.interaction?.left_items as string[]) || [];
  const rightItems = (step.interaction?.right_items as string[]) || [];
  const rightOptions = rightItems.filter((r) => !Object.values(value).includes(r));

  const setMapping = (left: string, right: string) => {
    if (disabled) return;
    const newValue = { ...value };
    // Remove existing mapping for this right item if any
    for (const [k, v] of Object.entries(newValue)) {
      if (v === right) delete newValue[k];
    }
    // Remove existing mapping for this left item
    delete newValue[left];
    newValue[left] = right;
    onChange(newValue);
  };

  const clearMapping = (left: string) => {
    if (disabled) return;
    const newValue = { ...value };
    delete newValue[left];
    onChange(newValue);
  };

  return (
    <div className="space-y-3" role="group" aria-label="Matching pairs">
      {leftItems.map((left) => {
        const mappedRight = value[left] || '';
        const availableOptions = mappedRight ? [...rightItems] : rightOptions;

        return (
          <div key={left} className="flex items-center gap-3 p-3 rounded border border-default bg-surface">
            <span className="flex-1 text-body-sm font-medium text-foreground">{tl(left)}</span>
            <svg className="w-5 h-5 text-text-muted flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11l5-5m0 0l5 5m-5-5v12" />
            </svg>
            <select
              value={mappedRight}
              onChange={(e) => e.target.value && setMapping(left, e.target.value)}
              disabled={disabled}
              className="flex-1 rounded border border-default px-3 py-2 text-body-sm bg-surface disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-ring"
              aria-label={`Match for ${left}`}
            >
              <option value="">Select...</option>
              {availableOptions.map((r) => (
                <option key={r} value={r}>{tl(r)}</option>
              ))}
            </select>
            {mappedRight && (
              <button
                onClick={() => clearMapping(left)}
                disabled={disabled}
                className="p-1 text-text-danger hover:text-danger-700 focus:outline-none focus:ring-2 focus:ring-ring rounded"
                aria-label="Clear mapping"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Evidence Select
// ---------------------------------------------------------------------------

interface EvidenceSelectProps {
  step: QuestStepDefinition;
  value: string[];
  onChange: (value: string[]) => void;
  disabled: boolean;
}

export function EvidenceSelectRenderer({ step, value = [], onChange, disabled }: EvidenceSelectProps) {
  const items = (step.interaction?.evidence_items as Array<{ id: string; text_key: string; category?: string }>) || [];
  const evidencePanelKey = (step.interaction?.evidence_panel_key as string) || '';

  const toggleItem = (id: string) => {
    if (disabled) return;
    const newValue = value.includes(id)
      ? value.filter((v) => v !== id)
      : [...value, id];
    onChange(newValue);
  };

  // Group by category
  const grouped: Record<string, typeof items> = {};
  for (const item of items) {
    const cat = item.category || 'other';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(item);
  }

  const panelLines = evidencePanelKey ? tl(evidencePanelKey).split('\n') : [];

  return (
    <div className="space-y-4" role="group" aria-label="Evidence selection">
      {/* Evidence panel — shown before options, e.g. bad bug report to inspect */}
      {panelLines.length > 0 && (
        <div className="rounded border-2 border-gray-300 bg-gray-50 overflow-hidden">
          <div className="px-4 py-2 bg-gray-200 border-b border-gray-300">
            <span className="text-caption font-semibold uppercase tracking-wider text-gray-600">
              {tl('quest.qa.bug_report.step04.context').split(':')[0]}
            </span>
          </div>
          <div className="p-4 font-mono text-sm leading-relaxed text-gray-800 whitespace-pre-wrap">
            {panelLines.map((line, i) => {
              // Bold section headers (lines ending with ':' or containing known headers)
              const isHeader = /^(Title|Заголовок|Steps to Reproduce|Шаги воспроизведения|Actual Result|Фактический результат|Expected Result|Ожидаемый результат|Environment|Окружение|Severity|Priority|Attachments|Вложения):/.test(line.trim());
              return isHeader ? (
                <div key={i} className="font-semibold text-gray-900 mt-1 first:mt-0">{line}</div>
              ) : (
                <div key={i}>{line}</div>
              );
            })}
          </div>
        </div>
      )}
      {Object.entries(grouped).map(([category, categoryItems]) => (
        <div key={category}>
          <h4 className="text-caption font-semibold uppercase tracking-wider text-text-muted mb-2">
            {category}
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {categoryItems.map((item) => {
              const isSelected = value.includes(item.id);
              return (
                <button
                  key={item.id}
                  onClick={() => toggleItem(item.id)}
                  disabled={disabled}
                  className={`p-3 rounded border-2 text-left transition-all ${
                    isSelected
                      ? 'border-selected bg-primary-50'
                      : 'border-default bg-surface hover:border-interactive hover:bg-muted'
                  } ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-ring'}`}
                  aria-pressed={isSelected}
                >
                  <div className="flex items-start gap-2">
                    <div className={`mt-0.5 w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0 ${
                      isSelected ? 'border-primary-500 bg-primary-500' : 'border-gray-400'
                    }`}>
                      {isSelected && (
                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                    <span className="text-body-sm text-foreground">{tl(item.text_key)}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Decision
// ---------------------------------------------------------------------------

interface DecisionProps {
  step: QuestStepDefinition;
  value: string | null;
  onChange: (value: string) => void;
  disabled: boolean;
}

export function DecisionRenderer({ step, value, onChange, disabled }: DecisionProps) {
  const options = (step.interaction?.options as Array<{ id: string; text_key: string }>) || [];

  return (
    <div className="space-y-3" role="radiogroup" aria-label="Decision options">
      {options.map((option) => {
        const isSelected = value === option.id;
        return (
          <button
            key={option.id}
            onClick={() => !disabled && onChange(option.id)}
            disabled={disabled}
            role="radio"
            aria-checked={isSelected}
            className={`${OPTION_BASE} ${
              isSelected ? OPTION_SELECTED_AMBER : OPTION_UNSELECTED
            } ${disabled ? OPTION_DISABLED : 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-amber-500'}`}
          >
            <div className="flex items-center gap-3">
              <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                isSelected ? 'border-amber-500' : 'border-gray-400'
              }`}>
                {isSelected && <div className="w-3.5 h-3.5 rounded-full bg-amber-500" />}
              </div>
              <div>
                <span className="text-body font-semibold text-foreground">{tl(option.text_key)}</span>
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Dialogue
// ---------------------------------------------------------------------------

interface DialogueProps {
  step: QuestStepDefinition;
  value: string | null;
  onChange: (value: string) => void;
  disabled: boolean;
  userValue?: string;
  onUserValueChange?: (value: string) => void;
}

export function DialogueRenderer({ step, value, onChange, disabled, userValue = '', onUserValueChange }: DialogueProps) {
  const characterSaysKey = (step.interaction?.character_says_key as string) || '';
  const options = (step.interaction?.options as Array<{ id: string; text_key: string }>) || [];
  const allowFreeText = step.interaction?.allow_free_text as boolean;
  const maxLength = (step.interaction?.max_length as number) || 2000;
  const placeholder = (step.interaction?.placeholder_key as string) || 'quest.write_response';

  return (
    <div className="space-y-4">
      {/* Character says */}
      {characterSaysKey && (
        <div className="rounded bg-purple-50 p-5 border border-purple-200">
          <p className="text-body italic text-purple-800">{tl(characterSaysKey)}</p>
        </div>
      )}

      {/* Predefined responses */}
      {options.length > 0 && (
        <div className="space-y-2">
          <p className="text-caption font-semibold uppercase tracking-wider text-text-secondary">Choose a response:</p>
          {options.map((option) => {
            const isSelected = value === option.id;
            return (
              <button
                key={option.id}
                onClick={() => !disabled && onChange(option.id)}
                disabled={disabled}
                className={`${OPTION_BASE} ${
                  isSelected ? OPTION_SELECTED_PURPLE : OPTION_UNSELECTED
                } ${disabled ? OPTION_DISABLED : 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-purple-500'}`}
              >
                <span className="text-body-sm text-foreground">{tl(option.text_key)}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Free text response */}
      {allowFreeText && (
        <div className="space-y-2">
          <textarea
            value={userValue}
            onChange={(e) => onUserValueChange?.(e.target.value)}
            disabled={disabled}
            placeholder={placeholder}
            rows={5}
            maxLength={maxLength}
            className="block w-full rounded border border-default px-4 py-3 text-body-sm focus:border-interactive focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 bg-surface text-foreground"
            aria-label="Dialogue response"
          />
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Unknown step fallback
// ---------------------------------------------------------------------------

interface UnknownStepProps {
  step: QuestStepDefinition;
}

export function UnknownStepRenderer({ step }: UnknownStepProps) {
  return (
    <div className="p-4 text-warning-700 bg-warning-50 rounded border border-warning-200">
      Unknown step type: {step.step_type}
    </div>
  );
}
