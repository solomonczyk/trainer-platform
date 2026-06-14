'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { listQuests } from '@/lib/api/client';
import { tl } from '@/lib/i18n';
import Button from '@/components/ui/Button';
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import {
  BookOpen,
  Play,
  Clock,
  Users,
  Layers,
  ChevronRight,
  ArrowLeft,
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
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      <button
        onClick={() => router.push(`/trainers/${slug}`)}
        className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        {tl('quest.back_to_trainer')}
      </button>

      <div className="mb-10">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          {tl('quest.quest_catalog')}
        </h1>
        <p className="mt-3 text-base sm:text-lg text-gray-600 dark:text-gray-300 leading-relaxed">
          {tl('quest.quest_catalog_desc')}
        </p>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 dark:bg-red-900/20 p-4 text-sm text-red-700 dark:text-red-300">
          {tl('common.error')}: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      )}

      {!isLoading && !error && quests.length === 0 && (
        <Card padding="lg" className="text-center">
          <div className="flex flex-col items-center gap-4 py-6">
            <BookOpen className="h-12 w-12 text-gray-300" />
            <p className="text-gray-500">{tl('quest.no_quests')}</p>
          </div>
        </Card>
      )}

      {quests.length > 0 && (
        <div className="space-y-5">
          {quests.map((q: any) => (
            <Card key={q.quest_id} padding="lg" className="border-2 border-gray-200 hover:border-primary-400 hover:shadow-lg transition-all duration-200 cursor-pointer bg-white dark:bg-gray-900"
              onClick={() => router.push(`/trainers/${slug}/quests/${q.quest_id}`)}
            >
              <div className="flex flex-col sm:flex-row sm:items-center gap-5">
                <div className="flex-1 min-w-0">
                  <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-2 leading-tight">
                    {tl(q.title_key) !== q.title_key ? tl(q.title_key) : q.title_key}
                  </h2>
                  <p className="text-base sm:text-[16px] text-gray-700 dark:text-gray-300 mb-4 line-clamp-3 leading-relaxed">
                    {tl(q.summary_key) !== q.summary_key ? tl(q.summary_key) : q.summary_key}
                  </p>

                  <div className="flex flex-wrap items-center gap-4 mb-3">
                    <span className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">
                      <Clock className="h-4 w-4 text-gray-500" />
                      {q.estimated_minutes} min
                    </span>
                    <span className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">
                      <Layers className="h-4 w-4 text-gray-500" />
                      {tl('quest.steps_count').replace('{count}', String(q.steps_count))}
                    </span>
                    <span className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">
                      <Users className="h-4 w-4 text-gray-500" />
                      {q.characters_count} {tl('quest.characters')}
                    </span>
                  </div>

                  {/* Interaction type badges */}
                  <div className="flex flex-wrap gap-2">
                    {(q.interaction_types as string[]).map((type: string) => (
                      <span key={type}
                        className="inline-flex items-center rounded-full bg-primary-100 dark:bg-primary-900/40 px-3 py-1 text-sm font-semibold text-primary-800 dark:text-primary-200 border border-primary-200 dark:border-primary-700"
                      >
                        {tl(`quest.step_${type}`)}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex-shrink-0 self-start sm:self-center">
                  <Button size="md" className="shadow-sm">
                    <Play className="h-5 w-5 mr-2" />
                    {tl('quest.start_quest')}
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
