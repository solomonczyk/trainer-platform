"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { getTrainer, getTrainerScenarios, sendAnalyticsEvent } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import {
  ArrowLeft,
  Clock,
  BarChart3,
  AlertCircle,
  BookOpen,
  FileText,
  Lightbulb,
  Target,
  Users,
} from "lucide-react";

const SCENARIO_IDS = [
  "ba_phase2_stakeholder_requirements",
  "ba_phase2_process_analysis",
  "ba_phase2_documentation_artifacts",
  "ba_phase2_conflict_resolution",
  "ba_phase2_traceability_impact",
  "ba_phase2_real_case_analysis",
];

const SCENARIO_META: Record<string, { icon: React.ReactNode; color: string }> = {
  ba_phase2_stakeholder_requirements: { icon: <Users className="h-5 w-5" />, color: "bg-blue-100 text-blue-600" },
  ba_phase2_process_analysis: { icon: <Target className="h-5 w-5" />, color: "bg-green-100 text-green-600" },
  ba_phase2_documentation_artifacts: { icon: <FileText className="h-5 w-5" />, color: "bg-purple-100 text-purple-600" },
  ba_phase2_conflict_resolution: { icon: <Lightbulb className="h-5 w-5" />, color: "bg-amber-100 text-amber-600" },
  ba_phase2_traceability_impact: { icon: <BarChart3 className="h-5 w-5" />, color: "bg-rose-100 text-rose-600" },
  ba_phase2_real_case_analysis: { icon: <BookOpen className="h-5 w-5" />, color: "bg-teal-100 text-teal-600" },
};

export default function Phase2ScenarioListPage() {
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

  const handleOpenScenario = (scenarioId: string) => {
    sendAnalyticsEvent("ba_phase2_scenario_opened", {
      trainer_slug: slug,
      scenario_id: scenarioId,
    });
    router.push(`/trainers/${slug}/phase2/${scenarioId}`);
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

  // Filter to Phase 2 scenarios
  const phase2Scenarios = (scenarios || []).filter(
    (s) => s.scenario_id && SCENARIO_IDS.includes(s.scenario_id)
  );

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Back Link */}
      {trainer && (
        <button
          onClick={() => router.push(`/trainers/${slug}`)}
          className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          {t("trainer.backToTrainer")}
        </button>
      )}

      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          {t("ba_phase2.title")}
        </h1>
        <p className="mt-2 text-gray-500">
          {t("ba_phase2.description")}
        </p>
        <div className="mt-3 inline-flex items-center gap-1.5 rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
          <BarChart3 className="h-3.5 w-3.5" />
          {t("ba_phase2.phase_2_badge")}
        </div>
      </div>

      {phase2Scenarios.length === 0 ? (
        <Card padding="lg" className="text-center">
          <BookOpen className="mx-auto h-12 w-12 text-gray-300" />
          <p className="mt-3 text-gray-500">{t("common.comingSoon")}</p>
        </Card>
      ) : (
        <div className="grid gap-4">
          {phase2Scenarios.map((scenario) => {
            const meta = SCENARIO_META[scenario.scenario_id] || {
              icon: <FileText className="h-5 w-5" />,
              color: "bg-gray-100 text-gray-600",
            };

            return (
              <Card key={scenario.id || scenario.scenario_id} padding="md">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="flex items-start gap-4 flex-1 min-w-0">
                    <div
                      className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${meta.color}`}
                    >
                      {meta.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-base">
                        {t(scenario.title_key) !== scenario.title_key
                          ? t(scenario.title_key)
                          : scenario.title_key}
                      </CardTitle>
                      {scenario.goal_key && (
                        <CardDescription className="mt-1 line-clamp-2">
                          {scenario.goal_key}
                        </CardDescription>
                      )}
                      <div className="mt-2 flex flex-wrap items-center gap-3">
                        <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                          <BarChart3 className="h-3 w-3" />
                          {scenario.difficulty || "intermediate"}
                        </span>
                        <span className="inline-flex items-center gap-1 text-xs text-gray-500">
                          <Clock className="h-3 w-3" />
                          {scenario.estimated_duration_minutes || 30}{" "}
                          {t("trainer.minutes")}
                        </span>
                      </div>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => handleOpenScenario(scenario.scenario_id)}
                  >
                    {t("ba_phase2.start")}
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Info Box */}
      <Card padding="md" className="mt-8 bg-amber-50 border-amber-200">
        <div className="flex items-start gap-3">
          <Lightbulb className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-800">
              {t("ba_phase2.how_it_works_title")}
            </p>
            <p className="mt-1 text-sm text-amber-700">
              {t("ba_phase2.how_it_works_desc")}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
