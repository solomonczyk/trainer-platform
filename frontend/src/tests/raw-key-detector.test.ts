import { describe, it, expect, vi, beforeEach } from 'vitest';

// ---------------------------------------------------------------------------
// Raw-key detector tests — verify that user-visible routes never show
// snake_case translation keys in ru-RU (for BA module list, activity pages,
// domain catalog, trainer cards, interaction badges, and pluralization).
// ---------------------------------------------------------------------------

describe('Raw-key detector: BA module list', () => {
  beforeEach(() => { vi.resetModules(); });

  it('t() resolves common BA activity titles to Russian text (not raw keys)', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');

    // These title keys must resolve to real Russian sentences
    const keys = ['ba_hr_q1_title', 'ba_hr_q2_title', 'ba_hr_q3_title',
                  'ba_basics_q1_title', 'ba_req_q1_title', 'ba_docs_q1_title',
                  'ba_model_q1_title', 'ba_method_q1_title', 'ba_metric_q1_title',
                  'ba_comm_q1_title', 'ba_tech_q1_title', 'ba_cases_q1_title'];
    for (const key of keys) {
      const result = i18n.t(key);
      expect(result).not.toBe(key);
      expect(/[а-яё]/i.test(result)).toBe(true);
      expect(result.length).toBeGreaterThan(10);
    }
  });

  it('t() for module title/description keys returns translated text', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');

    const modules = ['ba_hr_screening', 'ba_basics_stakeholders', 'ba_requirements_elicitation',
                     'ba_documentation_artifacts', 'ba_process_data_modeling'];
    for (const mod of modules) {
      const title = i18n.t(`modules.${mod}.title`);
      const desc = i18n.t(`modules.${mod}.description`);
      expect(title).not.toBe(`modules.${mod}.title`);
      expect(desc).not.toBe(`modules.${mod}.description`);
      expect(/[а-яё]/i.test(title)).toBe(true);
      expect(/[а-яё]/i.test(desc)).toBe(true);
    }
  });
});

describe('Raw-key detector: BA activity page', () => {
  beforeEach(() => { vi.resetModules(); });

  it('activity title resolves to Russian text via generated keys', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');

    // Simulate what happens when t(activityData.title_key) is called
    const title = i18n.t('ba_hr_q1_title');
    expect(title).not.toBe('ba_hr_q1_title');
    expect(/[а-яё]/i.test(title)).toBe(true);
    // It should mention "резюме" for the HR question
    expect(title).toContain('резюме');
  });

  it('activity_type_* badges are localized in ru-RU', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');

    expect(i18n.t('ba_trainer.activity_type_single_choice')).toBe('Один вариант');
    expect(i18n.t('ba_trainer.activity_type_multiple_choice')).toBe('Несколько вариантов');
    expect(i18n.t('ba_trainer.activity_type_matching')).toBe('Сопоставление');
    expect(i18n.t('ba_trainer.activity_type_fill_blanks')).toBe('Заполнение пропусков');
    expect(i18n.t('ba_trainer.activity_type_numeric')).toBe('Числовой ответ');
  });
});

describe('Raw-key detector: Domain catalog', () => {
  beforeEach(() => { vi.resetModules(); });

  it('domain title key resolves to a value (not raw key)', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');

    const domainTitle = i18n.t('domains.it');
    expect(domainTitle).not.toBe('domains.it');
    // "IT" is a Latin abbreviation used in both languages, so it won't be Cyrillic
    expect(domainTitle.length).toBeGreaterThan(0);
  });

  it('domain description resolves to Russian text in ru-RU', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');

    const domainDesc = i18n.t('domains.itDescription');
    expect(domainDesc).not.toBe('domains.itDescription');
    // Must be Russian text, not English "Information Technology"
    expect(domainDesc).not.toContain('Information Technology');
    expect(/[а-яё]/i.test(domainDesc)).toBe(true);
  });
});

describe('Raw-key detector: Trainer cards', () => {
  beforeEach(() => { vi.resetModules(); });

  it('trainer name keys resolve to Russian text', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');

    const trainerName = i18n.t('trainer.business_analyst_interview_trainer');
    expect(trainerName).not.toBe('trainer.business_analyst_interview_trainer');
    expect(/[а-яё]/i.test(trainerName)).toBe(true);

    const trainerDesc = i18n.t('trainer.business_analyst_interview_trainer_desc');
    expect(trainerDesc).not.toBe('trainer.business_analyst_interview_trainer_desc');
    expect(/[а-яё]/i.test(trainerDesc)).toBe(true);
  });
});

describe('Interaction badge localization', () => {
  beforeEach(() => { vi.resetModules(); });

  it('step_* interaction badges show short localized text in ru-RU', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');

    expect(i18n.t('quest.step_single_choice')).not.toBe('single choice');
    expect(i18n.t('quest.step_single_choice')).toBe('Один вариант');
    expect(i18n.t('quest.step_multiple_choice')).toBe('Несколько вариантов');
    expect(i18n.t('quest.step_evidence_select')).toBe('Выбор доказательств');
  });

  it('step_* badges are not raw English keys', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');

    // These must not be raw snake_case
    const badges = ['quest.step_single_choice', 'quest.step_multiple_choice',
                    'quest.step_free_text', 'quest.step_ordering',
                    'quest.step_matching', 'quest.step_evidence_select'];
    for (const key of badges) {
      const val = i18n.t(key);
      expect(val).not.toBe(key);
      expect(val).not.toContain('_');
    }
  });
});

describe('Pluralization: вопрос', () => {
  beforeEach(() => { vi.resetModules(); });

  it('pluralize() returns correct Russian forms for вопрос', async () => {
    const i18n = await import('@/lib/i18n');
    // Test the pluralize function directly
    const { pluralize } = i18n;

    expect(pluralize(1, 'вопрос', 'вопроса', 'вопросов')).toBe('1 вопрос');
    expect(pluralize(2, 'вопрос', 'вопроса', 'вопросов')).toBe('2 вопроса');
    expect(pluralize(5, 'вопрос', 'вопроса', 'вопросов')).toBe('5 вопросов');
    expect(pluralize(20, 'вопрос', 'вопроса', 'вопросов')).toBe('20 вопросов');
    expect(pluralize(21, 'вопрос', 'вопроса', 'вопросов')).toBe('21 вопрос');
  });

  it('activity count uses correct plural form via translation keys', async () => {
    const i18n = await import('@/lib/i18n');
    i18n.setLocale('ru-RU');
    const { pluralize } = i18n;

    // Simulate what the template does: pluralize(count, one, few, many)
    const one = i18n.t('ba_trainer.activity_label_one');
    const few = i18n.t('ba_trainer.activity_label_few');
    const many = i18n.t('ba_trainer.activity_label_many');

    expect(pluralize(1, one, few, many)).toBe('1 вопрос');
    expect(pluralize(2, one, few, many)).toBe('2 вопроса');
    expect(pluralize(5, one, few, many)).toBe('5 вопросов');
    expect(pluralize(20, one, few, many)).toBe('20 вопросов');
  });
});
