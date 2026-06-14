'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { listQuests } from '@/lib/api/client';
import { tl } from '@/lib/i18n';
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
          {quests.map((q: any) => (
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
                      {q.estimated_minutes} min
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
        </div>
      )}
    </PageContainer>
  );
}
