'use client';

import { useState, useEffect, useMemo } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { listQuests } from '@/lib/api/client';
import { tl, t } from '@/lib/i18n';
import Button from '@/components/ui/Button';
import Card, { CardTitle } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import PageContainer, { SectionHeader } from '@/components/ui/PageContainer';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import {
  BookOpen,
  Play,
  Clock,
  Users,
  Layers,
  ChevronRight,
  ArrowLeft,
  AlertCircle,
  Star,
  Award,
  Lightbulb,
  Target,
} from 'lucide-react';

export default function QuestCatalogPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;

  const { data, isLoading, error } = useQuery({
    queryKey: ['quests'],
    queryFn: () => listQuests(),
  });

  // Normalize slug comparison: URL uses hyphens (qa-engineer-...),
  // quest data trainer_slug uses underscores (qa_engineer_...)
  const normalizedSlug = slug.replace(/-/g, '_');
  const quests = data?.quests
    ? Object.values(data.quests).filter((q: any) => q.trainer_slug === slug || q.trainer_slug === normalizedSlug)
    : [];

  // Determine recommended quest (match backend quest IDs)
  const isQA = slug.includes('qa') || normalizedSlug.includes('qa');
  const recommendedQuestId = isQA ? 'qa_bug_report_structure_v1' : 'ba_payment_requirements_conflict';
  const recommendedTitleKey = isQA ? 'quest.qa.bug_report' : 'quest.ba.payment_conflict';

  const recommendedQuest = useMemo(() => {
    return quests.find((q: any) => q.quest_id === recommendedQuestId) || null;
  }, [quests, recommendedQuestId]);

  const otherQuests = useMemo(() => {
    return quests.filter((q: any) => q.quest_id !== recommendedQuestId);
  }, [quests, recommendedQuestId]);

  return (
    <PageContainer>
      <button
        onClick={() => router.push(`/trainers/${slug}`)}
        className="mb-6 inline-flex items-center gap-1.5 text-label text-text-secondary hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        {tl('quest.back_to_trainer')}
      </button>

      <SectionHeader
        title={tl('quest.quest_catalog')}
        description={tl('quest.quest_catalog_desc')}
      />

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" label={tl('common.loading')} />
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-danger-50 p-4 text-body-sm text-danger-700 border border-danger-200">
          {tl('common.error')}: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      )}

      {!isLoading && !error && quests.length === 0 && (
        <Card padding="lg" variant="default" className="text-center">
          <div className="flex flex-col items-center gap-4 py-6">
            <BookOpen className="h-12 w-12 text-text-muted" />
            <p className="text-body text-text-secondary">{tl('quest.no_quests')}</p>
          </div>
        </Card>
      )}

      {quests.length > 0 && (
        <div className="space-y-5">
          {/* Recommended Quest Banner */}
          {recommendedQuest && (
            <Card
              padding="lg"
              variant="elevated"
              className="border-2 border-selected shadow-elevated bg-gradient-to-br from-primary-50 to-purple-50 mb-6"
            >
              <div className="flex flex-col sm:flex-row sm:items-center gap-5">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-3">
                    <Star className="h-5 w-5 text-primary-600" />
                    <span className="text-caption font-bold uppercase tracking-wider text-primary-700">
                      {t('recommended_quest.title')}
                    </span>
                  </div>
                  <CardTitle className="text-h3 mb-2 leading-tight text-primary-900">
                    {(recommendedQuest as any).title_key
                      ? tl((recommendedQuest as any).title_key)
                      : (recommendedQuest as any).quest_id}
                  </CardTitle>
                  <p className="text-body text-text-secondary mb-4 leading-relaxed">
                    {isQA
                      ? t('recommended_quest.for_qa_reason')
                      : t('recommended_quest.for_ba_reason')}
                  </p>

                  <div className="flex flex-wrap items-center gap-4 mb-3">
                    <span className="inline-flex items-center gap-1.5 text-body-sm font-medium text-text-secondary">
                      <Clock className="h-4 w-4 text-text-muted" />
                      {t('recommended_quest.estimated_time_label').replace('{minutes}', String((recommendedQuest as any).estimated_minutes || 15))}
                    </span>
                    <span className="inline-flex items-center gap-1.5 text-body-sm font-medium text-text-secondary">
                      <Layers className="h-4 w-4 text-text-muted" />
                      {tl('quest.steps_count').replace('{count}', String((recommendedQuest as any).steps_count || 5))}
                    </span>
                    <span className="inline-flex items-center gap-1.5 text-body-sm font-medium text-primary-700">
                      <Award className="h-4 w-4" />
                      {isQA
                        ? t('recommended_quest.for_qa_skills')
                        : t('recommended_quest.for_ba_skills')}
                    </span>
                  </div>

                  {/* Why this quest explanation */}
                  <div className="rounded bg-white/60 p-3 mb-3 border border-primary-200">
                    <div className="flex items-start gap-2">
                      <Lightbulb className="h-4 w-4 text-primary-600 flex-shrink-0 mt-0.5" />
                      <p className="text-body-sm text-primary-800">
                        {isQA
                          ? t('recommended_quest.for_qa_why')
                          : t('recommended_quest.for_ba_why')}
                      </p>
                    </div>
                  </div>

                  {/* Interaction type badges */}
                  <div className="flex flex-wrap gap-2">
                    {((recommendedQuest as any).interaction_types as string[] || ['multiple_choice', 'ordering', 'free_text', 'matching']).map((type: string) => (
                      <Badge key={type} variant="primary" size="sm">
                        {tl(`quest.step_${type}`)}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="flex-shrink-0 self-start sm:self-center">
                  <Button
                    size="lg"
                    onClick={() => router.push(`/trainers/${slug}/quests/${(recommendedQuest as any).quest_id}`)}
                    className="shadow-md px-6"
                  >
                    <Play className="h-5 w-5" />
                    {t('recommended_quest.start_recommended')}
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* Other quests */}
          {otherQuests.length > 0 && (
            <>
              <h3 className="text-h3 text-foreground mb-4 mt-8">
                {t('recommended_quest.browse_all')}
              </h3>
              {otherQuests.map((q: any) => (
                <Card
                  key={q.quest_id}
                  padding="lg"
                  hover
                  variant="default"
                  className="border-2 hover:border-interactive hover:shadow-elevated"
                  onClick={() => router.push(`/trainers/${slug}/quests/${q.quest_id}`)}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center gap-5">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-h3 mb-2 leading-tight">
                        {tl(q.title_key) !== q.title_key ? tl(q.title_key) : q.title_key}
                      </CardTitle>
                      <p className="text-body text-text-secondary mb-4 line-clamp-3 leading-relaxed">
                        {tl(q.summary_key) !== q.summary_key ? tl(q.summary_key) : q.summary_key}
                      </p>

                      <div className="flex flex-wrap items-center gap-4 mb-3">
                        <span className="inline-flex items-center gap-1.5 text-body-sm font-medium text-text-secondary">
                          <Clock className="h-4 w-4 text-text-muted" />
                          {t('recommended_quest.estimated_time_label').replace('{minutes}', String(q.estimated_minutes))}
                        </span>
                        <span className="inline-flex items-center gap-1.5 text-body-sm font-medium text-text-secondary">
                          <Layers className="h-4 w-4 text-text-muted" />
                          {tl('quest.steps_count').replace('{count}', String(q.steps_count))}
                        </span>
                        <span className="inline-flex items-center gap-1.5 text-body-sm font-medium text-text-secondary">
                          <Users className="h-4 w-4 text-text-muted" />
                          {q.characters_count} {tl('quest.characters')}
                        </span>
                      </div>

                      {/* Interaction type badges */}
                      <div className="flex flex-wrap gap-2">
                        {(q.interaction_types as string[]).map((type: string) => (
                          <Badge key={type} variant="primary" size="sm">
                            {tl(`quest.step_${type}`)}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="flex-shrink-0 self-start sm:self-center">
                      <Button size="md" className="shadow-sm">
                        <Play className="h-5 w-5" />
                        {tl('quest.start_quest')}
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </>
          )}
        </div>
      )}
    </PageContainer>
  );
}
