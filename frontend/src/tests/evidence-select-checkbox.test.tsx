import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { EvidenceSelectRenderer } from '@/features/quests/interaction-renderers';
import type { QuestStepDefinition } from '@/lib/api/client';

// --- Mock i18n ---
vi.mock('@/lib/i18n', () => ({
  tl: (key: string) => {
    const map: Record<string, string> = {
      'evidence.title': 'Bug report title: Login fails on Safari',
      'evidence.step': 'Actual Result: Page crashes',
      'evidence.result': 'Expected Result: Successful login',
    };
    return map[key] ?? key;
  },
  ti: (key: string, params?: Record<string, string | number>) => {
    let text = key || '';
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        text = text.replace(`{${k}}`, String(v));
      }
    }
    return text;
  },
}));

// -------------------------------------------------------------------------
// Test Data
// -------------------------------------------------------------------------

const EVIDENCE_ITEMS = [
  { id: 'ev_1', text_key: 'evidence.title', category: 'Bug Report' },
  { id: 'ev_2', text_key: 'evidence.step', category: 'Bug Report' },
  { id: 'ev_3', text_key: 'evidence.result', category: 'Expected Behavior' },
];

const baseStep: QuestStepDefinition = {
  step_type: 'evidence_select',
  title_key: 'test.evidence.title',
  instruction_key: 'test.evidence.instruction',
  interaction: {
    evidence_items: EVIDENCE_ITEMS,
  },
} as unknown as QuestStepDefinition;

// -------------------------------------------------------------------------
// Helpers
// -------------------------------------------------------------------------

function renderEvidence(value: string[] = [], onChange = vi.fn(), disabled = false) {
  return render(
    <EvidenceSelectRenderer
      step={baseStep}
      value={value}
      onChange={onChange}
      disabled={disabled}
    />
  );
}

function getEvidenceButtons() {
  return screen.getAllByRole('checkbox');
}

// -------------------------------------------------------------------------
// Tests
// -------------------------------------------------------------------------

describe('EvidenceSelectRenderer — Multi-select Checkbox Semantics', () => {

  it('renders each evidence item with role="checkbox"', () => {
    renderEvidence();
    const buttons = getEvidenceButtons();
    expect(buttons.length).toBe(EVIDENCE_ITEMS.length);
    buttons.forEach((btn) => {
      expect(btn.getAttribute('role')).toBe('checkbox');
    });
  });

  it('sets aria-checked correctly on selected and unselected items', () => {
    const selectedIds = ['ev_1', 'ev_3'];
    renderEvidence(selectedIds);
    const buttons = getEvidenceButtons();

    // ev_1 — should be checked
    expect(buttons[0].getAttribute('aria-checked')).toBe('true');
    // ev_2 — should NOT be checked
    expect(buttons[1].getAttribute('aria-checked')).toBe('false');
    // ev_3 — should be checked
    expect(buttons[2].getAttribute('aria-checked')).toBe('true');
  });

  it('does NOT use aria-pressed (radio-like) attributes', () => {
    renderEvidence();
    const buttons = getEvidenceButtons();
    buttons.forEach((btn) => {
      expect(btn.hasAttribute('aria-pressed')).toBe(false);
    });
  });

  it('toggles selection on click (multi-select behavior)', () => {
    const onChange = vi.fn();
    renderEvidence([], onChange);

    const buttons = getEvidenceButtons();
    fireEvent.click(buttons[0]);
    expect(onChange).toHaveBeenCalledWith(['ev_1']);

    fireEvent.click(buttons[1]);
    expect(onChange).toHaveBeenCalledWith(['ev_2']);
  });

  it('de-selects an already-selected item', () => {
    const onChange = vi.fn();
    renderEvidence(['ev_1', 'ev_2'], onChange);

    const buttons = getEvidenceButtons();
    // Click already-selected item to deselect
    fireEvent.click(buttons[0]);
    expect(onChange).toHaveBeenCalledWith(['ev_2']);
  });

  it('does not toggle when disabled', () => {
    const onChange = vi.fn();
    renderEvidence(['ev_1'], onChange, true);

    const buttons = getEvidenceButtons();
    fireEvent.click(buttons[0]);
    expect(onChange).not.toHaveBeenCalled();
  });

  it('renders checkbox visual indicator (square box with checkmark)', () => {
    const { container } = renderEvidence(['ev_1']);
    const buttons = getEvidenceButtons();

    // First item is selected — should show filled square checkbox with checkmark SVG
    const selectedSvg = buttons[0].querySelector('svg');
    expect(selectedSvg).not.toBeNull();

    // Second item is not selected — checkbox should be empty
    const unselectedCheckbox = buttons[1].querySelector('div.mt-0\\.5');
    // Should still have the border-gray-400 indicator (unfilled square)
    expect(buttons[1].innerHTML).toContain('border-gray-400');
  });
});
