import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';

// -------------------------------------------------------------------------
// Test 5: BA HR question renders no raw keys in ru-RU
// -------------------------------------------------------------------------

describe('BA HR question i18n — no raw keys visible', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('t("ba_hr_q1_title") returns the Russian question sentence in ru-RU', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');
    const result = i18n.t('ba_hr_q1_title');

    // Must be a real Russian sentence containing Cyrillic, not "ba_hr_q1_title"
    expect(result).not.toBe('ba_hr_q1_title');
    expect(result).toMatch(/[а-яё]/i);
    expect(result.length).toBeGreaterThan(20);
    expect(result).toContain('резюме');
  });

  it('t("ba_hr_q1_title") returns an English sentence in en-US', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('en-US');
    const result = i18n.t('ba_hr_q1_title');

    expect(result).not.toBe('ba_hr_q1_title');
    expect(result).toMatch(/[a-z]/i);
    expect(result.length).toBeGreaterThan(5);
    expect(result).toContain('HR Screening');
  });

  it('ru-RU translation contains expected Russian text for ba_hr_q1_title', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');
    const titleText = i18n.t('ba_hr_q1_title');

    // Verify the translation is a real Russian sentence
    expect(titleText).not.toBe('ba_hr_q1_title');
    expect(/[а-яё]/i.test(titleText)).toBe(true);
    expect(titleText).toContain('резюме');
  });
});

// -------------------------------------------------------------------------
// Test 6: Interaction type badge is localized
// -------------------------------------------------------------------------

describe('Interaction type badge localization', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('ru-RU activity_type_* returns localized badge text', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');
    expect(i18n.t('ba_trainer.activity_type_single_choice')).toBe('Один вариант');
    expect(i18n.t('ba_trainer.activity_type_multiple_choice')).toBe('Несколько вариантов');
    expect(i18n.t('ba_trainer.activity_type_matching')).toBe('Сопоставление');
    expect(i18n.t('ba_trainer.activity_type_ordering')).toBe('Упорядочивание');
    expect(i18n.t('ba_trainer.activity_type_evidence_select')).toBe('Выбор доказательств');
    expect(i18n.t('ba_trainer.activity_type_free_text')).toBe('Свободный ответ');
  });

  it('en-US activity_type_* returns localized badge text', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('en-US');
    expect(i18n.t('ba_trainer.activity_type_single_choice')).toBe('Single Choice');
    expect(i18n.t('ba_trainer.activity_type_multiple_choice')).toBe('Multiple Choice');
    expect(i18n.t('ba_trainer.activity_type_matching')).toBe('Matching');
    expect(i18n.t('ba_trainer.activity_type_ordering')).toBe('Ordering');
    expect(i18n.t('ba_trainer.activity_type_evidence_select')).toBe('Evidence Select');
    expect(i18n.t('ba_trainer.activity_type_free_text')).toBe('Free Text');
  });

  it('ru-RU step_* interaction type badges return short badge-style text', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');

    // The step_* keys should now return short badge text, not instructional text
    expect(i18n.t('quest.step_single_choice')).toBe('Один вариант');
    expect(i18n.t('quest.step_multiple_choice')).toBe('Несколько вариантов');
    expect(i18n.t('quest.step_matching')).toBe('Сопоставление');
    expect(i18n.t('quest.step_ordering')).toBe('Упорядочивание');
    expect(i18n.t('quest.step_evidence_select')).toBe('Выбор доказательств');
    expect(i18n.t('quest.step_free_text')).toBe('Свободный ответ');
  });

  it('en-US step_* interaction type badges return short badge-style text', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('en-US');

    expect(i18n.t('quest.step_single_choice')).toBe('Single Choice');
    expect(i18n.t('quest.step_multiple_choice')).toBe('Multiple Choice');
    expect(i18n.t('quest.step_matching')).toBe('Matching');
    expect(i18n.t('quest.step_ordering')).toBe('Ordering');
    expect(i18n.t('quest.step_evidence_select')).toBe('Evidence Select');
    expect(i18n.t('quest.step_free_text')).toBe('Free Text');
  });
});
