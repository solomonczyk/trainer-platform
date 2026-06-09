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

  const quests = data?.quests
    ? Object.values(data.quests).filter((q: any) => q.trainer_slug === slug)
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

      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100">
          {tl('quest.quest_catalog')}
        </h1>
        <p className="mt-2 text-gray-500 dark:text-gray-400">
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
        <div className="space-y-4">
          {quests.map((q: any) => (
            <Card key={q.quest_id} padding="lg" className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => router.push(`/trainers/${slug}/quests/${q.quest_id}`)}
            >
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                <div className="flex-1">
                  <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-1">
                    {tl(q.title_key) !== q.title_key ? tl(q.title_key) : q.title_key}
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">
                    {tl(q.summary_key) !== q.summary_key ? tl(q.summary_key) : q.summary_key}
                  </p>

                  <div className="flex flex-wrap gap-3">
                    <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                      <Clock className="h-3.5 w-3.5" />
                      {q.estimated_minutes} min
                    </span>
                    <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                      <Layers className="h-3.5 w-3.5" />
                      {tl('quest.steps_count').replace('{count}', String(q.steps_count))}
                    </span>
                    <span className="inline-flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                      <Users className="h-3.5 w-3.5" />
                      {q.characters_count} {tl('quest.characters')}
                    </span>
                  </div>

                  {/* Interaction type badges */}
                  <div className="flex flex-wrap gap-1 mt-2">
                    {(q.interaction_types as string[]).map((type: string) => (
                      <span key={type}
                        className="inline-flex items-center rounded-full bg-primary-50 dark:bg-primary-900/20 px-2 py-0.5 text-[10px] font-medium text-primary-700 dark:text-primary-300"
                      >
                        {tl(`quest.step_${type}`)}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex-shrink-0">
                  <Button size="sm">
                    <Play className="h-4 w-4 mr-1" />
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
