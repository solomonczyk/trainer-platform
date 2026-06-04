"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getAllProgress } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import {
  AlertCircle,
  BarChart3,
  BookOpen,
  CheckCircle,
  ArrowRight,
  Award,
  TrendingUp,
  Target,
} from "lucide-react";

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

const levelOrder: Record<string, number> = {
  beginner: 1,
  intermediate: 2,
  advanced: 3,
  expert: 4,
};

function SkillBar({ name, score, level }: { name: string; score: number; level: string }) {
  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-medium text-gray-700">{name}</span>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-medium ${scoreColor(score)}`}>
            {Math.round(score)}%
          </span>
          {level && (
            <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-500">
              {level}
            </span>
          )}
        </div>
      </div>
      <div className="h-2 w-full rounded-full bg-gray-100">
        <div
          className={`h-2 rounded-full transition-all ${scoreBgColor(score)}`}
          style={{ width: `${Math.min(score, 100)}%` }}
        />
      </div>
    </div>
  );
}

export default function DetailedProgressPage() {
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

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Page Header */}
      <div className="mb-8">
        <Link
          href="/me/dashboard"
          className="mb-4 inline-flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ArrowRight className="h-4 w-4 rotate-180" />
          {t("progress.title")}
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">{t("progress.title")}</h1>
        <p className="mt-2 text-gray-500">
          {totalCompleted} {t("progress.completedScenarios").toLowerCase()},{ " "}
          {totalAttempts} {t("progress.totalAttempts").toLowerCase()}
        </p>
      </div>

      {/* Per-trainer Detailed Cards */}
      {progressList.length > 0 ? (
        <div className="space-y-6">
          {progressList.map((progress) => (
            <Card key={progress.trainer_slug} padding="lg">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-5">
                <div>
                  <div className="flex items-center gap-3">
                    <CardTitle className="text-lg">{progress.trainer_name}</CardTitle>
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        {
                          started: "bg-gray-100 text-gray-600",
                          developing: "bg-blue-100 text-blue-700",
                          ready: "bg-green-100 text-green-700",
                          strong: "bg-purple-100 text-purple-700",
                        }[progress.readiness_status] || "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {t(`progress.readiness.${progress.readiness_status}` as any) || progress.readiness_status}
                    </span>
                  </div>
                </div>
                <Link href={`/me/progress/${progress.trainer_slug}`}>
                  <Button variant="outline" size="sm">
                    {t("common.next")}
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </Button>
                </Link>
              </div>

              {/* Stats row */}
              <div className="mb-5 grid grid-cols-3 gap-4">
                <div className="rounded-lg bg-gray-50 p-3 text-center">
                  <p className={`text-lg font-bold ${scoreColor(progress.average_score)}`}>
                    {Math.round(progress.average_score)}%
                  </p>
                  <p className="text-xs text-gray-500">{t("progress.averageScore")}</p>
                </div>
                <div className="rounded-lg bg-gray-50 p-3 text-center">
                  <p className="text-lg font-bold text-gray-900">{progress.completed_scenarios}</p>
                  <p className="text-xs text-gray-500">{t("progress.completedScenarios")}</p>
                </div>
                <div className="rounded-lg bg-gray-50 p-3 text-center">
                  <p className="text-lg font-bold text-gray-900">{progress.total_attempts}</p>
                  <p className="text-xs text-gray-500">{t("progress.totalAttempts")}</p>
                </div>
              </div>

              {/* Skill Scores */}
              {progress.skill_scores && progress.skill_scores.length > 0 ? (
                <div>
                  <h3 className="mb-3 text-sm font-semibold text-gray-700">
                    {t("progress.skillScores")}
                  </h3>
                  {progress.skill_scores.map((skill) => (
                    <SkillBar
                      key={skill.skill_id}
                      name={skill.skill_name}
                      score={skill.score}
                      level={skill.level}
                    />
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400">{t("progress.noSkillData")}</p>
              )}
            </Card>
          ))}
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
    </div>
  );
}
