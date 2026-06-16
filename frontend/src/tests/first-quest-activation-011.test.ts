import { describe, it, expect, beforeAll } from 'vitest';
import { t, tl, ti, setLocale } from '@/lib/i18n';

describe('Localization - Preferred Quest and Mission Intro (011)', () => {
  beforeAll(() => {
    setLocale('en-US');
  });

  it('recommended_quest keys exist in en-US', () => {
    expect(t('recommended_quest.title')).toBe('Recommended First Quest');
    expect(t('recommended_quest.for_qa')).toBe('Bug Report Structure');
    expect(t('recommended_quest.for_qa_reason')).toContain('bug report fields');
    expect(t('recommended_quest.for_ba')).toBe('Conflicting Requirements for a Payment Feature');
    expect(t('recommended_quest.for_ba_reason')).toContain('stakeholders');
    expect(t('recommended_quest.start_recommended')).toBe('Start Recommended Quest');
    expect(t('recommended_quest.browse_all')).toBe('Browse All Quests');
    expect(t('recommended_quest.why_this_title')).toBe('Why this quest?');
    expect(t('recommended_quest.estimated_time_label')).toContain('{minutes}');
    expect(t('recommended_quest.steps_label')).toContain('{count}');
  });

  it('recommended_quest keys exist in ru-RU', () => {
    setLocale('ru-RU');
    expect(t('recommended_quest.title')).toBe('Рекомендуемый первый квест');
    expect(t('recommended_quest.for_qa')).toBe('Структура баг-репорта');
    expect(t('recommended_quest.start_recommended')).toBe('Начать рекомендуемый квест');
    expect(t('recommended_quest.why_this_title')).toBe('Почему этот квест?');
    setLocale('en-US');
  });

  it('mission_intro keys exist in en-US', () => {
    expect(t('mission_intro.skills_trained')).toBe('Skills Trained');
    expect(t('mission_intro.estimated_time')).toBe('Estimated Time');
    expect(t('mission_intro.how_feedback_works')).toBe('How Feedback Works');
    expect(t('mission_intro.how_feedback_desc')).toContain('After each answer');
    expect(t('mission_intro.start_mission')).toBe('Start Mission');
    expect(t('mission_intro.skills_list')).toBe('Skills you will practice in this quest');
    expect(t('mission_intro.interaction_types_label')).toBe('Interaction Types');
    expect(t('mission_intro.estimated_time_short')).toContain('{minutes}');
  });

  it('mission_intro keys exist in ru-RU', () => {
    setLocale('ru-RU');
    expect(t('mission_intro.skills_trained')).toBe('Развиваемые навыки');
    expect(t('mission_intro.start_mission')).toBe('Начать миссию');
    setLocale('en-US');
  });

  it('mistakes_review keys exist in en-US', () => {
    expect(t('mistakes_review.title')).toBe('Mistakes Review');
    expect(t('mistakes_review.subtitle')).toContain('Review each step');
    expect(t('mistakes_review.your_answer')).toBe('Your Answer');
    expect(t('mistakes_review.correct_answer')).toBe('Correct Answer');
    expect(t('mistakes_review.explanation')).toBe('Explanation');
    expect(t('mistakes_review.takeaway')).toBe('Takeaway');
    expect(t('mistakes_review.score')).toContain('{score}');
    expect(t('mistakes_review.no_mistakes')).toContain('great job');
    expect(t('mistakes_review.back_to_debrief')).toBe('Back to Debrief');
  });

  it('mistakes_review keys exist in ru-RU', () => {
    setLocale('ru-RU');
    expect(t('mistakes_review.title')).toBe('Разбор ошибок');
    expect(t('mistakes_review.no_mistakes')).toContain('отличная работа');
    setLocale('en-US');
  });

  it('debrief_enhanced keys exist in en-US', () => {
    expect(t('debrief_enhanced.professional_sample')).toBe('Professional Example');
    expect(t('debrief_enhanced.skills_summary')).toBe('Skills Summary');
    expect(t('debrief_enhanced.what_to_repeat')).toBe('What to Repeat');
    expect(t('debrief_enhanced.next_quest')).toBe('Next Recommended Quest');
    expect(t('debrief_enhanced.view_mistakes_review')).toBe('View Mistakes Review');
    expect(t('debrief_enhanced.final_score')).toBe('Final Score');
    expect(t('debrief_enhanced.quest_skills')).toBe('Skills Trained in This Quest');
  });

  it('debrief_enhanced keys exist in ru-RU', () => {
    setLocale('ru-RU');
    expect(t('debrief_enhanced.professional_sample')).toBe('Профессиональный пример');
    expect(t('debrief_enhanced.view_mistakes_review')).toBe('Посмотреть разбор ошибок');
    setLocale('en-US');
  });

  it('next_action keys exist in en-US', () => {
    expect(t('next_action.title')).toBe("What's Next?");
    expect(t('next_action.repeat_weak_topic')).toBe('Repeat This Quest');
    expect(t('next_action.start_next_quest')).toBe('Start Next Quest');
    expect(t('next_action.return_to_catalog')).toBe('Return to Catalog');
    expect(t('next_action.continue_path')).toBe('Continue {trainer} Path');
  });

  it('next_action keys exist in ru-RU', () => {
    setLocale('ru-RU');
    expect(t('next_action.title')).toBe('Что дальше?');
    expect(t('next_action.repeat_weak_topic')).toBe('Повторить этот квест');
    expect(t('next_action.start_next_quest')).toBe('Начать следующий квест');
    setLocale('en-US');
  });

  it('no raw i18n keys returned from tl() for new sections', () => {
    const keys = [
      'recommended_quest.title',
      'recommended_quest.for_qa',
      'recommended_quest.start_recommended',
      'mission_intro.skills_trained',
      'mission_intro.start_mission',
      'mistakes_review.title',
      'mistakes_review.your_answer',
      'debrief_enhanced.professional_sample',
      'debrief_enhanced.view_mistakes_review',
      'next_action.title',
      'next_action.repeat_weak_topic',
    ];
    keys.forEach((key) => {
      const result = t(key);
      expect(result).not.toBe(key);
      expect(result.length).toBeGreaterThan(0);
    });
  });

  it('ti function works with interpolation', () => {
    const result = ti('mission_intro.estimated_time_short', { minutes: '15' });
    expect(result).toBe('15 min');
  });
});
