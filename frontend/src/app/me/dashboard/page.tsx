"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getAllProgress } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { AlertCircle, BarChart3, BookOpen, TrendingUp, ArrowRight, Award, CheckCircle, Target } from "lucide-react";

function scoreColor(score: number): string {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-yellow-600";
  return "text-red-600";
}

function scoreBgColor(score: number): string {
  if (score >= 80) return "bg-green-100";
  if (score >= 60) return "bg-yellow-100";
  return "bg-red-100";
}

function readinessBadge(status: string) {
  const styles: Record<string, string> = {
    started: "bg-gray-100 text-gray-600",
    developing: "bg-blue-100 text-blue-700",
    ready: "bg-green-100 text-green-700",
    strong: "bg-purple-100 text-purple-700",
  };
  const label = t(`progress.readiness.${status}` as any) || status;
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
        styles[status] || styles.started
      }`}
    >
      {label}
    </span>
  );
}

export default function DashboardPage() {
  const router = useRouter();

  const {
    data: progressData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["allProgress"],
    queryFn: getAllProgress,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (isError || !progressData) {
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

  const progressList = progressData.progress_list || [];
  const totalCompleted = progressList.reduce((sum, p) => sum + p.completed_scenarios, 0);
  const totalAttempts = progressList.reduce((sum, p) => sum + p.total_attempts, 0);
  const avgScore =
    progressList.length > 0
      ? progressList.reduce((sum, p) => sum + p.average_score, 0) / progressList.length
      : 0;

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{t("progress.title")}</h1>
      </div>

      {/* Summary Cards */}
      <div className="mb-10 grid gap-4 sm:grid-cols-3">
        <Card padding="md" className="text-center">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 text-primary-600">
            <BarChart3 className="h-5 w-5" />
          </div>
          <p className="mt-3 text-2xl font-bold text-gray-900">
            {progressList.length > 0 ? `${Math.round(avgScore)}%` : "---"}
          </p>
          <p className="text-sm text-gray-500">{t("progress.averageScore")}</p>
        </Card>

        <Card padding="md" className="text-center">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-lg bg-green-100 text-green-600">
            <CheckCircle className="h-5 w-5" />
          </div>
          <p className="mt-3 text-2xl font-bold text-gray-900">{totalCompleted}</p>
          <p className="text-sm text-gray-500">{t("progress.completedScenarios")}</p>
        </Card>

        <Card padding="md" className="text-center">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100 text-purple-600">
            <Target className="h-5 w-5" />
          </div>
          <p className="mt-3 text-2xl font-bold text-gray-900">{totalAttempts}</p>
          <p className="text-sm text-gray-500">{t("progress.totalAttempts")}</p>
        </Card>
      </div>

      {/* Per-trainer Progress */}
      {progressList.length > 0 ? (
        <div>
          <h2 className="mb-4 text-xl font-semibold text-gray-900">
            {t("progress.trainerProgress")}
          </h2>
          <div className="space-y-4">
            {progressList.map((progress) => {
              const maxSkill = progress.skill_scores?.length
                ? progress.skill_scores.reduce((max, s) => (s.score > max.score ? s : max))
                : null;

              return (
                <Link key={progress.trainer_slug} href={`/me/progress/${progress.trainer_slug}`}>
                  <Card hover padding="md">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3">
                          <CardTitle className="text-base">{progress.trainer_name}</CardTitle>
                          {readinessBadge(progress.readiness_status)}
                        </div>
                        <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-gray-500">
                          <span className="flex items-center gap-1">
                            <BarChart3 className="h-4 w-4" />
                            {t("progress.averageScore")}:{" "}
                            <span className={`font-medium ${scoreColor(progress.average_score)}`}>
                              {Math.round(progress.average_score)}%
                            </span>
                          </span>
                          <span className="flex items-center gap-1">
                            <BookOpen className="h-4 w-4" />
                            {progress.completed_scenarios} {t("progress.completedScenarios").toLowerCase()}
                          </span>
                        </div>
                        {maxSkill && (
                          <div className="mt-1 flex items-center gap-1 text-xs text-gray-400">
                            <Award className="h-3 w-3" />
                            {t("progress.skillScores")}: {maxSkill.skill_name} ({Math.round(maxSkill.score)}%)
                          </div>
                        )}
                      </div>
                      <ArrowRight className="h-5 w-5 text-gray-300 flex-shrink-0" />
                    </div>
                  </Card>
                </Link>
              );
            })}
          </div>
        </div>
      ) : (
        <Card padding="lg" className="text-center">
          <BookOpen className="mx-auto h-12 w-12 text-gray-300" />
          <p className="mt-3 text-gray-500">{t("progress.noProgress")}</p>
          <div className="mt-4">
            <Button onClick={() => router.push("/domains")}>
              {t("nav.domains")}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </Card>
      )}

      {/* Link to detailed progress */}
      {progressList.length > 0 && (
        <div className="mt-6 text-center">
          <Link
            href="/me/progress"
            className="inline-flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-500"
          >
            {t("progress.title")}
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      )}
    </div>
  );
}
