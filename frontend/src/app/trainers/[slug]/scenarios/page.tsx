"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { getTrainer, getTrainerScenarios, isAuthenticated } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardTitle, CardDescription } from "@/components/ui/Card";
import { ArrowLeft, Clock, BarChart3, AlertCircle, BookOpen } from "lucide-react";

const difficultyColors: Record<string, string> = {
  beginner: "bg-green-100 text-green-700",
  easy: "bg-green-100 text-green-700",
  intermediate: "bg-yellow-100 text-yellow-700",
  medium: "bg-yellow-100 text-yellow-700",
  advanced: "bg-orange-100 text-orange-700",
  hard: "bg-red-100 text-red-700",
  expert: "bg-red-100 text-red-700",
};

const difficultyDefault = "bg-gray-100 text-gray-700";

export default function ScenarioListPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;

  const { data: trainer } = useQuery({
    queryKey: ["trainer", slug],
    queryFn: () => getTrainer(slug),
    enabled: !!slug,
  });

  const {
    data: scenarios,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["trainerScenarios", slug],
    queryFn: () => getTrainerScenarios(slug),
    enabled: !!slug,
  });

  const handleStartScenario = (scenarioId: string) => {
    if (!isAuthenticated()) {
      router.push(`/login?redirect=/trainers/${slug}/scenarios`);
      return;
    }
    router.push(`/scenarios/${scenarioId}`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (isError || !scenarios) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <AlertCircle className="h-12 w-12 text-red-400" />
        <p className="text-lg font-medium text-gray-900">{t("common.error")}</p>
        <p className="text-sm text-gray-500">{(error as Error)?.message}</p>
        <Button variant="outline" onClick={() => refetch()}>
          {t("common.retry")}
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Back Link */}
      {trainer && (
        <Link
          href={`/trainers/${slug}`}
          className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          {t("trainer.backToTrainer")}
        </Link>
      )}

      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          {trainer
            ? (t(`trainer.${trainer.trainer_product_id}`) !== `trainer.${trainer.trainer_product_id}`
              ? t(`trainer.${trainer.trainer_product_id}`)
              : trainer.name)
            : t("trainer.scenarioList")}
        </h1>
        <p className="mt-2 text-gray-500">{t("trainer.scenarioList")}</p>
      </div>

      {scenarios.length === 0 ? (
        <Card padding="lg" className="text-center">
          <BookOpen className="mx-auto h-12 w-12 text-gray-300" />
          <p className="mt-3 text-gray-500">{t("common.comingSoon")}</p>
        </Card>
      ) : (
        <div className="grid gap-4">
          {scenarios.map((scenario) => (
            <Card key={scenario.id} padding="md">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <CardTitle className="text-base">
                    {t(scenario.title_key) !== scenario.title_key
                      ? t(scenario.title_key)
                      : scenario.title_key}
                  </CardTitle>
                  {scenario.goal_key && (
                    <CardDescription className="mt-1 line-clamp-2">
                      {t(scenario.goal_key)}
                    </CardDescription>
                  )}
                  <div className="mt-2 flex flex-wrap items-center gap-3">
                    {/* Difficulty Badge */}
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                        difficultyColors[scenario.difficulty?.toLowerCase()] || difficultyDefault
                      }`}
                    >
                      <BarChart3 className="h-3 w-3" />
                      {t(`trainer.level_${scenario.difficulty}`) !== `trainer.level_${scenario.difficulty}` ? t(`trainer.level_${scenario.difficulty}`) : scenario.difficulty}
                    </span>

                    {/* Duration */}
                    <span className="inline-flex items-center gap-1 text-xs text-gray-500">
                      <Clock className="h-3 w-3" />
                      {scenario.estimated_duration_minutes} {t("trainer.minutes")}
                    </span>

                    {/* Track */}
                    {scenario.track && (
                      <span className="inline-flex items-center rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-700">
                        {scenario.track}
                      </span>
                    )}
                  </div>
                </div>

                <Button
                  size="sm"
                  onClick={() => handleStartScenario(scenario.scenario_id || scenario.id)}
                >
                  {t("trainer.startScenario")}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
