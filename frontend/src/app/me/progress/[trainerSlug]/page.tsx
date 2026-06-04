"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { getTrainerProgress } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import {
  AlertCircle,
  ArrowLeft,
  BarChart3,
  BookOpen,
  CheckCircle,
  Award,
  TrendingUp,
  Target,
  Clock,
  GraduationCap,
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

function SkillProgressBar({ name, score, level, attempts }: {
  name: string;
  score: number;
  level: string;
  attempts: number;
}) {
  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-800">{name}</span>
          {level && (
            <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-500">
              {level}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">{attempts} attempts</span>
          <span className={`text-sm font-bold ${scoreColor(score)}`}>
            {Math.round(score)}%
          </span>
        </div>
      </div>
      <div className="h-2.5 w-full rounded-full bg-gray-100">
        <div
          className={`h-2.5 rounded-full transition-all ${scoreBgColor(score)}`}
          style={{ width: `${Math.min(score, 100)}%` }}
        />
      </div>
    </div>
  );
}

export default function TrainerProgressPage() {
  const params = useParams();
  const router = useRouter();
  const trainerSlug = params?.trainerSlug as string;

  const {
    data: progress,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["trainerProgress", trainerSlug],
    queryFn: () => getTrainerProgress(trainerSlug),
    enabled: !!trainerSlug,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (isError || !progress) {
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

  const readinessLabel = t(`progress.readiness.${progress.readiness_status}` as any) || progress.readiness_status;

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Back Link */}
      <Link
        href="/me/progress"
        className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        {t("progress.title")}
      </Link>

      {/* Trainer Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary-100 text-primary-600">
            <GraduationCap className="h-7 w-7" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{progress.trainer_name}</h1>
            <p className="mt-1 flex items-center gap-2 text-gray-500">
              <span className="text-sm">{readinessLabel}</span>
            </p>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="mb-8 grid gap-4 sm:grid-cols-3">
        <Card padding="md" className="text-center">
          <p className={`text-3xl font-bold ${scoreColor(progress.average_score)}`}>
            {Math.round(progress.average_score)}%
          </p>
          <p className="mt-1 text-sm text-gray-500">{t("progress.averageScore")}</p>
        </Card>

        <Card padding="md" className="text-center">
          <p className="text-3xl font-bold text-gray-900">
            {progress.completed_scenarios}
          </p>
          <p className="mt-1 text-sm text-gray-500">{t("progress.completedScenarios")}</p>
        </Card>

        <Card padding="md" className="text-center">
          <p className="text-3xl font-bold text-gray-900">
            {progress.total_attempts}
          </p>
          <p className="mt-1 text-sm text-gray-500">{t("progress.totalAttempts")}</p>
        </Card>
      </div>

      {/* Readiness Status */}
      <Card padding="md" className="mb-8">
        <CardHeader>
          <Target className="h-5 w-5 text-gray-400" />
          <CardTitle className="text-sm font-medium text-gray-700">
            Readiness Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${
                {
                  started: "bg-gray-100 text-gray-600",
                  developing: "bg-blue-100 text-blue-700",
                  ready: "bg-green-100 text-green-700",
                  strong: "bg-purple-100 text-purple-700",
                }[progress.readiness_status] || "bg-gray-100 text-gray-600"
              }`}
            >
              {readinessLabel}
            </span>
            <span className="text-sm text-gray-400">
              ({progress.completed_scenarios} {t("progress.completedScenarios").toLowerCase()})
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Skill Scores */}
      {progress.skill_scores && progress.skill_scores.length > 0 ? (
        <Card padding="lg">
          <CardHeader>
            <Award className="h-5 w-5 text-gray-400" />
            <CardTitle className="text-base text-gray-900">
              {t("progress.skillScores")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {progress.skill_scores.map((skill) => (
              <SkillProgressBar
                key={skill.skill_id}
                name={skill.skill_name}
                score={skill.score}
                level={skill.level}
                attempts={skill.attempts_count}
              />
            ))}
          </CardContent>
        </Card>
      ) : (
        <Card padding="md">
          <p className="text-sm text-gray-400">{t("progress.noSkillData")}</p>
        </Card>
      )}

      {/* Actions */}
      <div className="mt-8 flex flex-wrap gap-3">
        <Button
          variant="outline"
          onClick={() => router.push(`/trainers/${trainerSlug}/scenarios`)}
        >
          <BookOpen className="mr-2 h-4 w-4" />
          {t("trainer.scenarios")}
        </Button>
      </div>
    </div>
  );
}
